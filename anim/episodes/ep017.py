"""ep017 — Mini-historia: "The Manhole That Hiccuped" (story-020, idea b20261123-2-i01). Plaza urbana (env_real.build_plaza). Rótulo fijo arriba:
"POV: the manhole has hiccups". La tapa de alcantarilla (a ras del suelo) da HIPO: cada hipo es un saltito seco (sube 0,3 s y cae con CLONK) con un
puff breve de vapor y el sonido "hic"; entre hipos queda quieta ~0,5 s (ritmo regular hic... hic...).
  1-60    gancho/hipo 1: la tapa en lo alto de su salto sobre el puff, el hombre agachado; cae (clonk). Hic: escupe una BOTA; él salta atrás.
  48-100  hipo 2: escupe un PATITO; vuelve de un salto y lo caza (squeak); hipo 3 normal; lo deja en el suelo.
  100-177 SUSTO: se aleja agachado (Sneaking), vuelve cargando (Charge) y salta ante la tapa con los brazos arriba, de cara a ella; la tapa, a mitad
          de un hipo, se queda CONGELADA temblando 0,6 s y cae plana, en silencio.
  177-236 REMATE en primer plano: alivio (asiente), pausa, y el HIC se le pasa a él: saltito seco y puff de vapor por la boca, mano a la boca; la
          tapa detrás hace un saltito y cae con clonk (se ríe).
  236-294 general: hic de la tapa, él agachado como en el fotograma 1 (bucle; la bota desaparece en el corte a general y el patito en el corte a plano medio).
Convenio: yaw 0 mira a cámara (-y), 90 mira a +x; mira hacia (sin yaw, -cos yaw). 24 fps, 294 fotogramas = 12,3 s."""
import math
import bpy
from mathutils import Vector
from mixamo import MixamoActor
from klunk_toon import apply as klunk, expression, blink
import env_real

TITLE = "The Manhole That Hiccuped"
CAPTION = "POV: the manhole has hiccups"
SPEED = 1.0
ENV = "mesa"                      # base mínima del kit; build_plaza la vacía y monta la plaza
CUSTOM_CAMERA = True

FPS = 24
F_END = 294
M = Vector((-0.55, 0.0, 0.0))     # centro de la tapa
P1 = Vector((0.40, -0.45, 0.0))   # casa del hombre: delante a la derecha de la tapa (inicio, susto y final)
P2 = Vector((0.95, 0.65, 0.0))    # tras el salto atrás
HID = Vector((1.0, 1.3, 0.0))   # donde se aleja agachado antes del susto
YAW = -50.0
YAW_BOO = -75.0                   # cara a la tapa (de perfil a cámara) durante el susto
YAW_REM = 37.0                    # remate: de frente a la cámara del primer plano (la tapa queda detrás, a un lado)
LR = 0.66                         # radio de la tapa
LID_Z0 = 0.03                     # centro de la tapa asentada (plana en su aro)
HOP = 0.85                        # altura del salto de un hipo
TILT = 25.0                       # grados en x: la cara superior mira a la cámara en lo alto del salto

# hipos de la tapa: (inicio, subida, fotograma hasta el que se mantiene arriba, caída, altura). Entre hipos queda quieta >= 12 fotogramas.
HICS = [(-5, 7, 2, 6, HOP),                 # gancho: ya en el aire en el fotograma 1
        (22, 7, 29, 6, HOP), (48, 7, 55, 6, HOP), (74, 7, 81, 6, HOP), (100, 7, 107, 6, HOP),
        (150, 7, 171, 6, HOP),              # susto: sube, se CONGELA temblando (157-171) y cae plana en silencio
        (222, 6, 228, 5, 0.85),             # remate: saltito de risa tras el hic de él
        (286, 7, 10 ** 5, 1, HOP)]          # final: sube y queda (fotograma 1)
LAND = [8, 35, 61, 87, 113, 233]            # aterrizajes con clonk (el del susto, 177, es silencioso)
F_FREEZE0, F_FREEZE1 = 157, 171
F_BOOT, T_BOOT = 25, 22           # lanzamiento de la bota y vuelo
F_DUCK, T_DUCK = 51, 22
F_CATCH = F_DUCK + T_DUCK
F_HOP1, F_HOP2 = 26, 50           # inicio de los clips Jumping (despegue +5, aterrizaje +23)
F_REL = 96                        # suelta el patito en el suelo
G_DUCK = Vector((0.6, -0.95, 0.2))
F_SNEAK0, F_CHARGE0, F_BOO = 100, 136, 150
F_HIC_MAN = 212
F_CUT_WIDE = 236


def R(d): return math.radians(d)
def sstep(t): t = max(0.0, min(1.0, t)); return t * t * (3 - 2 * t)
def lerp(a, b, t): return a + (b - a) * t


# ------------------------------------------------------------------ estado de la tapa
def lid_v(f):
    """Altura sobre el aro (m) de la tapa en el fotograma f."""
    v = 0.0
    for (t0, tu, th, td, ap) in HICS:
        if t0 <= f < t0 + tu: v = max(v, ap * (1 - (1 - (f - t0) / float(tu)) ** 2))
        elif t0 + tu <= f < th: v = max(v, ap)
        elif th <= f < th + td: v = max(v, ap * (1 - ((f - th) / float(td)) ** 2))
    return v


def lid_pose(f):
    v = lid_v(f); k = min(1.0, v / HOP)
    z = LID_Z0 + v; rx = TILT * k; ry = 0.0; rz = 18.0 * k
    if F_FREEZE0 <= f <= F_FREEZE1:                       # congelada: solo tiembla (sacudida rápida y pequeña)
        rx += 3.5 * math.sin(2.3 * f); ry += 4.0 * math.cos(2.9 * f); z += 0.012 * math.sin(3.1 * f)
    for l in LAND + [177]:
        if l <= f < l + 8:
            u = (f - l) / 8.0; rx += 4 * math.sin(u * 13) * (1 - u); ry += 3 * math.cos(u * 10) * (1 - u)
    return (M.x, M.y, z), (R(rx), R(ry), R(rz))




# ------------------------------------------------------------------ materiales y utilidades
def mmat(S, name, rgb, rough=0.5, metal=0.0):
    k = "m_" + name
    if k in S.mats: return S.mats[k]
    m = bpy.data.materials.new(k); m.use_nodes = True
    b = m.node_tree.nodes["Principled BSDF"]
    b.inputs["Base Color"].default_value = (*rgb, 1); b.inputs["Roughness"].default_value = rough; b.inputs["Metallic"].default_value = metal
    S.mats[k] = m
    return m


def O(S, prim, name, mat, loc=(0, 0, 0), scale=(1, 1, 1), rot=(0, 0, 0), parent=None, **kw):
    o = S.obj(prim, name, "white", loc, scale, rot, parent, True, **kw); o.data.materials[0] = mat; return o


def steam_mat(S, name, vertical=True, strength=1.0, scroll=True):
    """Vapor: Mix(Transparent, Emission) con alfa = ruido * degradado vertical * borde suave."""
    k = "steam_" + name
    if k in S.mats: return S.mats[k]
    m = bpy.data.materials.new(k); m.use_nodes = True; nt = m.node_tree; N, L = nt.nodes, nt.links
    for n in list(N): N.remove(n)
    out = N.new("ShaderNodeOutputMaterial"); mix = N.new("ShaderNodeMixShader"); tr = N.new("ShaderNodeBsdfTransparent"); em = N.new("ShaderNodeEmission")
    em.inputs["Color"].default_value = (0.93, 0.96, 1.0, 1); em.inputs["Strength"].default_value = 1.25 if name == "boca" else 1.4
    tc = N.new("ShaderNodeTexCoord"); mp = N.new("ShaderNodeMapping"); mp.inputs["Scale"].default_value = (3.2, 3.2, 2.0)
    nz = N.new("ShaderNodeTexNoise"); nz.inputs["Scale"].default_value = 1.6; nz.inputs["Detail"].default_value = 6.0; nz.inputs["Roughness"].default_value = 0.6
    rp = N.new("ShaderNodeValToRGB"); rp.color_ramp.elements[0].position = 0.30; rp.color_ramp.elements[1].position = 0.72
    sep = N.new("ShaderNodeSeparateXYZ"); fade = N.new("ShaderNodeMapRange"); fade.inputs["From Min"].default_value = 0.45; fade.inputs["From Max"].default_value = 1.0
    fade.inputs["To Min"].default_value = 1.0; fade.inputs["To Max"].default_value = 0.0; fade.clamp = True
    lw = N.new("ShaderNodeLayerWeight"); lw.inputs["Blend"].default_value = 0.5
    inv = N.new("ShaderNodeMath"); inv.operation = "SUBTRACT"; inv.inputs[0].default_value = 1.0
    m1 = N.new("ShaderNodeMath"); m1.operation = "MULTIPLY"; m2 = N.new("ShaderNodeMath"); m2.operation = "MULTIPLY"; m3 = N.new("ShaderNodeMath"); m3.operation = "MULTIPLY"
    m3.inputs[1].default_value = 0.85 * strength
    L.new(tc.outputs["Generated"], mp.inputs["Vector"]); L.new(mp.outputs["Vector"], nz.inputs["Vector"]); L.new(nz.outputs["Fac"], rp.inputs["Fac"])
    L.new(lw.outputs["Facing"], inv.inputs[1]); L.new(rp.outputs["Color"], m1.inputs[0]); L.new(inv.outputs[0], m1.inputs[1])
    if vertical:
        L.new(tc.outputs["Generated"], sep.inputs[0]); L.new(sep.outputs["Z"], fade.inputs["Value"]); L.new(m1.outputs[0], m2.inputs[0]); L.new(fade.outputs[0], m2.inputs[1])
        L.new(m2.outputs[0], m3.inputs[0])
    else:
        L.new(m1.outputs[0], m3.inputs[0])
    L.new(m3.outputs[0], mix.inputs["Fac"]); L.new(tr.outputs[0], mix.inputs[1]); L.new(em.outputs[0], mix.inputs[2]); L.new(mix.outputs[0], out.inputs["Surface"])
    if name == "boca":                                    # nube opaca y blanca (el hic del hombre)
        for l in list(mix.inputs["Fac"].links): L.remove(l)
        mix.inputs["Fac"].default_value = 1.0; em.inputs["Strength"].default_value = 3.0
    S.mats[k] = m; S._steam_map = getattr(S, "_steam_map", []) + [mp]
    return m


# ------------------------------------------------------------------ objetos del gag
def build_manhole(S):
    """Boca de alcantarilla A RAS DEL SUELO: aro de fundición claro enrasado, anillo oscuro hundido y agujero negro. La tapa reposa plana dentro."""
    frame_m = mmat(S, "marco", (0.36, 0.35, 0.33), 0.8, 0.3); hole_m = mmat(S, "boca", (0.003, 0.003, 0.004), 0.95)
    iron = mmat(S, "hierro", (0.11, 0.10, 0.095), 0.5, 0.85); steel = mmat(S, "acero", (0.55, 0.53, 0.50), 0.3, 0.95)
    paint = mmat(S, "pintura_tapa", (0.95, 0.72, 0.05), 0.5)
    O(S, "cylinder", "marco", frame_m, (M.x, M.y, 0.004), (0.84, 0.84, 0.004), vertices=64)
    O(S, "cylinder", "anillo", iron, (M.x, M.y, 0.0075), (0.74, 0.74, 0.003), vertices=64)
    O(S, "cylinder", "boca", hole_m, (M.x, M.y, 0.0105), (0.71, 0.71, 0.001), vertices=64)
    lid = S.empty("tapa", (M.x, M.y, LID_Z0))
    O(S, "cylinder", "disco", iron, (0, 0, 0), (LR, LR, 0.02), parent=lid, vertices=64)
    O(S, "cylinder", "canto", steel, (0, 0, 0), (LR + 0.01, LR + 0.01, 0.014), parent=lid, vertices=64)
    for sg in (1, -1):                                    # el mismo dibujo en las dos caras (la cámara ve la inferior cuando está en el aire)
        zf = sg * 0.024
        for rr, mm in ((LR - 0.06, steel), (0.46, iron), (0.28, steel)):
            O(S, "torus", "aro", mm, (0, 0, zf), (1, 1, 1), parent=lid, major_radius=rr, minor_radius=0.018, major_segments=48, minor_segments=8)
        for i in range(12):
            a = R(i * 30.0 + 15.0)
            O(S, "cube", "nervio", steel, (0.37 * math.cos(a), 0.37 * math.sin(a), zf), (0.17, 0.02, 0.011), (0, 0, a), parent=lid)
        O(S, "cylinder", "cubo", paint, (0, 0, zf), (0.13, 0.13, 0.011), parent=lid, vertices=32)
    return lid




def build_steam(S):
    """Solo PUFFS breves de vapor (sin columna continua): esferas con el material de vapor que se hinchan y se disipan."""
    pm = steam_mat(S, "puff", False, 1.0)
    return [O(S, "uv_sphere", "puff", pm, (M.x, M.y, 0.2), (0.001,) * 3, segments=16, ring_count=8) for _ in range(44)]


def build_boot(S):
    e = S.empty("bota", (0, 0, -5))
    yel = mmat(S, "bota_roja", (0.82, 0.07, 0.06), 0.3); blk = mmat(S, "suela", (0.03, 0.03, 0.03), 0.8); wht = mmat(S, "puño", (0.9, 0.9, 0.85), 0.6)
    O(S, "cylinder", "caña", yel, (0, 0, 0.14), (0.10, 0.10, 0.17), parent=e, vertices=24)
    O(S, "cylinder", "puño", wht, (0, 0, 0.30), (0.108, 0.108, 0.02), parent=e, vertices=24)
    O(S, "uv_sphere", "pie", yel, (0, 0.13, -0.03), (0.10, 0.27, 0.09), parent=e, segments=20, ring_count=10)
    O(S, "uv_sphere", "suela", blk, (0, 0.13, -0.105), (0.106, 0.28, 0.03), parent=e, segments=20, ring_count=8)
    e.scale = (1.6, 1.6, 1.6)
    return e


def build_duck(S):
    e = S.empty("patito", (0, 0, -5))
    yel = mmat(S, "pato", (1.0, 0.84, 0.05), 0.4); org = mmat(S, "pico_pato", (1.0, 0.38, 0.03), 0.5); blk = mmat(S, "ojo_pato", (0.01, 0.01, 0.01), 0.2)
    O(S, "uv_sphere", "cuerpo", yel, (0, 0, 0), (0.15, 0.19, 0.13), parent=e, segments=24, ring_count=12)
    O(S, "uv_sphere", "cabeza", yel, (0, 0.12, 0.15), (0.095, 0.095, 0.095), parent=e, segments=20, ring_count=10)
    O(S, "uv_sphere", "pico", org, (0, 0.215, 0.135), (0.055, 0.075, 0.022), parent=e, segments=14, ring_count=8)
    for sx in (-1, 1): O(S, "uv_sphere", "ojo", blk, (sx * 0.05, 0.18, 0.18), (0.016, 0.016, 0.016), parent=e, segments=8, ring_count=6)
    O(S, "uv_sphere", "cola", yel, (0, -0.19, 0.07), (0.05, 0.07, 0.05), (math.radians(30), 0, 0), parent=e, segments=12, ring_count=8)
    e.scale = (1.5, 1.5, 1.5)
    return e


def parab(p0, p1, apex_h, u):
    """Arco de p0 a p1 con altura extra apex_h en la mitad (u en 0..1)."""
    return Vector((lerp(p0.x, p1.x, u), lerp(p0.y, p1.y, u), lerp(p0.z, p1.z, u) + 4 * apex_h * u * (1 - u)))


# ------------------------------------------------------------------ cámara
CAM_W = ((-0.3, -7.4, 1.2), (-0.3, 0.0, 1.2), 50, 7.9)       # encuadre del fotograma 1 (se repite al final)


def cam_set(S, f, loc, tgt, lens, focus):
    S.cam.location = loc; S.cam.keyframe_insert("location", frame=f)
    S.cam.data.lens = lens; S.cam.data.keyframe_insert("lens", frame=f)
    S.cam.data.dof.focus_distance = focus; S.cam.data.dof.keyframe_insert("focus_distance", frame=f)
    S.tgt.location = tgt; S.tgt.keyframe_insert("location", frame=f)


def seg(S, a, clip, f0, f1, start=0, speed=1.0, blend=4, repeat=1):
    S.f = f0
    cl = a.clips[clip]; avail = int((cl.frame_range[1] - cl.frame_range[0] - start) / speed)
    a.play(clip, frames=min(avail * repeat, f1 - f0 + blend), speed=speed, blend=blend, start=max(0, start), repeat=repeat)


def hand_mid(S, a, f):
    S.sc.frame_set(f); bpy.context.view_layer.update()
    mw, pb = a.arm.matrix_world, a.arm.pose.bones
    l = mw @ pb[a.pfx + "LeftHand"].head; r = mw @ pb[a.pfx + "RightHand"].head
    return (l + r) / 2


# ------------------------------------------------------------------ la historia


# ------------------------------------------------------------------ la historia
def l1(S):
    props = env_real.build_plaza(S, rot_deg=20)
    lid = build_manhole(S); puffs = build_steam(S); boot = build_boot(S); duck = build_duck(S)
    a = MixamoActor(S, x=P1.x, yaw=YAW, use=["Looking Around", "Sneaking Forward", "Surprised", "Jumping", "Picking Up", "Victory", "Head Nod Yes", "Charge"]); klunk(a)

    # ---- hombre: clips ----
    SNEAK = 8                                            # fotograma del clip Sneaking Forward = pose de agachado del plano 1
    seg(S, a, "Sneaking Forward", 1, 20, start=SNEAK, speed=0.35, blend=0)
    seg(S, a, "Surprised", 18, 26, start=14, speed=1.6, blend=3)                       # hic 1: respingo
    seg(S, a, "Jumping", F_HOP1, F_HOP1 + 24, start=14, blend=3)                       # salto atrás
    seg(S, a, "Jumping", F_HOP2, F_HOP2 + 22, start=14, blend=2)                       # vuelve de un salto
    seg(S, a, "Picking Up", F_CATCH - 8, 84, start=118, speed=0.5, blend=4)            # brazos al frente: caza el patito
    seg(S, a, "Picking Up", 84, F_SNEAK0, start=24, speed=1.4, blend=5)                # se agacha y lo deja en el suelo
    seg(S, a, "Sneaking Forward", F_SNEAK0, F_CHARGE0, start=0, speed=0.9, blend=6)    # se aleja agachado
    seg(S, a, "Charge", F_CHARGE0, F_BOO, start=0, speed=1.5, blend=4)                 # vuelve cargando
    seg(S, a, "Victory", F_BOO, 178, start=18, speed=1.0, blend=3)                     # susto: brazos arriba
    seg(S, a, "Head Nod Yes", 178, F_HIC_MAN + 3, start=0, speed=1.2, blend=4)         # alivio: asiente
    seg(S, a, "Surprised", F_HIC_MAN + 3, 232, start=14, speed=1.3, blend=3)           # hic propio: mano a la boca
    seg(S, a, "Sneaking Forward", 232, F_END, start=SNEAK - 4, speed=0.35, blend=8)    # vuelve a agacharse: pose del plano 1

    # ---- hombre: posición y orientación ----
    def pos(f):
        if f <= F_HOP1 + 5: return P1
        if f <= F_HOP1 + 23: return P1.lerp(P2, sstep((f - F_HOP1 - 5) / 18.0))
        if f <= F_HOP2 + 5: return P2
        if f <= F_HOP2 + 23: return P2.lerp(P1, sstep((f - F_HOP2 - 5) / 18.0))
        if f <= F_SNEAK0: return P1
        if f <= F_CHARGE0: return P1.lerp(HID, (f - F_SNEAK0) / float(F_CHARGE0 - F_SNEAK0))
        if f <= F_BOO: return HID.lerp(P1, sstep((f - F_CHARGE0) / float(F_BOO - F_CHARGE0)))
        return P1
    def yaw(f):
        if f < F_SNEAK0 - 2: return YAW
        if f < F_SNEAK0 + 4: return lerp(YAW, 125.0, (f - F_SNEAK0 + 2) / 6.0)
        if f < F_CHARGE0 - 4: return 125.0
        if f < F_CHARGE0: return lerp(125.0, -37.0, (f - F_CHARGE0 + 4) / 4.0)
        if f < F_BOO: return -37.0
        if f < F_BOO + 6: return lerp(-37.0, YAW_BOO, (f - F_BOO) / 6.0)
        if f < 176: return YAW_BOO
        if f < 182: return lerp(YAW_BOO, YAW_REM, (f - 176) / 6.0)
        if f < 232: return YAW_REM
        if f < 240: return lerp(YAW_REM, YAW, (f - 232) / 8.0)
        return YAW
    hic_bump = lambda f: 0.42 * math.sin(math.pi * (f - F_HIC_MAN) / 8.0) if F_HIC_MAN <= f <= F_HIC_MAN + 8 else 0.0
    bpy.context.preferences.edit.keyframe_new_interpolation_type = "LINEAR"
    for f in range(1, F_END + 1):
        p = pos(f); S.key(a.root, f, loc=(p.x, p.y, hic_bump(f)), rot=(0, 0, R(yaw(f))), interp="LINEAR")

    # ---- tapa ----
    for f in range(1, F_END + 12):
        loc, rot = lid_pose(f); lid.location = loc; lid.rotation_euler = rot
        lid.keyframe_insert("location", frame=f); lid.keyframe_insert("rotation_euler", frame=f)
    for mp in S._steam_map:                               # el ruido del vapor evoluciona
        for f in range(1, F_END + 12, 4):
            mp.inputs["Location"].default_value = (0, 0, -0.06 * f); mp.inputs["Location"].keyframe_insert("default_value", frame=f)
    # puffs breves: 4 por hipo (sobre la boca) y uno de polvo al caer plana tras el susto
    pe = []
    for (t0, tu, th, td, ap) in HICS:
        if t0 < 0 and False: continue
        for j, ang in enumerate((20, 110, 200, 290)):
            c = M + Vector((0.5 * math.cos(R(ang)), 0.5 * math.sin(R(ang)), 0.12))
            pe.append((max(1, t0 + 1 + (j % 2)), c, 0.34 if ap > 0.6 else 0.22, 14, 0.5))
    pe += [(177, M + Vector((dx, dy, 0.14)), 0.4, 14, 0.15) for dx, dy in ((0.7, 0.0), (-0.7, 0.0), (0.0, -0.7))]
    pe.sort(key=lambda e: e[0])
    for pi, (f0, c, r, dur, rise) in enumerate(pe):
        if pi >= len(puffs) - 3: break
        o = puffs[pi]
        for (f, sc, dz) in ((f0 - 1, 0.001, 0.0), (f0 + dur * 0.35, r, rise * 0.55), (f0 + dur, 0.001, rise)):
            d = Vector((c.x - M.x, c.y - M.y, 0)); d = d.normalized() if d.length > 0.01 else Vector((0, 0, 0))
            o.location = (c.x + d.x * 0.1 * (f - f0 + 1) / dur * 3, c.y + d.y * 0.1 * (f - f0 + 1) / dur * 3, c.z + dz); o.scale = (sc, sc, sc * 0.85)
            o.keyframe_insert("location", frame=max(1, int(f))); o.keyframe_insert("scale", frame=max(1, int(f)))
    # NUBE blanca opaca y grande (2-3 veces la cabeza) junto a la boca del hombre, delante de la fachada; se disipa en ~0,4 s
    mm_ = steam_mat(S, "boca", False, 8.0); mps = puffs[-3:]
    for q in mps: q.data.materials[0] = mm_
    left = Vector((-0.76, -0.65, 0.0))                    # a la izquierda de la cámara del primer plano
    for f in range(F_HIC_MAN - 2, F_HIC_MAN + 16):
        S.sc.frame_set(f); bpy.context.view_layer.update()
        hp0 = a.head.matrix_world.translation.copy(); t = f - F_HIC_MAN
        for j, q in enumerate(mps):
            tj = t - j
            rr = (0.42, 0.32, 0.28)[j]; dz_, lf_ = ((-0.08, 0.42), (-0.20, 0.64), (-0.36, 0.30))[j]
            if tj < 0: sc = 0.001
            elif tj <= 3: sc = rr * tj / 3.0
            else: sc = max(0.001, rr * (1.0 - (tj - 3) / 7.0))
            q.location = hp0 + Vector((0, 0, dz_ + 0.01 * max(0, tj))) + left * lf_
            q.scale = (sc, sc, sc); q.keyframe_insert("location", frame=f); q.keyframe_insert("scale", frame=f)

    # ---- bota: sale por el borde derecho de la boca en el hipo 1 y rueda lejos de él ----
    B0 = Vector((M.x - 0.78, M.y - 0.1, 0.35)); B1 = Vector((-1.35, -0.8, 0.13)); BR = Vector((-1.12, -0.95, 0.13))
    for f in range(F_BOOT - 6, 140):
        if f < F_BOOT or f >= 100: p, rot = Vector((0, 0, -5)), (0, 0, 0)
        elif f <= F_BOOT + T_BOOT:
            u = (f - F_BOOT) / float(T_BOOT); p = parab(B0, B1, 1.0, u); e = sstep((u - 0.7) / 0.3)
            rot = (R(lerp(-400 * u, 0, e)), R(lerp(0, 90, e)), R(40 * u))
        else:
            t = f - F_BOOT - T_BOOT; u = min(1.0, t / 16.0); p = B1.lerp(BR, u); p.z = 0.13 + 0.4 * abs(math.sin(math.pi * u * 1.5)) * (1 - u); rot = (R(40 * u), R(90), R(40 + 60 * u))
        boot.location = p; boot.rotation_euler = rot
        boot.keyframe_insert("location", frame=f); boot.keyframe_insert("rotation_euler", frame=f)

    # ---- patito: arco hasta las manos, en brazos, al suelo; desaparece en el corte al plano general ----
    hp = hand_mid(S, a, F_CATCH) + Vector((0, 0, 0.05)); D0 = Vector((M.x + 0.78, M.y - 0.1, 0.35))
    for f in range(F_DUCK - 6, 140):
        if f < F_DUCK or f >= 134: p, rot = Vector((0, 0, -5)), (0, 0, 0)
        elif f <= F_CATCH:
            u = (f - F_DUCK) / float(T_DUCK); p = parab(D0, hp, 1.0, u); rot = (R(-360 * (1 - u)), 0, R(180 + 300 * (1 - u)))
        elif f < F_REL:
            p = hand_mid(S, a, f) + Vector((0, 0, 0.06)); rot = (0, 0, R(180))
        elif f < F_REL + 5:
            u = (f - F_REL) / 5.0; p = (hand_mid(S, a, f) + Vector((0, 0, 0.06))).lerp(G_DUCK, u); rot = (0, 0, R(lerp(180, 120, u)))
        else:
            p = G_DUCK; rot = (0, 0, R(120))
        sq = 1.0
        if F_CATCH + 2 <= f <= F_CATCH + 7: sq = 1 - 0.25 * math.sin(math.pi * (f - F_CATCH - 2) / 5.0)        # lo aprieta
        duck.location = p; duck.rotation_euler = rot; duck.scale = (1.5 / sq ** 0.5, 1.5 / sq ** 0.5, 1.5 * sq)
        for pth in ("location", "rotation_euler", "scale"): duck.keyframe_insert(pth, frame=f)

    # ---- palomas: huyen con el primer hipo ----
    for i, b in enumerate(props["birds"]):
        loc0 = Vector(b.location); f0 = 24 + i
        S.key(b, 1, loc=tuple(loc0), interp="LINEAR"); S.key(b, f0, loc=tuple(loc0), interp="LINEAR")
        S.key(b, f0 + 22, loc=(loc0.x - 3.5 - i, loc0.y + 5, 3.5 + i), interp="LINEAR"); S.key(b, f0 + 23, loc=(0, 0, -9), interp="LINEAR")
        for wn, sg in zip(b["wings"], (-1, 1)):
            w = bpy.data.objects[wn]
            for j in range(0, 22, 3):
                w.rotation_euler = (0, R(sg * (55 if (j // 3) % 2 == 0 else -35)), 0); w.keyframe_insert("rotation_euler", frame=f0 + j)
            w.rotation_euler = (0, 0, 0); w.keyframe_insert("rotation_euler", frame=1); w.keyframe_insert("rotation_euler", frame=f0 - 1)

    # ---- sonido: hic antes de cada salto, clonk al caer; el susto cae en SILENCIO ----
    for (t0, tu, th, td, ap) in HICS:
        if t0 > 0: S.cue("hic", t0 - 2, vol=-3); S.cue("whoosh", t0, vol=-14)
    for l in LAND: S.cue("clunk", l, vol=-4)
    S.cue("pop", F_BOOT, vol=-6); S.cue("hit", F_BOOT + T_BOOT, vol=-6)
    S.cue("pop", F_DUCK, vol=-6); S.cue("squeak", F_CATCH, vol=-5)
    S.cue("step", F_SNEAK0 + 6, vol=-16); S.cue("step", F_SNEAK0 + 16, vol=-16); S.cue("step", F_SNEAK0 + 26, vol=-16)
    S.cue("huh", F_BOO + 3, vol=-6)                                                    # su "¡bu!"; después silencio hasta el alivio
    S.cue("sigh", 186, vol=-5)                                                         # alivio
    S.cue("hic", F_HIC_MAN, vol=-2)                                                    # el hic pasa a él (mismo sonido que la tapa)

    # ---- cara ----
    expression(a, "neutra", 1, 1.0, ramp=2)
    expression(a, "sorpresa", 18, 1.0, ramp=3); expression(a, "neutra", 60, 1.0, ramp=4); expression(a, "feliz", F_CATCH + 2, 1.0, ramp=4)
    expression(a, "neutra", 98, 1.0, ramp=6); expression(a, "enfado", F_CHARGE0, 0.7, ramp=4); expression(a, "feliz", F_BOO + 2, 1.0, ramp=3)
    expression(a, "neutra", 178, 1.0, ramp=5); expression(a, "feliz", 184, 0.7, ramp=4); expression(a, "neutra", 200, 1.0, ramp=4)
    expression(a, "sorpresa", F_HIC_MAN - 1, 1.0, ramp=3); expression(a, "sorpresa", 226, 0.5, ramp=5); expression(a, "neutra", 250, 1.0, ramp=10)
    for f in (14, 62, 120, 196, 270): blink(a, f)

    # ---- cámara: cortes (CONSTANT) ----
    shots = [(1, CAM_W),
             (50, ((3.8, -4.1, 1.1), (0.7, -0.1, 1.3), 40, 5.3)),                     # medio: caza el patito y lo deja
             (100, CAM_W),                                                            # se aleja agachado
             (134, ((-0.2, -6.0, 1.2), (-0.25, -0.2, 1.45), 50, 5.8)),                # plano medio: carga, salta ante la tapa, la tapa se congela
             (178, ((2.6, -3.4, 1.5), (-0.15, -0.2, 1.8), 35, 4.1)),                    # PRIMER PLANO del remate: él y la tapa detrás
             (F_CUT_WIDE, CAM_W)]                                                     # encuadre del fotograma 1: bucle
    for f, (loc, tg, lens, foc) in shots: cam_set(S, f, loc, tg, lens, foc)
    S.set_interp(S.cam, "CONSTANT", ("location",)); S.set_interp(S.cam.data, "CONSTANT"); S.set_interp(S.tgt, "CONSTANT")
    S.f = F_END
    a.verify(S.f)
    return a


LEVELS = [(0, l1)]
