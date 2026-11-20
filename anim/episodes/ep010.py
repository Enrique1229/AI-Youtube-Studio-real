"""ep010 — Cada nivel de IQ toca la campana de un poste alto. Parque junto al río (realista, personaje humano de Mixamo).
-450 salta con el brazo estirado y no llega (cae en cuclillas y se enfada); -80 lanza su zapato: rebota en el poste y le da en la cabeza;
120 trepa el poste y roza la campana con un dedo (dling mínimo); 900 empuja una papelera bajo la campana, se sube y salta: dling a lo grande;
5469 mira alrededor, ve la cuerda de tirar que cuelga detrás del poste (visible desde el fotograma 1), la agarra y tira: campana a todo trapo.
(Mejora del crítico: el 900 NO usa cuerda; la cuerda de tirar se ve de reojo en todos los niveles y solo la usa el 5469.)"""
import math
import random
import bmesh
import bpy
from mathutils import Vector
from mixamo import MixamoActor

TITLE = "Every IQ Level Rings the Bell on a Tall Post"
ONSCREEN = "Every IQ level rings the bell"
ENV = "parque"
CUSTOM_CAMERA = True
LABEL_STYLE = "big"

PX = -6.2            # x del poste (y = 0)
POLE_H = 3.55
BX = PX + 0.40       # x de la campana (cuelga de un brazo a la derecha del poste)
BELL_S = 1.3         # escala de la campana (grande en móvil)
BZ = 3.42            # punto de cuelgue de la campana
RY = 0.55            # y de la cuerda de tirar (detrás del plano del poste)
KX = PX + 0.20       # x donde la cuerda está enrollada en el suelo (detrás del poste)
BIN_H = 0.96


def R(d): return math.radians(d)


# ------------------------------------------------------------------ materiales y utilidades
def mmat(S, name, rgb, rough=0.5, metal=0.0, emit=None, alpha=None):
    k = "m_" + name
    if k in S.mats: return S.mats[k]
    m = bpy.data.materials.new(k); m.use_nodes = True
    b = m.node_tree.nodes["Principled BSDF"]
    b.inputs["Base Color"].default_value = (*rgb, 1); b.inputs["Roughness"].default_value = rough; b.inputs["Metallic"].default_value = metal
    if emit:
        b.inputs["Emission Color"].default_value = (*emit, 1); b.inputs["Emission Strength"].default_value = 3.0
    S.mats[k] = m
    return m


def O(S, prim, name, mat, loc=(0, 0, 0), scale=(1, 1, 1), rot=(0, 0, 0), parent=None, smooth=True, **kw):
    o = S.obj(prim, name, "white", loc, scale, rot, parent, smooth, **kw); o.data.materials[0] = mat; return o


def pole_wood(S):
    """Madera real (Poly Haven brown_planks_03) con el mapeo estirado para un cilindro (vueltas x metros)."""
    if "pole_wood" in S.mats: return S.mats["pole_wood"]
    import env_real
    base = env_real._pbr(S, "brown_planks_03", res="1k", scale=1.5)
    m = base.copy(); m.name = "pole_wood"
    for n in m.node_tree.nodes:
        if n.type == "MAPPING": n.inputs["Scale"].default_value = (1.0, 5.0, 1.0)
    S.mats["pole_wood"] = m
    return m


def lathe(S, name, prof, mat, steps=40, thick=0.016):
    """Sólido de revolución (campana) a partir de un perfil (radio, z)."""
    me = bpy.data.meshes.new(name); bm = bmesh.new()
    vs = [bm.verts.new((r, 0, z)) for r, z in prof]
    es = [bm.edges.new((vs[i], vs[i + 1])) for i in range(len(vs) - 1)]
    bmesh.ops.spin(bm, geom=vs + es, cent=(0, 0, 0), axis=(0, 0, 1), angle=2 * math.pi, steps=steps)
    bmesh.ops.remove_doubles(bm, verts=bm.verts, dist=1e-5)
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    bm.to_mesh(me); bm.free()
    for p in me.polygons: p.use_smooth = True
    o = bpy.data.objects.new(name, me); S.sc.collection.objects.link(o); o.data.materials.append(mat)
    md = o.modifiers.new("grosor", "SOLIDIFY"); md.thickness = thick; md.offset = -1
    return o


def head_pos(S, a, f):
    S.sc.frame_set(f); bpy.context.view_layer.update()
    return a.head.matrix_world.translation.copy()


def bone_pos(S, a, bone, f, frac=0.0):
    """Posición mundial de un hueso (0 = base, 1 = punta) en el fotograma f."""
    S.sc.frame_set(f); bpy.context.view_layer.update()
    pb = a.arm.pose.bones[a.pfx + bone]
    return a.arm.matrix_world @ (pb.head + (pb.tail - pb.head) * frac)


def cam_static(S, cx=PX - 0.2, lens=44, dist=6.5, tz=2.0):
    loc = (cx, -dist, tz + 0.05); tgt = (cx, 0, tz)
    S.cam.location = loc; S.cam.data.lens = lens; S.tgt.location = tgt
    S.cam.keyframe_insert("location", frame=1); S.cam.data.keyframe_insert("lens", frame=1); S.tgt.keyframe_insert("location", frame=1)


def place(S, a, f, x, y, z=0.0, yaw=0.0, interp="BEZIER"):
    S.key(a.root, f, loc=(x, y, z), rot=(0, 0, R(yaw)), interp=interp)


def seg(S, a, clip, f0, f1=None, start=0, speed=1.0, blend=4):
    """Clip en [f0, f1] (se funde con el siguiente en `blend` fotogramas). f1=None: último clip (sostiene su pose final)."""
    S.f = f0
    cl = a.clips[clip]; avail = int((cl.frame_range[1] - cl.frame_range[0] - start) / speed)
    a.play(clip, frames=(min(avail, f1 - f0 + blend) if f1 is not None else None), speed=speed, blend=blend, start=start)


def dust(S, x, y, z, f, n=5, spread=0.4, size=0.07, rise=0.3, seed=0):
    rr = random.Random(seed + int(x * 10) + f); m = mmat(S, "polvo", (0.36, 0.29, 0.19), rough=1.0)
    for i in range(n):
        d = S.obj("uv_sphere", "polvo", "white", (x, y, z), (0.001,) * 3, segments=8, ring_count=6); d.data.materials[0] = m
        dx = rr.uniform(-spread, spread); dy = rr.uniform(-spread * 0.5, spread * 0.5); sz = size * rr.uniform(0.7, 1.3)
        S.key(d, f - 1, loc=(x, y, z), scale=(0.001,) * 3)
        S.key(d, f + 4, loc=(x + dx * 0.6, y + dy, z + rise * 0.4), scale=(sz, sz * 0.8, sz * 0.8))
        S.key(d, f + 14, loc=(x + dx, y + dy, z + rise), scale=(sz * 1.4, sz, sz))
        S.key(d, f + 19, loc=(x + dx * 1.1, y + dy, z + rise * 1.1), scale=(0.001,) * 3)


def daze(S, p, f0, n=40):
    """Estrellitas que giran sobre la cabeza (centro p) durante n fotogramas."""
    m = mmat(S, "estrella", (1.0, 0.85, 0.15), rough=0.4, emit=(1.0, 0.8, 0.1))
    for i in range(3):
        o = S.obj("uv_sphere", "estrella", "white", tuple(p), (0.001,) * 3, segments=6, ring_count=4); o.data.materials[0] = m
        ph = 2 * math.pi * i / 3
        for k in range(0, n + 1, 2):
            ang = ph + k * 0.32
            loc = (p.x + 0.26 * math.cos(ang), p.y + 0.12 * math.sin(ang), p.z + 0.32 + 0.03 * math.sin(ang * 2))
            sc = 0.05 * min(1.0, k / 4.0, (n - k) / 4.0 + 0.001)
            S.key(o, f0 + k, loc=loc, rot=(ang, 0, 0), scale=(max(0.001, sc),) * 3, interp="LINEAR")
    S.cue("pop", f0, vol=-9)


# ------------------------------------------------------------------ escenario: poste, campana, cuerda, papelera, zapato
class W: pass


def build_set(S, rope=False):
    w = W()
    for o in list(S.sc.objects):                                   # matas de hierba fuera del pie del poste y de la cuerda enrollada
        if o.instance_type == "COLLECTION" and "grass" in o.name and math.hypot(o.location.x - PX, o.location.y - 0.35) < 0.95:
            bpy.data.objects.remove(o, do_unlink=True)
    wood = pole_wood(S)
    iron = mmat(S, "hierro", (0.07, 0.075, 0.08), rough=0.45, metal=0.9)
    brass = mmat(S, "laton", (0.85, 0.58, 0.18), rough=0.26, metal=1.0)
    dark = mmat(S, "interior", (0.12, 0.07, 0.03), rough=0.5, metal=0.8)
    rope_m = mmat(S, "cuerda", (0.62, 0.50, 0.30), rough=0.95)
    soil = mmat(S, "tierra_poste", (0.20, 0.13, 0.07), rough=1.0)
    # poste (3,55 m, tres veces la altura de la cadera: la campana queda fuera del alcance de un salto)
    O(S, "cylinder", "poste", wood, (PX, 0, POLE_H / 2), (0.075, 0.075, POLE_H / 2), vertices=24)
    O(S, "cylinder", "base_poste", wood, (PX, 0, 0.05), (0.15, 0.15, 0.05), vertices=24)
    O(S, "uv_sphere", "remate_poste", iron, (PX, 0, POLE_H + 0.0), (0.095, 0.095, 0.07), segments=16, ring_count=10)
    O(S, "cylinder", "tierra_base", soil, (PX, 0, 0.012), (0.42, 0.34, 0.012), vertices=20, smooth=False)
    # brazo de hierro con refuerzo, hasta la campana
    O(S, "cube", "brazo", iron, ((PX + BX) / 2, 0, BZ + 0.03), ((BX - PX) / 2 + 0.05, 0.028, 0.028), smooth=False)
    O(S, "cube", "refuerzo", iron, (PX + 0.15, 0, BZ - 0.14), (0.20, 0.016, 0.016), rot=(0, R(-45), 0), smooth=False)
    O(S, "cylinder", "colgador", iron, (BX, 0, BZ - 0.02), (0.012, 0.012, 0.045), vertices=8)
    # campana de latón con badajo
    w.bell = S.empty("campana", (BX, 0, BZ)); w.bell.scale = (BELL_S,) * 3
    prof = [(0.0, -0.10), (0.045, -0.105), (0.085, -0.125), (0.112, -0.20), (0.128, -0.29), (0.148, -0.37), (0.185, -0.44), (0.225, -0.495), (0.238, -0.51)]
    b = lathe(S, "campana_cuerpo", prof, brass); b.parent = w.bell
    O(S, "cylinder", "boca_campana", dark, (0, 0, -0.50), (0.222, 0.222, 0.004), parent=w.bell, vertices=32, smooth=False)
    w.clapper = S.empty("badajo", (0, 0, -0.13), parent=w.bell)
    O(S, "cylinder", "varilla_badajo", iron, (0, 0, -0.14), (0.006, 0.006, 0.14), parent=w.clapper, vertices=8)
    O(S, "uv_sphere", "bola_badajo", iron, (0, 0, -0.31), (0.036, 0.036, 0.036), parent=w.clapper, segments=12, ring_count=8)
    S.key(w.bell, 1, rot=(0, 0, 0)); S.key(w.clapper, 1, rot=(0, 0, 0))
    w.top = Vector((BX, RY, BZ + 0.03)); w.K0 = Vector((KX, RY + 0.05, 0.14))
    if rope: build_rope(S, w, iron, wood)
    # papelera de parque (1 m): chapa verde con aros y boca negra
    w.bin = S.empty("papelera", (-9, -0.45, 0))
    gm = mmat(S, "papelera", (0.10, 0.30, 0.16), rough=0.4, metal=0.7)
    O(S, "cylinder", "pap_cuerpo", gm, (0, 0, BIN_H / 2 - 0.01), (0.27, 0.27, BIN_H / 2 - 0.02), parent=w.bin, vertices=32)
    O(S, "cylinder", "pap_aro_sup", iron, (0, 0, BIN_H - 0.03), (0.285, 0.285, 0.03), parent=w.bin, vertices=32)
    O(S, "cylinder", "pap_boca", dark, (0, 0, BIN_H - 0.002), (0.235, 0.235, 0.004), parent=w.bin, vertices=32, smooth=False)
    O(S, "cylinder", "pap_aro_inf", iron, (0, 0, 0.08), (0.28, 0.28, 0.025), parent=w.bin, vertices=32)
    for z in (0.35, 0.6):
        O(S, "cylinder", "pap_banda", iron, (0, 0, z), (0.276, 0.276, 0.012), parent=w.bin, vertices=32)
    S.key(w.bin, 1, loc=(-9, -0.45, 0))                        # fuera de cuadro salvo en el 900
    # zapato de cuero marrón (para el -80)
    leather = mmat(S, "cuero", (0.16, 0.07, 0.03), rough=0.5)
    sole = mmat(S, "suela", (0.05, 0.04, 0.035), rough=0.9)
    w.shoe = S.empty("zapato", (0, 0, -9))
    O(S, "cube", "suela", sole, (0.0, 0, 0.0), (0.145, 0.052, 0.018), parent=w.shoe, smooth=False)
    O(S, "uv_sphere", "empeine", leather, (0.03, 0, 0.045), (0.13, 0.05, 0.05), parent=w.shoe, segments=14, ring_count=8)
    O(S, "uv_sphere", "puntera", leather, (0.10, 0, 0.03), (0.06, 0.048, 0.036), parent=w.shoe, segments=12, ring_count=8)
    O(S, "cylinder", "caña", leather, (-0.07, 0, 0.09), (0.045, 0.04, 0.06), parent=w.shoe, vertices=12)
    O(S, "cube", "tacon", sole, (-0.09, 0, -0.015), (0.04, 0.05, 0.016), parent=w.shoe, smooth=False)
    w.shoe.scale = (1.4, 1.4, 1.4)
    return w


def build_rope(S, w, iron, wood):
    """Solo en el 5469: gancho trasero, cuerda (oculta hasta que la recoge) y el sobrante enrollado en el suelo detrás del poste."""
    rope_m = mmat(S, "cuerda", (0.62, 0.48, 0.26), rough=0.95)
    O(S, "cube", "gancho_cuerda", iron, (BX, RY / 2, BZ + 0.03), (0.016, RY / 2 + 0.02, 0.016), smooth=False)
    w.rope = O(S, "cylinder", "cuerda", rope_m, tuple(w.top), (0.001,) * 3, vertices=8, smooth=False)
    w.toggle = O(S, "uv_sphere", "tirador", wood, tuple(w.K0), (0.001,) * 3, segments=12, ring_count=8)
    w.coil = S.empty("cuerda_enrollada", (KX, RY + 0.05, 0.0))
    for k in range(4):
        O(S, "uv_sphere", "vuelta", rope_m, (0.03 * math.cos(k * 1.7), 0.03 * math.sin(k * 1.7), 0.04 + 0.045 * (k % 3)), (0.17 - 0.016 * k, 0.17 - 0.016 * k, 0.034),
          rot=(0, 0, k * 0.9), parent=w.coil, segments=16, ring_count=6)
    O(S, "uv_sphere", "tirador_suelo", wood, (0.0, 0.0, 0.14), (0.032, 0.032, 0.05), parent=w.coil, segments=12, ring_count=8)
    S.key(w.coil, 1, scale=(1, 1, 1)); S.key(w.rope, 1, scale=(0.001,) * 3); S.key(w.toggle, 1, scale=(0.001,) * 3)


def rope_set(S, w, f, K):
    """La cuerda va del gancho (fijo) al tirador K (posición mundial) en el fotograma f."""
    A = w.top; d = Vector(K) - A; L = d.length
    q = Vector((0, 0, 1)).rotation_difference(d.normalized()); e = q.to_euler()
    S.key(w.rope, f, loc=tuple((A + Vector(K)) / 2), rot=(e.x, e.y, e.z), scale=(0.014, 0.014, L / 2), interp="LINEAR")
    S.key(w.toggle, f, loc=tuple(K), scale=(0.032, 0.032, 0.05), interp="LINEAR")


def ring(S, w, f, amp, decay=22.0, n=22, big=True, sound=True):
    """Campana: vaivén amortiguado (rotación en y), badajo en contrafase, rayitas de sonido y el cue."""
    for k in range(n):
        sg = 1 if k % 2 == 0 else -1; g = f + k * 3
        th = R(amp) * sg * math.exp(-(k * 3) / decay)
        S.key(w.bell, g, rot=(0, th, 0), interp="BEZIER")
        S.key(w.clapper, g + 1, rot=(0, -th * 1.8, 0), interp="BEZIER")
    S.key(w.bell, f + n * 3, rot=(0, 0, 0)); S.key(w.clapper, f + n * 3, rot=(0, 0, 0))
    m = mmat(S, "dling", (1.0, 0.9, 0.35), rough=0.3, emit=(1.0, 0.85, 0.2))
    zc = BZ - 0.33; rays = ((20, 0.44, 0.60), (48, 0.44, 0.60), (76, 0.44, 0.60)) if big else ((35, 0.40, 0.47),)
    for sx in (-1, 1):
        for (deg, r0, r1) in rays:
            ang = R(deg); c, s_ = math.cos(ang) * sx, math.sin(ang)
            ln = (r1 - r0) / 2
            o = S.obj("cube", "dling", "white", (BX, 0.05, zc), (0.001,) * 3, rot=(0, math.atan2(c, s_), 0), smooth=False); o.data.materials[0] = m
            p0 = (BX + c * (r0 + ln), 0.05, zc + s_ * (r0 + ln)); p1 = (BX + c * (r1 + ln + 0.05), 0.05, zc + s_ * (r1 + ln + 0.05))
            big_s = (0.012, 0.012, ln) if big else (0.008, 0.008, ln * 0.7)
            S.key(o, f, loc=p0, scale=(0.001,) * 3); S.key(o, f + 2, loc=p0, scale=big_s)
            S.key(o, f + 7, loc=p1, scale=big_s); S.key(o, f + 10, loc=p1, scale=(0.001,) * 3)
    if sound: S.cue("bell", f, vol=(-1 if big else -15))


# ------------------------------------------------------------------ nivel -450
def l1(S):
    """-450: ya saltando en el fotograma 1 con el brazo estirado bajo la campana; no llega; salta otra vez más fuerte, cae en cuclillas y la mira con rabia."""
    w = build_set(S); cam_static(S)
    x, y = BX - 0.05, -0.35
    a = MixamoActor(S, x=x, yaw=0, use=["Victory", "Jumping", "Angry"])
    # salto 1 (ya en el aire en el fotograma 1), cuclillas, salto 2 más alto, caída
    for f, z in ((1, 0.24), (3, 0.40), (5, 0.45), (8, 0.25), (11, 0.0), (20, 0.0), (22, 0.25), (26, 0.62), (28, 0.65), (31, 0.4), (34, 0.0)):
        place(S, a, f, x, y, z, 0)
    seg(S, a, "Victory", 1, 12, start=33)
    seg(S, a, "Jumping", 12, 24, start=41)
    seg(S, a, "Victory", 21, 36, start=33)
    seg(S, a, "Jumping", 33, 44, start=40)
    seg(S, a, "Angry", 42, None, start=0)
    S.cue("boing", 1, vol=-6); S.cue("clunk", 11, vol=-12); S.cue("boing", 21, vol=-4); S.cue("clunk", 34, vol=-5); S.cue("hit", 34, vol=-12)
    dust(S, x, y, 0.03, 34, n=6, spread=0.5, size=0.08, rise=0.25)
    dust(S, x, y, 0.03, 11, n=3, spread=0.3, size=0.05, rise=0.2)
    S.f = 106
    a.verify(S.f)
    return a


# ------------------------------------------------------------------ nivel -80
def l2(S):
    """-80: lanza su zapato (Throw); rebota en el poste y le cae en la cabeza; se desploma de espaldas sin llegar a la campana."""
    w = build_set(S); cam_static(S, cx=PX - 0.55)
    xc = PX - 0.85
    a = MixamoActor(S, x=xc, yaw=90, use=["Throw", "Falling Back Death"])
    place(S, a, 1, xc, 0, 0, 90)
    seg(S, a, "Throw", 1, 33, start=0)
    seg(S, a, "Falling Back Death", 32, None, start=0, blend=3)
    f_rel, f_pole, f_head = 20, 25, 33
    # el zapato va en la mano hasta soltarlo
    for f in range(1, f_rel + 1):
        p = bone_pos(S, a, "RightHand", f, 0.55)
        S.key(w.shoe, f, loc=(p.x, p.y, p.z), rot=(0, R(-20), 0), interp="LINEAR")
    p0 = bone_pos(S, a, "RightHand", f_rel, 0.55)
    hd = head_pos(S, a, f_head - 1)
    top = (hd.x + 0.02, 0.0, hd.z + 0.13)
    path = [(f_pole, (PX - 0.10, 0, 2.22), (0, R(-30), 0)),
            (f_pole + 4, (PX - 0.50, 0, 2.58), (0, R(-190), 0)),
            (f_head, top, (0, R(-340), 0)),
            (f_head + 3, (top[0] + 0.15, -0.05, top[2] + 0.30), (0, R(-420), 0)),
            (f_head + 8, (top[0] + 0.40, -0.12, 0.07), (0, R(-540), 0)),
            (f_head + 10, (top[0] + 0.46, -0.12, 0.16), (0, R(-575), 0)),
            (f_head + 13, (top[0] + 0.52, -0.12, 0.05), (0, R(-600), 0))]
    S.key(w.shoe, f_rel, loc=(p0.x, p0.y, p0.z), rot=(0, R(-60), 0), interp="LINEAR")
    for (f, loc, rot) in path: S.key(w.shoe, f, loc=loc, rot=rot, interp="LINEAR")
    S.cue("whoosh", f_rel - 2, vol=-9); S.cue("clunk", f_pole, vol=-3); S.cue("hit", f_head, vol=-8); S.cue("pop", f_head, vol=-5)
    S.cue("hit", f_head + 22, vol=-9); S.cue("clunk", f_head + 9, vol=-12)
    # estrellitas sobre la cabeza ya en el suelo
    hl = head_pos(S, a, f_head + 45)
    daze(S, hl, f_head + 40, n=44)
    dust(S, xc - 0.8, 0.0, 0.03, f_head + 24, n=6, spread=0.55, size=0.08, rise=0.2)
    S.f = 112
    a.verify(S.f)
    return a


# ------------------------------------------------------------------ nivel 120
def l3(S):
    """120: trepa el poste como por un muro (Climbing Up Wall); roza la campana con un dedo: dling mínimo; se agarra temblando."""
    w = build_set(S); cam_static(S, cx=PX - 0.1)
    xc = PX - 0.30
    a = MixamoActor(S, x=xc, yaw=90, use=["Climbing Up Wall"])
    place(S, a, 1, xc, 0, 0, 90)
    seg(S, a, "Climbing Up Wall", 1, None, start=0, speed=0.65)
    # al final del ascenso se estira hacia la campana (la campana está a la derecha del poste)
    place(S, a, 55, xc, 0, 0, 90); place(S, a, 64, xc + 0.14, 0, 0, 90)
    rr = random.Random(3)
    for f in range(66, 114, 2):                                    # tiembla agarrado al poste
        t = (f - 66) / 48.0
        place(S, a, f, xc + 0.14 + rr.uniform(-0.008, 0.008), 0, -0.14 * max(0.0, (t - 0.45) / 0.55) + rr.uniform(-0.007, 0.007), 90, "LINEAR")
    ft = 63
    ring(S, w, ft, amp=5.0, decay=14.0, n=9, big=False)            # dling mínimo
    S.cue("bell", ft, vol=-15)
    for f in (4, 14, 24, 34, 44):
        S.cue("creak", f, vol=-16)
    S.cue("slide_down", 90, vol=-14)
    # gotita de sudor
    hp = head_pos(S, a, 75)
    d = S.obj("uv_sphere", "sudor", "water", (hp.x, hp.y - 0.13, hp.z + 0.04), (0.001,) * 3, segments=8, ring_count=6)
    S.key(d, 73, loc=(hp.x, hp.y - 0.13, hp.z + 0.04), scale=(0.001,) * 3); S.key(d, 76, loc=(hp.x, hp.y - 0.13, hp.z + 0.03), scale=(0.025, 0.025, 0.036))
    S.key(d, 89, loc=(hp.x, hp.y - 0.13, hp.z - 0.35), scale=(0.022, 0.022, 0.04)); S.key(d, 92, loc=(hp.x, hp.y - 0.13, hp.z - 0.5), scale=(0.001,) * 3)
    S.f = 118
    a.verify(S.f)
    return a


# ------------------------------------------------------------------ nivel 900
def l4(S):
    """900 (sin cuerda, mejora del crítico): empuja la papelera bajo la campana, se sube de un salto y salta otra vez: dling a lo grande; se ríe."""
    w = build_set(S); cam_static(S, cx=PX - 0.45)
    by = -0.45
    x0 = BX - 1.93                                                 # raíz al empezar a empujar (la papelera, 1,08 m por delante)
    a = MixamoActor(S, x=x0, yaw=90, use=["Pushing", "Victory", "Jumping", "Laughing"])
    xr1 = BX - 1.08                                                # raíz al terminar de empujar
    S.key(w.bin, 1, loc=(x0 + 1.08, by, 0), interp="LINEAR"); S.key(w.bin, 37, loc=(BX, by, 0), interp="LINEAR")
    place(S, a, 1, x0, by, 0, 90, "LINEAR"); place(S, a, 33, xr1, by, 0, 90, "LINEAR")
    # salto heroico sobre la papelera (en el aire se gira a cámara), cuclillas, saltito con los brazos arriba, aterriza y se ríe
    zt = BIN_H
    for f, x, z, yaw in ((34, xr1, 0.0, 90), (37, xr1 + 0.35, 0.75, 70), (41, xr1 + 0.78, zt + 0.55, 40), (45, BX - 0.08, zt + 0.25, 15), (48, BX, zt, 0)):
        place(S, a, f, x, by, z, yaw)
    place(S, a, 56, BX, by, zt, 0)
    for f, z in ((58, zt + 0.12), (61, zt + 0.30), (64, zt + 0.10), (67, zt)):
        place(S, a, f, BX, by, z, 0)
    seg(S, a, "Pushing", 1, 35, start=0)
    seg(S, a, "Victory", 34, 50, start=33)
    seg(S, a, "Jumping", 48, 60, start=43)
    seg(S, a, "Victory", 57, 68, start=33)
    seg(S, a, "Laughing", 66, None, start=20)
    for f in range(4, 36, 8):
        S.cue("slide_down", f, vol=-16)
        dust(S, x0 + 1.08 + (f - 1) * (0.85 / 36) - 0.25, by, 0.03, f, n=2, spread=0.15, size=0.05, rise=0.12)
    S.cue("whoosh", 34, vol=-10); S.cue("boing", 34, vol=-6); S.cue("clunk", 48, vol=-4)
    dust(S, BX, by, zt, 48, n=4, spread=0.3, size=0.05, rise=0.15)
    S.cue("boing", 57, vol=-8)
    ring(S, w, 61, amp=24.0, decay=34.0, n=26, big=True)
    S.f = 118
    a.verify(S.f)
    return a


# ------------------------------------------------------------------ nivel 5469
def l5(S):
    """5469: se queda quieto y mira alrededor; ve la cuerda de tirar a ras de suelo (colgaba del gancho desde el principio); la recoge (Picking Up),
    tira: la campana suena fuerte; levanta los brazos y suelta la cuerda, que vuelve al suelo."""
    w = build_set(S, rope=True); cam_static(S, cx=PX - 0.1)
    ry = RY + 0.05
    xr = KX + 0.50
    a = MixamoActor(S, x=xr, yaw=-90, use=["Looking Around", "Picking Up", "Victory"])
    place(S, a, 1, xr, ry, 0, -90)
    speed = 1.8
    seg(S, a, "Looking Around", 1, 30, start=0)
    seg(S, a, "Picking Up", 28, 92, start=22, speed=speed)
    seg(S, a, "Victory", 90, None, start=12)
    fp = int(28 + (57 - 22) / speed)                               # fotograma en que la mano está más abajo (coge la cuerda)
    hp = bone_pos(S, a, "RightHand", fp, 0.8)
    dx, dy = w.K0.x - hp.x, w.K0.y - hp.y
    place(S, a, 1, xr + dx, ry + dy, 0, -90)                       # coloca al personaje para que su mano alcance el tirador
    # tirador: quieto en el suelo hasta fp; luego sigue a la mano; tirón; suelta y vuelve al suelo
    f_tug, f_rel = 84, 94
    # plano corto de la cuerda enrollada en el suelo, detrás del poste (mientras mira alrededor)
    cam, tg, ln = S.cam, S.tgt, S.cam.data
    for f, loc, tl, lens in ((12, (PX + 1.0, -2.4, 0.8), (PX + 0.25, 0.5, 0.2), 44), (31, (PX - 0.1, -6.5, 2.05), (PX - 0.1, 0, 2.0), 44)):
        cam.location = loc; cam.keyframe_insert("location", frame=f); ln.lens = lens; ln.keyframe_insert("lens", frame=f)
        tg.location = tl; tg.keyframe_insert("location", frame=f)
    S.set_interp(cam, "CONSTANT", ("location",)); S.set_interp(ln, "CONSTANT"); S.set_interp(tg, "CONSTANT")
    S.key(w.coil, fp - 1, scale=(1, 1, 1)); S.key(w.coil, fp, scale=(0.001,) * 3)             # la recoge: el montón desaparece
    S.key(w.rope, fp - 2, scale=(0.001,) * 3); S.key(w.toggle, fp - 2, scale=(0.001,) * 3)
    rope_set(S, w, fp - 1, w.K0)
    for f in range(fp, f_tug):
        p = bone_pos(S, a, "RightHand", f, 0.8)
        rope_set(S, w, f, (p.x, p.y, p.z))
    p = bone_pos(S, a, "RightHand", f_tug, 0.8)
    for f in range(f_tug, f_rel):
        p = bone_pos(S, a, "RightHand", f, 0.8)
        k = max(0.0, 1 - abs(f - f_tug - 2) / 3.0)                 # tirón hacia abajo de 3 fotogramas
        rope_set(S, w, f, (p.x, p.y, p.z - 0.22 * k))
    rope_set(S, w, f_rel, (p.x, p.y, p.z)); rope_set(S, w, f_rel + 5, (w.K0.x + 0.03, w.K0.y, 0.55)); rope_set(S, w, f_rel + 9, w.K0)
    rope_set(S, w, f_rel + 13, (w.K0.x - 0.02, w.K0.y, 0.30)); rope_set(S, w, f_rel + 17, w.K0)
    for f in (f_tug - 1, f_tug, f_tug + 1, f_tug + 2):             # el cuerpo cede con el tirón
        place(S, a, f, xr + dx, ry + dy, -0.05 if f in (f_tug, f_tug + 1) else 0.0, -90)
    S.cue("pop", fp, vol=-12); S.cue("creak", f_tug - 2, vol=-10)
    ring(S, w, f_tug + 1, amp=26.0, decay=36.0, n=28, big=True)
    S.cue("tada", f_rel + 2, vol=-10)
    S.f = 140
    a.verify(S.f)
    return a


LEVELS = [(-450, l1), (-80, l2), (120, l3), (900, l4), (5469, l5)]
