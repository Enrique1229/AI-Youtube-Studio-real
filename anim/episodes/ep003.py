"""ep003 — Objetos vivos: un huevo sonámbulo camina hasta el borde de la encimera y cae; un huevero lo atrapa (sin diálogo, sin rótulo)."""
import math
import bpy
import bmesh

TITLE = "The Sleepwalking Egg"
CAPTION = None
SPEED = 1.0
CTA = "follow for more"
ENV = "mesa"
CUSTOM_CAMERA = True

EDGE = 1.0            # x del borde de la encimera
FLOOR = -1.0          # z del suelo
ZS = 0.216            # z del centro del huevo de pie
SPX = 0.82            # x de la cuchara
LAND_X = 1.17         # x del huevero (y de aterrizaje)
F_WALK0, F_WALK1 = 30, 196
F_FALL = 208          # empieza a caer
F_LAND = 245
JAR_X = 1.38


def rad(d): return math.radians(d)


# ---------------------------------------------------------------- cara (copiada de ep002) y utilidades
def mkface(S, parent, k=1.0, gap=0.055):
    r = 0.034 * k; P = {"lids": [], "pupils": [], "brows": []}
    P["root"] = S.empty("cara", parent=parent)
    for sx in (-1, 1):
        S.obj("uv_sphere", "ojo", "white", (gap * k * sx, 0, 0), (r, r * 0.7, r * 1.15), parent=P["root"], segments=16, ring_count=10)
        P["pupils"].append(S.obj("uv_sphere", "pupila", "black", (gap * k * sx, -r * 0.55, 0), (r * 0.5, r * 0.25, r * 0.55), parent=P["root"], segments=12, ring_count=8))
        lid = S.obj("uv_sphere", "parpado", "foam", (gap * k * sx, -r * 0.1, r * 0.5), (r * 1.1, r * 0.8, 0.001), parent=P["root"], segments=16, ring_count=10)
        P["lids"].append((lid, r))
        P["brows"].append(S.obj("cube", "ceja", "black", (gap * k * sx, -r * 0.5, r * 1.7), (r * 1.0, 0.007 * k, 0.008 * k), parent=P["root"], smooth=False))
    P["mouth"] = S.obj("uv_sphere", "boca", "black", (0, -0.002 * k, -r * 2.6), (0.03 * k, 0.008 * k, 0.006 * k), parent=P["root"], segments=16, ring_count=8)
    P["k"] = k; P["r"] = r; P["gap"] = gap * k
    return P


def half_ring(S, parent, loc, major, minor, name="arco"):
    """Medio aro inferior (‿) mirando a cámara."""
    bpy.ops.mesh.primitive_torus_add(major_radius=major, minor_radius=minor, major_segments=24, minor_segments=8, location=loc, rotation=(rad(90), 0, 0))
    o = bpy.context.object; o.name = name; o.parent = parent; o.data.materials.append(S.mat("black"))
    bm = bmesh.new(); bm.from_mesh(o.data)
    bmesh.ops.delete(bm, geom=[v for v in bm.verts if v.co.y > 0.0005], context="VERTS")
    bm.to_mesh(o.data); bm.free()
    for p in o.data.polygons: p.use_smooth = True
    return o


def sleepface(S, parent, k=1.0, gap=0.055):
    """Cara dormida: ojos cerrados en arco, cejas relajadas, boca pequeña (ronca), sonrisa oculta."""
    r = 0.034 * k; P = {"brows": [], "arcs": []}
    P["root"] = S.empty("cara", parent=parent)
    for sx in (-1, 1):
        P["arcs"].append(half_ring(S, P["root"], (gap * k * sx, -r * 0.2, r * 0.25), r * 0.8, 0.005 * k, "ojo_cerrado"))
        P["brows"].append(S.obj("cube", "ceja", "black", (gap * k * sx, -r * 0.5, r * 2.1), (r * 0.95, 0.006 * k, 0.007 * k), rot=(0, rad(14 * sx), 0), parent=P["root"], smooth=False))
    P["mouth"] = S.obj("uv_sphere", "boca", "black", (0, -0.002 * k, -r * 2.2), (0.016 * k, 0.006 * k, 0.005 * k), parent=P["root"], segments=16, ring_count=8)
    P["k"] = k; P["r"] = r; P["gap"] = gap * k
    P["smile"] = add_smile(S, P)
    return P


def add_smile(S, P):
    k, r = P["k"], P["r"]
    sm = half_ring(S, P["root"], (0, -0.004 * k, -r * 1.7), 0.026 * k, 0.0045 * k, "sonrisa")
    S.key(sm, 1, scale=(0.001,) * 3)
    return sm


def smile_at(S, P, f, on=True, interp="BACK"):
    """Cambia la boca (óvalo) por la sonrisa en arco."""
    sm = P["smile"]
    if on:
        S.key(P["mouth"], f - 1, scale=tuple(P["mouth"].scale)); S.key(P["mouth"], f, scale=(0.001,) * 3)
        S.key(sm, f - 1, scale=(0.001,) * 3); S.key(sm, f + 3, scale=(1, 1, 1), interp=interp)
    else:
        S.key(sm, f, scale=(0.001,) * 3)


def brows_set(S, P, f, deg):
    for sx, b in zip((-1, 1), P["brows"]): S.key(b, f, rot=(0, rad(deg * sx), 0))


def face_mood(S, P, f, mood):
    k = P["k"]
    mo = {"smile": ((0.034, 0.008, 0.015), 4), "neutral": ((0.02, 0.006, 0.005), 6), "wide": ((0.012, 0.007, 0.012), 16),
          "worry": ((0.018, 0.006, 0.006), 14), "oh": ((0.012, 0.007, 0.014), 14)}[mood]
    S.key(P["mouth"], f, scale=tuple(v * k for v in mo[0]))
    for sx, b in zip((-1, 1), P["brows"]): S.key(b, f, rot=(0, rad(mo[1] * sx), 0))


def face_blink(S, P, f, hold=0, only=None):
    for i, (lid, r) in enumerate(P["lids"]):
        if only is not None and i != only: continue
        lx, ly = r * 1.1, r * 0.8
        S.key(lid, f - 1, scale=(lx, ly, 0.001)); S.key(lid, f + 1, scale=(lx, ly, r * 1.1))
        S.key(lid, f + 3 + hold, scale=(lx, ly, r * 1.1)); S.key(lid, f + 5 + hold, scale=(lx, ly, 0.001))


def face_look(S, P, f, dx, dz=0.0):
    r = P["r"]
    for sx, p in zip((-1, 1), P["pupils"]): S.key(p, f, loc=(P["gap"] * sx + dx, -r * 0.55, dz))


def _kps(o):
    ad = o.animation_data
    if not ad or not ad.action: return
    act = ad.action
    fcs = list(act.fcurves) if hasattr(act, "fcurves") else [fc for l in act.layers for st in l.strips for cb in st.channelbags for fc in cb.fcurves]
    for fc in fcs:
        if fc.data_path == "location": yield from fc.keyframe_points


def shot(S, f, x, z, d=0.85, tz=None, interp="CONSTANT"):
    S.key(S.cam, f, loc=(x, -d * 1.75, z), interp=interp)
    S.key(S.tgt, f, loc=(x, 0, z if tz is None else tz), interp=interp)
    for o in (S.cam, S.tgt):
        for kp in _kps(o):
            if int(round(kp.co[0])) == f: kp.interpolation = interp


def O(S, prim, name, mat, loc, scale=(1, 1, 1), rot=(0, 0, 0), parent=None, smooth=True, **kw):
    o = S.obj(prim, name, "white", loc, scale, rot, parent, smooth, **kw); o.data.materials[0] = mat; return o


def hop(S, o, x1, f0, dur=9, h=0.07, y=None, z0=0.0):
    x0 = o.location.x
    yy = o.location.y if y is None else y
    S.key(o, f0, loc=(x0, yy, z0)); S.key(o, f0 + 2, loc=(x0, yy, z0), scale=(1.06, 1.0, 0.92))
    S.key(o, f0 + 2 + dur // 2, loc=((x0 + x1) / 2, yy, z0 + h), scale=(0.97, 1, 1.05))
    S.key(o, f0 + 2 + dur, loc=(x1, yy, z0), scale=(1.05, 1.0, 0.93)); S.key(o, f0 + 5 + dur, loc=(x1, yy, z0), scale=(1, 1, 1))
    S.cue("boing", f0 + 2 + dur, vol=-9)
    o.location = (x1, yy, z0)


# ---------------------------------------------------------------- nivel
def l1(S):
    S.cam.data.dof.aperture_fstop = 5.0; S.cam.data.dof.focus_object = S.tgt
    # --- materiales ---
    shell = S.pmat("cascara", [(0.3, (0.90, 0.80, 0.64)), (0.7, (0.96, 0.89, 0.76))], scale=14, rough=0.7, bump=0.04)
    shell2 = S.pmat("cascara2", [(0.3, (0.86, 0.75, 0.60)), (0.7, (0.92, 0.83, 0.70))], scale=10, rough=0.7, bump=0.03)   # extremidades, algo más oscuras
    shoe = S.pmat("zapato", [(0.3, (0.55, 0.30, 0.15)), (0.7, (0.65, 0.38, 0.20))], scale=6, rough=0.6, bump=0.0)
    ceramic = S.pmat("ceramica", [(0.3, (0.18, 0.40, 0.72)), (0.7, (0.30, 0.55, 0.85))], scale=3, rough=0.12, bump=0.0)
    steel = S.pmat("acero", [(0.3, (0.70, 0.72, 0.76)), (0.7, (0.85, 0.87, 0.90))], scale=4, rough=0.25, bump=0.0)
    steel.node_tree.nodes["Principled BSDF"].inputs["Metallic"].default_value = 0.35
    terra = S.pmat("terracota", [(0.3, (0.62, 0.30, 0.17)), (0.7, (0.75, 0.40, 0.22))], scale=8, rough=0.55, bump=0.1)
    mug = S.pmat("taza", [(0.3, (0.88, 0.66, 0.18)), (0.7, (0.95, 0.76, 0.28))], scale=3, rough=0.2, bump=0.0)
    glass = S.pmat("sal", [(0.3, (0.88, 0.90, 0.92)), (0.7, (0.97, 0.97, 0.98))], scale=4, rough=0.15, bump=0.0)
    tile = S.pmat("baldosa", [(0.3, (0.22, 0.20, 0.19)), (0.7, (0.32, 0.29, 0.27))], scale=5, rough=0.4, bump=0.05)
    cabm = S.pmat("mueble", [(0.3, (0.30, 0.20, 0.13)), (0.7, (0.40, 0.28, 0.18))], scale=9, rough=0.5, bump=0.15)
    bubm = S.pmat("burbuja", [(0.3, (0.82, 0.92, 1.0)), (0.7, (1.0, 1.0, 1.0))], scale=3, rough=0.1, bump=0.0, alpha=0.3)

    # --- escenario: borde de encimera, mueble, suelo ---
    top = bpy.data.objects["encimera"]; top.location.x = EDGE - 6.0                         # la encimera acaba en x = EDGE
    O(S, "cube", "mueble", cabm, (EDGE - 0.03 - 6.0, 0, (FLOOR - 0.1) / 2 - 0.05), (6, 2.9, (-0.1 - FLOOR) / 2), smooth=False)
    O(S, "cube", "suelo", tile, (0, 0, FLOOR - 0.05), (8, 6, 0.05), smooth=False)
    O(S, "cube", "pared_baja", cabm, (0, 3.2, FLOOR / 2 - 0.05), (8, 0.1, -FLOOR / 2 + 0.05), smooth=False)
    li = bpy.data.objects.new("foco_bajo", bpy.data.lights.new("foco_bajo", "AREA")); S.sc.collection.objects.link(li)
    li.location = (1.2, -1.0, -0.3); li.rotation_euler = (rad(90), 0, 0); li.data.energy = 30; li.data.size = 1.5; li.data.color = (1.0, 0.85, 0.65)

    lf = bpy.data.objects.new("relleno", bpy.data.lights.new("relleno", "AREA")); S.sc.collection.objects.link(lf)
    lf.location = (0.4, -1.6, 1.0); lf.rotation_euler = (rad(65), 0, 0); lf.data.energy = 10; lf.data.size = 1.5; lf.data.color = (1.0, 0.92, 0.8)

    # --- objetos de la encimera (al fondo) ---
    O(S, "cylinder", "taza", mug, (0.30, 0.14, 0.055), radius=0.075, depth=0.11, vertices=48, smooth=False)
    O(S, "cylinder", "cafe", S.mat("brown"), (0.30, 0.14, 0.108), radius=0.066, depth=0.01, vertices=48, smooth=False)
    O(S, "torus", "asa", mug, (0.385, 0.14, 0.06), rot=(rad(90), 0, 0), major_radius=0.035, minor_radius=0.011, major_segments=24, minor_segments=8)
    O(S, "cylinder", "sal", glass, (0.64, 0.11, 0.065), radius=0.042, depth=0.13, vertices=40, smooth=False)
    O(S, "cylinder", "sal_tapa", steel, (0.64, 0.11, 0.14), radius=0.044, depth=0.028, vertices=40, smooth=False)

    # --- tarro y huevero en el suelo ---
    O(S, "cylinder", "tarro", terra, (JAR_X, 0.0, FLOOR + 0.25), radius=0.11, depth=0.5, vertices=48, smooth=False)
    O(S, "cylinder", "tarro_tapa", terra, (JAR_X, 0.0, FLOOR + 0.52), radius=0.12, depth=0.05, vertices=48, smooth=False)
    hv = S.empty("huevero", (JAR_X, 0.19, FLOOR))
    O(S, "cylinder", "pie_h", ceramic, (0, 0, 0.01), radius=0.11, depth=0.02, vertices=48, parent=hv, smooth=False)
    O(S, "cylinder", "tallo_h", ceramic, (0, 0, 0.045), radius=0.045, depth=0.05, vertices=48, parent=hv, smooth=False)
    O(S, "cone", "copa_h", ceramic, (0, 0, 0.15), parent=hv, radius1=0.08, radius2=0.115, depth=0.16, vertices=48, smooth=False)
    hf = mkface(S, hv, 0.85); hf["root"].location = (0, -0.103, 0.152)
    face_mood(S, hf, 1, "neutral"); hf["smile"] = add_smile(S, hf); smile_at(S, hf, 2)
    face_look(S, hf, 1, 0.0, 0.0)

    # --- cuchara (con cara) ---
    sp = S.empty("cuchara", (SPX, 0.12, 0.0))
    O(S, "cylinder", "mango", steel, (0, 0, 0.25), radius=0.014, depth=0.50, vertices=24, parent=sp)
    O(S, "uv_sphere", "cazo", steel, (0, 0, 0.53), (0.09, 0.018, 0.12), parent=sp, segments=40, ring_count=24)
    sf = mkface(S, sp, 0.85); sf["root"].location = (0, -0.012, 0.53)
    hands = []
    for sx in (-1, 1):
        h_ = O(S, "uv_sphere", "mano", S.mat("coral"), (0.14 * sx, -0.03, 0.40), (0.032,) * 3, parent=sp)
        hands.append((h_, sx))
    sf["smile"] = add_smile(S, sf)
    face_mood(S, sf, 1, "neutral"); face_look(S, sf, 1, 0.0, 0.0)

    # --- el huevo ---
    egg = S.empty("huevo", (0.05, 0, ZS))
    O(S, "uv_sphere", "cascara", shell, (0, 0, 0), (0.105, 0.10, 0.13), parent=egg, segments=48, ring_count=28)
    ef = sleepface(S, egg, 0.95); ef["root"].location = (0, -0.095, 0.03)
    hips = []
    for sx in (-1, 1):
        hip = S.empty("cadera", (0.045 * sx, 0, -0.125), parent=egg)
        O(S, "cylinder", "pierna", shell2, (0, 0, -0.04), radius=0.016, depth=0.08, vertices=16, parent=hip)
        O(S, "uv_sphere", "pie", shoe, (0, -0.012, -0.078), (0.03, 0.04, 0.017), parent=hip, segments=20, ring_count=12)
        hips.append(hip)
    arms = []
    for (ay, az) in ((-0.03, 0.012), (0.012, -0.04)):
        sh = S.empty("hombro", (0.06, ay, az), parent=egg)
        O(S, "cylinder", "brazo", shell2, (0.11, 0, 0), rot=(0, rad(90), 0), radius=0.014, depth=0.22, vertices=16, parent=sh)
        O(S, "uv_sphere", "mano", shell2, (0.23, 0, 0), (0.026, 0.026, 0.026), parent=sh, segments=16, ring_count=10)
        arms.append(sh)
    bub = O(S, "uv_sphere", "burbuja", bubm, (-0.125, -0.10, -0.03), (0.001,) * 3, parent=egg, segments=24, ring_count=14)
    S.key(bub, 1, scale=(0.001,) * 3)

    def bubble(f0, r, dur):
        S.key(bub, f0, scale=(0.001,) * 3); S.key(bub, f0 + int(dur * 0.65), scale=(r,) * 3); S.key(bub, f0 + dur, scale=(0.001,) * 3)

    # --- cámara: cortes entre planos cerrados ---
    S.cam.data.lens = 50; S.cam.data.keyframe_insert("lens", frame=1)
    shot(S, 1, 0.10, 0.24, d=0.78)                         # gancho: huevo dormido, brazos estirados
    shot(S, 30, 0.52, 0.05, d=1.7)                         # abierto (1 s): el borde y el vacío
    shot(S, 54, 0.22, 0.24, d=0.8, interp="LINEAR")        # sigue al huevo entre la taza y la sal
    shot(S, 97, 0.43, 0.24, d=0.8)
    shot(S, 98, 0.66, 0.31, d=1.0)                        # la cuchara ve acercarse al huevo
    shot(S, 150, 0.80, 0.32, d=0.82, interp="LINEAR")      # el huevo llega al borde
    shot(S, F_WALK1, 0.99, 0.32, d=0.82)
    shot(S, 212, 1.08, 0.50, d=0.55)                       # primer plano de la cuchara: mira a cámara y se tapa los ojos
    shot(S, 230, LAND_X, -0.62, d=0.95)                    # cámara baja: caída en silencio y huevero
    shot(S, 300, 0.95, 0.46, d=0.68)                       # la cuchara celebra
    shot(S, 330, LAND_X + 0.04, -0.60, d=0.78)             # final: el huevo duerme en el huevero

    # --- 0-1 s: gancho, el huevo se balancea dormido ---
    for f in range(1, 31, 3):
        s = math.sin((f - 1) / 24 * 2 * math.pi)
        S.key(egg, f, loc=(0.05, 0, ZS), rot=(0, rad(5 * s), 0))
    for h_ in arms: S.key(h_, 1, rot=(0, 0, 0))
    for hp in hips: S.key(hp, 1, rot=(0, 0, 0))
    brows_set(S, ef, 1, 14)
    S.cue("creak", 6, vol=-8); bubble(4, 0.03, 22)
    S.key(ef["mouth"], 4, scale=(0.016 * 0.95, 0.006 * 0.95, 0.005 * 0.95))
    S.key(ef["mouth"], 10, scale=(0.016 * 0.95, 0.007 * 0.95, 0.012 * 0.95)); S.key(ef["mouth"], 22, scale=(0.016 * 0.95, 0.006 * 0.95, 0.005 * 0.95))

    # --- 1-8 s: sonámbulo, camina hacia el borde ---
    wx = lambda f: 0.05 + (0.93 - 0.05) * (f - F_WALK0) / (F_WALK1 - F_WALK0)
    n = (F_WALK1 - F_WALK0) // 6
    for j in range(n + 1):
        f = F_WALK0 + 6 * j
        S.key(egg, f, loc=(wx(f), 0, ZS + (0.012 if j % 2 else 0.0)), rot=(0, rad(3 if j % 2 else -2), 0), interp="LINEAR")
        a = (-26, 0, 26, 0)[j % 4]
        S.key(hips[1], f, rot=(0, rad(a), 0)); S.key(hips[0], f, rot=(0, rad(-a), 0))
        for ai, h_ in enumerate(arms):
            S.key(h_, f, rot=(0, rad((4 if (j // 2 + ai) % 2 else -4)), 0))
    for f, r_ in ((62, 0.028), (104, 0.03), (146, 0.03)):
        S.cue("creak", f, vol=-9); bubble(f - 2, r_, 24)
        S.key(ef["mouth"], f - 2, scale=(0.016 * 0.95, 0.006 * 0.95, 0.005 * 0.95)); S.key(ef["mouth"], f + 6, scale=(0.016 * 0.95, 0.007 * 0.95, 0.012 * 0.95))
        S.key(ef["mouth"], f + 20, scale=(0.016 * 0.95, 0.006 * 0.95, 0.005 * 0.95))

    # cuchara: aburrida, ve venir al huevo y se asusta
    for f in (118, 138):
        for lid, r in sf["lids"]: pass
    face_blink(S, sf, 118)
    face_look(S, sf, 98, 0.0, 0.0); face_look(S, sf, 128, -0.03, 0.0)
    face_mood(S, sf, 128, "neutral")
    face_look(S, sf, 146, -0.03, 0.0); face_mood(S, sf, 152, "wide"); face_look(S, sf, 160, 0.03, 0.0)
    face_blink(S, sf, 134)
    S.key(sp, 1, loc=(SPX, 0.12, 0.0)); S.key(sp, 150, loc=(SPX, 0.12, 0.0), rot=(0, 0, 0))
    S.key(sp, 153, loc=(SPX, 0.12, 0.02), rot=(0, rad(-6), 0), scale=(0.96, 1, 1.06))               # se sobresalta
    S.key(sp, 158, loc=(SPX, 0.12, 0.0), rot=(0, 0, 0), scale=(1, 1, 1))
    S.f = 174; hop(S, sp, 0.90, 174, dur=9, h=0.07); hop(S, sp, 0.97, 188, dur=8, h=0.06)
    face_mood(S, sf, 176, "wide"); face_look(S, sf, 176, 0.03, 0.0)

    # --- el pie en el aire (duda), la cuchara se lanza y falla ---
    S.key(egg, F_WALK1 + 2, loc=(0.95, 0, ZS), rot=(0, rad(3), 0), interp="LINEAR")
    S.key(hips[1], F_WALK1, rot=(0, rad(-10), 0)); S.key(hips[1], F_WALK1 + 5, rot=(0, rad(-58), 0), interp="BACK")
    S.key(hips[0], F_WALK1 + 5, rot=(0, rad(8), 0))
    S.key(egg, F_WALK1 + 8, loc=(0.99, 0, ZS), rot=(0, rad(6), 0), interp="BEZIER")
    S.key(egg, F_FALL - 1, loc=(1.01, 0, ZS), rot=(0, rad(8), 0))
    S.key(hips[1], F_FALL, rot=(0, rad(-58), 0))
    S.key(sp, 198, loc=(0.97, 0.12, 0.0), rot=(0, 0, 0)); S.key(sp, 201, loc=(0.97, 0.12, 0.0), rot=(0, rad(-8), 0))   # anticipación
    S.key(sp, 206, loc=(0.97, 0.12, 0.0), rot=(0, rad(18), 0), interp="BACK")                                      # se lanza
    S.key(sp, 220, loc=(0.97, 0.12, 0.0), rot=(0, rad(22), 0)); S.key(sp, 228, loc=(0.97, 0.12, 0.0), rot=(0, rad(8), 0))
    S.key(sp, 240, loc=(0.97, 0.12, 0.0), rot=(0, 0, 0))
    S.cue("whoosh", 204, vol=-8)
    face_mood(S, sf, 202, "oh")
    face_look(S, sf, 212, 0.0, 0.0)                                                                    # mira a cámara
    for hnd, sx in hands:                                                                              # se tapa los ojos
        S.key(hnd, 213, loc=(0.15 * sx, -0.03, 0.44), scale=(0.001,) * 3)
        S.key(hnd, 216, loc=(0.12 * sx, -0.03, 0.44), scale=(0.032,) * 3)
        S.key(hnd, 222, loc=(0.047 * sx, -0.045, 0.53), scale=(0.037, 0.032, 0.037), interp="BACK")
        S.key(hnd, 292, loc=(0.047 * sx, -0.045, 0.53), scale=(0.037, 0.032, 0.037))
        S.key(hnd, 298, loc=(0.16 * sx, -0.03, 0.50), scale=(0.032,) * 3)
        S.key(hnd, 304, loc=(0.14 * sx, -0.03, 0.58), scale=(0.032,) * 3, interp="BACK")
        S.key(hnd, 328, loc=(0.14 * sx, -0.03, 0.56), scale=(0.032,) * 3)
        S.key(hnd, 334, loc=(0.15 * sx, -0.03, 0.40), scale=(0.001,) * 3)
    S.cue("pop", 221, vol=-8)

    # --- 8-10 s: caída libre (silencio); el huevo no se entera ---
    c = (ZS - (FLOOR + 0.30)) / (37 / 24) ** 2
    for k_ in range(0, 38, 3):
        f = F_FALL + k_
        t = k_ / 24
        S.key(egg, f, loc=(1.03 + (LAND_X - 1.03) * (k_ / 37), 0, ZS - c * t * t), rot=(0, rad(8 + 14 * math.sin(k_ / 37 * math.pi * 0.9)), 0))
    for h_ in arms: S.key(h_, F_FALL + 4, rot=(0, rad(-5), 0)); S.key(h_, F_FALL + 14, rot=(0, rad(-58), 0), interp="BACK")
    arms_a, arms_b = arms
    for f in range(F_FALL + 6, F_LAND, 8):
        S.key(hips[0], f, rot=(0, rad(28 if (f // 8) % 2 else -22), 0)); S.key(hips[1], f, rot=(0, rad(-22 if (f // 8) % 2 else 28), 0))
    # huevero asoma en el último medio segundo
    S.key(hv, F_LAND - 13, loc=(JAR_X, 0.19, FLOOR), scale=(1, 1, 1))
    S.key(hv, F_LAND - 11, loc=(JAR_X + 0.02, 0.19, FLOOR), scale=(1.03, 1, 0.94))
    S.key(hv, F_LAND - 2, loc=(LAND_X, 0.0, FLOOR), scale=(0.97, 1, 1.05), interp="BEZIER")
    S.key(hv, F_LAND, loc=(LAND_X, 0.0, FLOOR), scale=(1, 1, 1))
    face_blink(S, hf, F_LAND - 9, only=1)                                                               # guiño
    face_look(S, hf, F_LAND - 12, 0.0, 0.025); face_look(S, hf, F_LAND - 3, 0.0, 0.03)

    # --- 10-12 s: aterriza en el huevero, boing, se acomoda, sonríe, ronca ---
    S.cue("boing", F_LAND, vol=-1)
    S.key(egg, F_LAND, loc=(LAND_X, 0, FLOOR + 0.30 - 0.0), rot=(0, rad(4), 0), scale=(1, 1, 1))
    S.key(egg, F_LAND + 2, loc=(LAND_X, 0, FLOOR + 0.265), rot=(0, rad(-6), 0), scale=(1.1, 1.08, 0.86))
    S.key(egg, F_LAND + 7, loc=(LAND_X, 0, FLOOR + 0.325), rot=(0, rad(5), 0), scale=(0.96, 0.96, 1.06))
    S.key(egg, F_LAND + 13, loc=(LAND_X, 0, FLOOR + 0.295), rot=(0, rad(-4), 0), scale=(1.02, 1.02, 0.98))
    S.key(egg, F_LAND + 20, loc=(LAND_X, 0, FLOOR + 0.30), rot=(0, rad(1), 0), scale=(1, 1, 1))
    S.key(egg, F_LAND + 32, loc=(LAND_X, 0, FLOOR + 0.30), rot=(0, rad(-1.5), 0))
    S.key(hv, F_LAND + 2, loc=(LAND_X, 0.0, FLOOR), scale=(1.07, 1.05, 0.88))
    S.key(hv, F_LAND + 9, loc=(LAND_X, 0.0, FLOOR), scale=(0.98, 0.98, 1.03)); S.key(hv, F_LAND + 15, loc=(LAND_X, 0.0, FLOOR), scale=(1, 1, 1))
    for h_ in arms:
        S.key(h_, F_LAND - 1, rot=(0, rad(-58), 0)); S.key(h_, F_LAND + 8, rot=(0, rad(88), 0), interp="BACK"); S.key(h_, F_LAND + 40, rot=(0, rad(88), 0))
    for hp in hips: S.key(hp, F_LAND - 1, rot=(0, 0, 0))
    for h_ in arms: S.key(h_, F_LAND + 8, scale=(1, 1, 1)); S.key(h_, F_LAND + 15, scale=(0.001,) * 3)       # los brazos se recogen dentro del huevero
    smile_at(S, ef, F_LAND + 14)
    brows_set(S, ef, F_LAND + 14, 12)
    smile_at(S, hf, F_LAND + 2)
    face_blink(S, hf, F_LAND + 24, only=1); face_look(S, hf, F_LAND + 12, 0.0, 0.0)
    S.cue("creak", 270, vol=-9)
    bub.name = "burbuja_final"
    S.key(bub, 254, scale=(0.001,) * 3); S.key(bub, 290, scale=(0.055,) * 3); S.key(bub, 297, scale=(0.045,) * 3); S.key(bub, 300, scale=(0.045,) * 3)

    # --- 12-14 s: la cuchara celebra desde el borde ---
    S.key(ef["mouth"], 232, scale=(0.001,) * 3)
    smile_at(S, sf, 297); brows_set(S, sf, 297, 8)
    S.key(sp, 296, loc=(0.97, 0.12, 0.0), rot=(0, 0, 0), scale=(1, 1, 1))
    hop(S, sp, 0.97, 300, dur=8, h=0.09); hop(S, sp, 0.97, 314, dur=8, h=0.09)
    face_look(S, sf, 300, 0.0, 0.0); face_blink(S, sf, 322)
    S.cue("tada", 301, vol=-3)

    # --- 14-16 s: final, el huevo ronca otra vez (enlaza con el gancho) ---
    S.key(bub, 334, scale=(0.045,) * 3); S.key(bub, 346, scale=(0.078,) * 3); S.key(bub, 349, scale=(0.001,) * 3)
    S.cue("creak", 336, vol=-9); S.cue("pop", 349, vol=-5)
    face_blink(S, hf, 346, only=1)
    S.key(egg, 330, loc=(LAND_X, 0, FLOOR + 0.30), rot=(0, rad(-1.5), 0)); S.key(egg, 372, loc=(LAND_X, 0, FLOOR + 0.30), rot=(0, rad(1.5), 0))
    S.f = 372
    return egg


LEVELS = [(0, l1)]
