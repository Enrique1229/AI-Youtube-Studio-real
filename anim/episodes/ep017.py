"""ep017 — Mini-historia: "The Manhole That Hiccuped" (story-020, idea b20261123-2-i01). Plaza urbana (env_real.build_plaza: HDRI dresden_square,
adoquín PBR, 19 piezas de atrezo Poly Haven, bordillo, calzada, charcos, hojas, palomas). Cámara baja (z=1,2, horizontal) que deja ver la boca en el suelo y la tapa en lo alto.

Tapa de alcantarilla gigante (disco de hierro de 1,3 m con nervios por ambas caras, marco claro con boca negra) que da hipo sobre un chorro de
vapor (cilindro semitransparente con ruido que sube). Cada hipo: pop, la tapa sube inclinada y escupe un objeto de primitivas.
  1-28    gancho: la tapa en lo alto sobre el vapor (encuadre del fotograma 1), el hombre agachado a un lado; cae con CLONK.
  60-135  hipo 1: bota roja; el hombre da un salto atrás y la bota rueda lejos. Hipo 2: patito de goma; vuelve de un salto y lo caza (SQUEAK).
  146-204 se agacha a cubierto (sobre el adoquín, sin objetos delante); sale con los brazos arriba; la tapa se queda CONGELADA en lo alto y cae plana con PLATILLO.
  204-300 alivio (asiente, suspira), le da un HIC a él: salta unos centímetros, la tapa responde con un clonk burlón y sube otra vez
          sobre el vapor; él se agacha: mismo encuadre y pose del fotograma 1 (bucle).
Convenio: yaw 0 mira a cámara (-y); yaw -50 mira a la tapa (izquierda) y a cámara. Fotograma 24 fps, ~12,5 s."""
import math
import bpy
from mathutils import Vector
from mixamo import MixamoActor
from klunk_toon import apply as klunk, expression, blink
import env_real

TITLE = "The Manhole That Hiccuped"
CAPTION = None
SPEED = 1.0
ENV = "mesa"                      # base mínima del kit; build_plaza la vacía y monta la plaza
CUSTOM_CAMERA = True

FPS = 24
F_END = 300
M = Vector((-0.55, 0.0, 0.0))     # centro de la tapa
P1 = Vector((0.9, 0.6, 0.0))      # sitio del hombre (inicio y final)
P2 = Vector((1.1, 1.7, 0.0))      # tras el salto atrás
YAW = -50.0
LR = 0.66                         # radio de la tapa
LID_Z0 = 0.03                     # centro de la tapa asentada (plana en su aro)
APEX = 2.2
TILT = -40.0                      # grados en x: la cara inferior mira a la cámara baja

# eventos de la tapa: (inicio, subida, fotograma hasta el que se mantiene arriba, caída). El primero ya empieza arriba (gancho).
HICS = [(-50, 1, 20, 8), (62, 8, 73, 9), (106, 8, 117, 9), (150, 8, 196, 8), (250, 9, 10 ** 5, 1)]
LAND = [28, 82, 126, 204]          # aterrizajes (suenan)
F_FREEZE0, F_FREEZE1 = 167, 196
F_BOOT, T_BOOT = 64, 26           # lanzamiento de la bota y vuelo
F_DUCK, T_DUCK = 108, 28
F_CATCH = F_DUCK + T_DUCK
F_HOP1, F_HOP2 = 76, 112          # inicio de los clips Jumping (despegue +5, aterrizaje +23)
F_HIC_MAN = 240
F_SUCK, T_SUCK = 252, 14          # la tapa se lleva el patito


def R(d): return math.radians(d)
def sstep(t): t = max(0.0, min(1.0, t)); return t * t * (3 - 2 * t)
def lerp(a, b, t): return a + (b - a) * t


# ------------------------------------------------------------------ estado de la tapa
def lid_k(f):
    """Altura normalizada de la tapa (0 asentada, 1 en el ápice)."""
    k = 0.0
    for (t0, tu, th, td) in HICS:
        if t0 <= f < t0 + tu: k = 1 - (1 - (f - t0) / float(tu)) ** 2
        elif t0 + tu <= f < th: k = 1.0
        elif th <= f < th + td: k = (1 - (f - th) / float(td)) ** 2
    return k


def lid_pose(f):
    k = lid_k(f)
    z = LID_Z0 + (APEX - LID_Z0) * k
    rx = TILT * k; rz = 22.0 * k; ry = 0.0
    # temblor mientras flota (se apaga en la congelación) y balanceo al asentarse
    if k > 0.99 and not (F_FREEZE0 <= f <= F_FREEZE1) and f > 3: rx += 3.0 * math.sin(0.6 * f); ry += 2.5 * math.cos(0.5 * f)
    if F_FREEZE0 <= f <= F_FREEZE0 + 4: rx += 2.0 * math.sin(7.0 * f)
    for l in LAND:
        if l <= f < l + 10:
            u = (f - l) / 10.0; z += 0.05 * abs(math.sin(math.pi * u * 2)) * (1 - u); rx += 5 * math.sin(u * 14) * (1 - u); ry += 4 * math.cos(u * 11) * (1 - u)
    # el final: la tapa responde al hipo de él con un saltito antes de subir
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
    em.inputs["Color"].default_value = (0.93, 0.96, 1.0, 1); em.inputs["Strength"].default_value = 1.4
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
    col = S.empty("vapor", (M.x, M.y, 0.012))
    cm = steam_mat(S, "col", True, 1.0)
    O(S, "cylinder", "col_vapor", cm, (0, 0, 0.5), (0.58, 0.58, 0.5), parent=col, vertices=32)
    O(S, "cylinder", "col_vapor2", cm, (0, 0, 0.5), (0.36, 0.36, 0.5), parent=col, vertices=24)
    puffs = []
    pm = steam_mat(S, "puff", False, 0.9)
    for i in range(24):
        puffs.append(O(S, "uv_sphere", "puff", pm, (M.x, M.y, 0.2), (0.001,) * 3, segments=16, ring_count=8))
    return col, puffs


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
def l1(S):
    props = env_real.build_plaza(S, rot_deg=20)
    lid = build_manhole(S); steam, puffs = build_steam(S); boot = build_boot(S); duck = build_duck(S)
    a = MixamoActor(S, x=P1.x, yaw=YAW, use=["Looking Around", "Sneaking Forward", "Surprised", "Jumping", "Picking Up", "Victory", "Head Nod Yes"]); klunk(a)

    # ---- hombre: clips ----
    SNEAK = 8                                            # fotograma del clip Sneaking Forward = pose de agachado del plano 1
    seg(S, a, "Sneaking Forward", 1, 62, start=SNEAK, speed=0.35, blend=0)
    seg(S, a, "Surprised", 60, 76, start=14, speed=1.6, blend=4)                       # hic 1: respingo
    seg(S, a, "Jumping", F_HOP1, F_HOP1 + 24, start=14, blend=3)                       # salto atrás
    seg(S, a, "Surprised", F_HOP1 + 24, F_HOP2, start=14, speed=1.8, blend=3)          # hic 2: otro respingo
    seg(S, a, "Jumping", F_HOP2, F_HOP2 + 22, start=14, blend=3)                       # vuelve de un salto
    seg(S, a, "Picking Up", F_CATCH - 8, F_CATCH + 10, start=118, speed=0.5, blend=4)    # brazos al frente: caza el patito
    seg(S, a, "Picking Up", F_CATCH + 10, 166, start=20, speed=1.0, blend=6)            # se agacha (con el patito)
    seg(S, a, "Victory", 166, 204, start=18, speed=1.0, blend=4)                       # susto: brazos arriba
    seg(S, a, "Head Nod Yes", 204, F_HIC_MAN - 4, start=0, speed=1.5, blend=5)         # alivio: asiente
    seg(S, a, "Surprised", F_HIC_MAN - 4, 258, start=14, speed=1.6, blend=3)           # hic propio
    seg(S, a, "Sneaking Forward", 258, F_END, start=SNEAK - 4, speed=0.35, blend=8)    # vuelve a agacharse: pose del plano 1

    # ---- hombre: posición ----
    def pos(f):
        if f <= F_HOP1 + 5: return P1
        if f <= F_HOP1 + 23: return P1.lerp(P2, sstep((f - F_HOP1 - 5) / 18.0))
        if f <= F_HOP2 + 5: return P2
        if f <= F_HOP2 + 23: return P2.lerp(P1, sstep((f - F_HOP2 - 5) / 18.0))
        return P1
    hic_bump = lambda f: 0.16 * math.sin(math.pi * min(1.0, max(0.0, (f - F_HIC_MAN) / 5.0))) if F_HIC_MAN <= f <= F_HIC_MAN + 5 else 0.0
    bpy.context.preferences.edit.keyframe_new_interpolation_type = "LINEAR"
    for f in range(1, F_END + 1):
        p = pos(f); S.key(a.root, f, loc=(p.x, p.y, hic_bump(f)), rot=(0, 0, R(YAW)), interp="LINEAR")

    # ---- tapa y vapor ----
    for f in range(1, F_END + 12):
        loc, rot = lid_pose(f); lid.location = loc; lid.rotation_euler = rot
        lid.keyframe_insert("location", frame=f); lid.keyframe_insert("rotation_euler", frame=f)
        k = lid_k(f); h = max(0.0, loc[2] - 0.2) if k > 0.02 else 0.0
        steam.scale = (1.0 + 0.04 * math.sin(0.5 * f), 1.0 + 0.04 * math.cos(0.4 * f), max(0.001, h)); steam.keyframe_insert("scale", frame=f)
    for mp in S._steam_map:                               # el ruido sube con el tiempo
        for f in range(1, F_END + 12, 4):
            if F_FREEZE0 <= f <= F_FREEZE1: continue
            mp.inputs["Location"].default_value = (0, 0, -0.045 * min(f, F_FREEZE0) if f < F_FREEZE0 else -0.045 * F_FREEZE0 - 0.045 * (f - F_FREEZE1))
            mp.inputs["Location"].keyframe_insert("default_value", frame=f)
    # bocanadas de vapor/polvo: (fotograma, centro, radio, duración, subida)
    puff_events = []
    for t0 in (62, 106, 150, 250): puff_events += [(t0 + 1, M + Vector((dx, dy, 0.25)), 0.5, 16, 0.6) for dx, dy in ((0.35, 0.0), (-0.35, 0.1), (0.0, -0.4))]
    for l in LAND: puff_events += [(l, M + Vector((dx, dy, 0.18)), 0.45 if l != 204 else 0.8, 16 if l != 204 else 22, 0.2) for dx, dy in ((0.8, 0.1), (-0.8, 0.0), (0.2, -0.8), (0.0, 0.8))]
    pi = 0
    for (f0, c, r, dur, rise) in puff_events:
        if pi >= len(puffs): break
        o = puffs[pi]; pi += 1
        for (f, sc, dz, dx) in ((f0 - 1, 0.001, 0.0, 0.0), (f0 + dur * 0.4, r, rise * 0.5, 0.2), (f0 + dur, 0.001, rise, 0.4)):
            d = (c - M); d.z = 0; d = d.normalized() if d.length > 0.01 else Vector((0, 0, 0))
            o.location = (c.x + d.x * dx, c.y + d.y * dx, c.z + dz); o.scale = (sc, sc, sc * 0.8)
            o.keyframe_insert("location", frame=int(f)); o.keyframe_insert("scale", frame=int(f))

    # ---- bota: sale a la derecha por el borde de la boca, rueda lejos de él ----
    B0 = Vector((M.x + 0.62, M.y - 0.05, 0.30)); B1 = Vector((P1.x - 0.50, P1.y - 0.35, 0.13)); BR = Vector((P1.x - 1.15, P1.y - 0.55, 0.13))
    for f in range(F_BOOT - 6, F_BOOT + T_BOOT + 20):
        if f < F_BOOT: p, rot = Vector((0, 0, -5)), (0, 0, 0)
        elif f <= F_BOOT + T_BOOT:
            u = (f - F_BOOT) / float(T_BOOT); p = parab(B0, B1, 1.55, u); e = sstep((u - 0.7) / 0.3)
            rot = (R(lerp(-400 * u, 0, e)), R(lerp(0, 90, e)), R(40 * u))
        else:
            t = f - F_BOOT - T_BOOT                   # dos botes y rueda hasta BR
            u = min(1.0, t / 16.0); p = B1.lerp(BR, u); p.z = 0.13 + 0.45 * abs(math.sin(math.pi * u * 1.5)) * (1 - u) ; rot = (R(40 * u), R(90), R(40 + 60 * u))
        boot.location = p; boot.rotation_euler = rot
        boot.keyframe_insert("location", frame=f); boot.keyframe_insert("rotation_euler", frame=f)
    boot.location = (0, 0, -5); boot.keyframe_insert("location", frame=F_BOOT - 7)
    boot.keyframe_insert("location", frame=F_CATCH + 40)

    # ---- patito: arco hasta las manos del hombre y luego las sigue ----
    hp = hand_mid(S, a, F_CATCH) + Vector((0, 0, 0.05)); D0 = Vector((M.x + 0.62, M.y, 0.30))
    for f in range(F_DUCK - 6, F_END + 12):
        if f < F_DUCK: p, rot = Vector((0, 0, -5)), (0, 0, 0)
        elif f <= F_CATCH:
            u = (f - F_DUCK) / float(T_DUCK); p = parab(D0, hp, 1.5, u); rot = (R(-360 * (1 - u)), 0, R(180 + 300 * (1 - u)))
        elif f < F_SUCK:
            h_ = hand_mid(S, a, f) + Vector((0, 0, 0.06)); p = h_; rot = (0, 0, R(180))
        elif f <= F_SUCK + T_SUCK:                         # la tapa se lo lleva: vuela a la boca y se pierde en el vapor (cierra el bucle)
            u = (f - F_SUCK) / float(T_SUCK); p = parab(hand_mid(S, a, F_SUCK) + Vector((0, 0, 0.06)), Vector((M.x + 0.1, M.y, 0.9)), 0.9, u)
            rot = (R(-300 * u), 0, R(180 + 240 * u))
        else:
            p = Vector((0, 0, -5)); rot = (0, 0, 0)
        sq = 1.0
        if F_CATCH + 4 <= f <= F_CATCH + 9: sq = 1 - 0.25 * math.sin(math.pi * (f - F_CATCH - 4) / 5.0)       # lo aprieta
        duck.location = p; duck.rotation_euler = rot; duck.scale = (1.5 / sq ** 0.5, 1.5 / sq ** 0.5, 1.5 * sq)
        for pth in ("location", "rotation_euler", "scale"): duck.keyframe_insert(pth, frame=f)
    duck.location = (0, 0, -5); duck.keyframe_insert("location", frame=F_DUCK - 7)

    # ---- palomas: huyen con el primer hipo ----
    for i, b in enumerate(props["birds"]):
        loc0 = Vector(b.location); f0 = 61 + i
        S.key(b, 1, loc=tuple(loc0), interp="LINEAR"); S.key(b, f0, loc=tuple(loc0), interp="LINEAR")
        S.key(b, f0 + 22, loc=(loc0.x - 3.5 - i, loc0.y + 5, 3.5 + i), interp="LINEAR"); S.key(b, f0 + 23, loc=(0, 0, -9), interp="LINEAR")
        for wn, sg in zip(b["wings"], (-1, 1)):
            w = bpy.data.objects[wn]
            for j in range(0, 22, 3):
                w.rotation_euler = (0, R(sg * (55 if (j // 3) % 2 == 0 else -35)), 0); w.keyframe_insert("rotation_euler", frame=f0 + j)
            w.rotation_euler = (0, 0, 0); w.keyframe_insert("rotation_euler", frame=1); w.keyframe_insert("rotation_euler", frame=f0 - 1)

    # ---- sonido (un sonido distinto por beat; sin tono ascendente repetido) ----
    S.cue("clunk", 28, vol=-3); S.cue("whoosh", 20, vol=-12)                                 # gancho: la tapa cae
    S.cue("hic", 60, vol=-3); S.cue("whoosh", 63, vol=-9); S.cue("pop", F_BOOT, vol=-6)       # hipo 1 + bota
    S.cue("hit", F_BOOT + T_BOOT, vol=-6); S.cue("clunk", 82, vol=-6); S.cue("step", F_BOOT + T_BOOT + 9, vol=-12)
    S.cue("hic", 104, vol=-3); S.cue("whoosh", 107, vol=-9); S.cue("pop", F_DUCK, vol=-6)     # hipo 2 + patito
    S.cue("clunk", 126, vol=-6); S.cue("squeak", F_CATCH, vol=-5); S.cue("oof", F_CATCH + 1, vol=-12)
    S.cue("hic", 148, vol=-3); S.cue("whoosh", 151, vol=-9)                                  # hipo 3: sube
    S.cue("huh", 167, vol=-6)                                                                # susto: la tapa se congela
    S.cue("cymbal", 204, vol=-5); S.cue("hit", 204, vol=-10)                                 # cae plana: platillo
    S.cue("sigh", 214, vol=-5); S.cue("step", 230, vol=-14)
    S.cue("hic", F_HIC_MAN, vol=-2); S.cue("clunk", 250, vol=-4); S.cue("whoosh", 252, vol=-8); S.cue("pop", F_SUCK + T_SUCK, vol=-8)   # él da hic; la tapa responde y sube

    # ---- cara ----
    expression(a, "neutra", 1, 1.0, ramp=2)
    expression(a, "sorpresa", 58, 1.0, ramp=3); expression(a, "enfado", 90, 0.4, ramp=5)
    expression(a, "sorpresa", 104, 1.0, ramp=3); expression(a, "feliz", F_CATCH + 2, 1.0, ramp=4)
    expression(a, "neutra", 146, 1.0, ramp=6); expression(a, "sorpresa", 168, 0.8, ramp=3); expression(a, "feliz", 198, 0.7, ramp=4)
    expression(a, "feliz", 210, 1.0, ramp=4); expression(a, "neutra", 232, 1.0, ramp=3); expression(a, "sorpresa", F_HIC_MAN - 1, 1.0, ramp=3)
    expression(a, "enfado", 258, 0.6, ramp=5); expression(a, "neutra", 280, 1.0, ramp=10)
    for f in (30, 86, 178, 224, 268): blink(a, f)

    # ---- cámara: cortes (CONSTANT); el último repite el encuadre del fotograma 1 ----
    shots = [(1, CAM_W),
             (130, ((3.6, -3.9, 1.1), (0.75, 0.6, 1.25), 45, 5.4)),                    # medio: caza el patito
             (146, CAM_W),                                                            # esconderse y susto
             (194, ((0.9, -5.4, 0.45), (0.0, 0.2, 1.2), 36, 5.6)),                  # la tapa cae plana (platillo)
             (212, ((3.3, -4.8, 1.3), (1.0, 0.6, 1.12), 45, 5.9)),                    # alivio + hic: la cara
             (256, CAM_W)]                                                            # encuadre del fotograma 1: bucle
    for f, (loc, tg, lens, foc) in shots: cam_set(S, f, loc, tg, lens, foc)
    S.set_interp(S.cam, "CONSTANT", ("location",)); S.set_interp(S.cam.data, "CONSTANT"); S.set_interp(S.tgt, "CONSTANT")
    S.f = F_END
    a.verify(S.f)
    return a


LEVELS = [(0, l1)]
