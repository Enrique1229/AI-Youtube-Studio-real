"""ep007 — Objetos vivos: una mantequilla con cara cae en una sartén caliente, descubre que patina, esquiva un molinillo de pimienta,
se derrite en un charco liso y acaba cubriendo una tortita, que sonríe (sin diálogo, sin rótulo)."""
import math
import bpy
import bmesh

TITLE = "The Butter Who Learned to Skate"
CAPTION = "This butter wants to skate"   # premisa fija arriba
SPEED = 1.0
CTA = "follow for more"
ENV = "mesa"
CUSTOM_CAMERA = True

PAN_X = 0.05          # centro de la sartén
PZ = 0.03             # z del fondo de la sartén
CX, CY = -0.15, 0.08  # centro de la órbita (y del molinillo)
RX, RY = 0.22, 0.16
PK_X = 0.30           # x de la tortita
PK_H = 0.17           # altura de la tortita
F_O0, F_O1 = 4, 130   # órbita
F_POSE0, F_D, F_PK, F_E, F_FIN = 131, 173, 225, 259, 323
F_END = 408
TH0, TH1 = math.pi, 3.5 * math.pi


def rad(d): return math.radians(d)


# ---------------------------------------------------------------- caras
def mkface(S, parent, k=1.0, gap=0.055):
    r = 0.034 * k; P = {"lids": [], "pupils": [], "brows": [], "eyes": []}
    P["root"] = S.empty("cara", parent=parent)
    for sx in (-1, 1):
        P["eyes"].append(S.obj("uv_sphere", "ojo", "white", (gap * k * sx, 0, 0), (r, r * 0.7, r * 1.15), parent=P["root"], segments=16, ring_count=10))
        P["pupils"].append(S.obj("uv_sphere", "pupila", "black", (gap * k * sx, -r * 0.55, 0), (r * 0.5, r * 0.25, r * 0.55), parent=P["root"], segments=12, ring_count=8))
        lid = S.obj("uv_sphere", "parpado", "foam", (gap * k * sx, -r * 0.1, r * 0.5), (r * 1.1, r * 0.8, 0.001), parent=P["root"], segments=16, ring_count=10)
        P["lids"].append((lid, r))
        P["brows"].append(S.obj("cube", "ceja", "black", (gap * k * sx, -r * 0.5, r * 1.7), (r * 1.0, 0.007 * k, 0.008 * k), parent=P["root"], smooth=False))
    P["mouth"] = S.obj("uv_sphere", "boca", "black", (0, -0.002 * k, -r * 2.6), (0.03 * k, 0.008 * k, 0.006 * k), parent=P["root"], segments=16, ring_count=8)
    P["k"] = k; P["r"] = r; P["gap"] = gap * k
    P["ms"] = (0.03 * k, 0.008 * k, 0.006 * k); P["pop"] = 1.0; P["look"] = (0.0, 0.0)
    return P


def half_ring(S, parent, loc, major, minor, name="arco"):
    bpy.ops.mesh.primitive_torus_add(major_radius=major, minor_radius=minor, major_segments=24, minor_segments=8, location=loc, rotation=(rad(90), 0, 0))
    o = bpy.context.object; o.name = name; o.parent = parent; o.data.materials.append(S.mat("black"))
    bm = bmesh.new(); bm.from_mesh(o.data)
    bmesh.ops.delete(bm, geom=[v for v in bm.verts if v.co.y > 0.0005], context="VERTS")
    bm.to_mesh(o.data); bm.free()
    for p in o.data.polygons: p.use_smooth = True
    return o


def happy_face(S, P):
    """Prepara la sonrisa de verdad (medio aro ‿); se muestra con smile_at. Oculta al inicio."""
    k, r = P["k"], P["r"]
    P["smile"] = half_ring(S, P["root"], (0, -0.004 * k, -r * 1.9), 0.026 * k, 0.0045 * k, "sonrisa")
    S.key(P["smile"], 1, scale=(0.001,) * 3)
    return P["smile"]


def smile_at(S, P, f, on=True):
    sm = P["smile"]
    if on:
        S.key(P["mouth"], f - 1, scale=P["ms"]); S.key(P["mouth"], f, scale=(0.001,) * 3)
        S.key(sm, f - 1, scale=(0.001,) * 3); S.key(sm, f + 3, scale=(1, 1, 1), interp="BACK")
        for sx, b in zip((-1, 1), P["brows"]): S.key(b, f + 3, rot=(0, rad(4 * sx), 0))
    else:
        S.key(sm, f - 1, scale=(1, 1, 1)); S.key(sm, f, scale=(0.001,) * 3)
        S.key(P["mouth"], f - 1, scale=(0.001,) * 3)


def face_mood(S, P, f, mood):
    k = P["k"]
    mo = {"smile": ((0.034, 0.008, 0.015), 4), "neutral": ((0.02, 0.006, 0.005), 6), "wide": ((0.012, 0.007, 0.012), 16),
          "worry": ((0.018, 0.006, 0.006), 14), "oh": ((0.014, 0.008, 0.017), 6), "calm": ((0.016, 0.006, 0.004), -6)}[mood]
    P["ms"] = tuple(v * k for v in mo[0])
    S.key(P["mouth"], f, scale=P["ms"])
    for sx, b in zip((-1, 1), P["brows"]): S.key(b, f, rot=(0, rad(mo[1] * sx), 0))


def face_blink(S, P, f, hold=0, only=None):
    for i, (lid, r) in enumerate(P["lids"]):
        if only is not None and i != only: continue
        lx, ly = r * 1.1, r * 0.8
        S.key(lid, f - 1, scale=(lx, ly, 0.001)); S.key(lid, f + 1, scale=(lx, ly, r * 1.1))
        S.key(lid, f + 3 + hold, scale=(lx, ly, r * 1.1)); S.key(lid, f + 5 + hold, scale=(lx, ly, 0.001))


def face_look(S, P, f, dx, dz=0.0, pop=None):
    """Pupilas (y adelantada si los ojos están muy abiertos). pop: ojos enormes (escala de ojo y pupila)."""
    r = P["r"]
    if pop is not None:
        P["pop"] = pop
        for sx, e in zip((-1, 1), P["eyes"]): S.key(e, f, scale=(r * pop, r * 0.7 * pop, r * 1.15 * pop))
    pp = P["pop"]; P["look"] = (dx, dz)
    for sx, p in zip((-1, 1), P["pupils"]):
        S.key(p, f, loc=(P["gap"] * sx + dx, -r * 0.55 * pp, dz), scale=(r * 0.5 * (1 + (pp - 1) * 0.6), r * 0.25, r * 0.55 * (1 + (pp - 1) * 0.6)))


def shot(S, f, x, z, d=0.85, tz=None, elev=0.0, y=0.0, interp="CONSTANT"):
    """Plano de cámara; interp=CONSTANT => corte seco al siguiente plano; LINEAR => sigue sin acelerar."""
    S.key(S.cam, f, loc=(x, y - d * 1.75, z + elev), interp=interp)
    S.key(S.tgt, f, loc=(x, y, z if tz is None else tz), interp=interp)
    for o in (S.cam, S.tgt): _force(S, o, f, interp)


def _force(S, o, f, interp):
    for fc in S.fcurves(o):
        if fc.data_path == "location":
            for kp in fc.keyframe_points:
                if int(round(kp.co[0])) == f: kp.interpolation = interp


# ---------------------------------------------------------------- órbita de la mantequilla
def _g(u):
    if u < 0.85: return u / 0.925
    w = (u - 0.85) / 0.15
    return (0.85 + 0.075 * (1 - (1 - w) ** 2)) / 0.925


def th(f):
    u = min(max((f - F_O0) / (F_O1 - F_O0), 0.0), 1.0)
    return TH0 + (TH1 - TH0) * _g(u)


def bpos(f):
    t = th(f); return (CX + RX * math.cos(t), CY + RY * math.sin(t))


def bscale(f):
    pts = [(4, 1.0), (54, 0.86), (105, 0.74), (130, 0.65)]
    if f <= pts[0][0]: return pts[0][1]
    for (f0, s0), (f1, s1) in zip(pts, pts[1:]):
        if f <= f1: return s0 + (s1 - s0) * (f - f0) / (f1 - f0)
    return pts[-1][1]


# ---------------------------------------------------------------- nivel
def l1(S):
    S.cam.data.dof.aperture_fstop = 6.0; S.cam.data.dof.focus_object = S.tgt
    # --- materiales ---
    # crema pálido de mantequilla real (no amarillo intenso: evita parecido con un personaje de dibujos con marca registrada)
    butter = S.pmat("mantequilla", [(0.3, (0.98, 0.90, 0.62)), (0.7, (1.0, 0.95, 0.74))], scale=4, rough=0.32, bump=0.015)
    bsdf = butter.node_tree.nodes["Principled BSDF"]
    for nm, v in (("Subsurface Weight", 0.08), ("Subsurface Scale", 0.05)):
        if nm in bsdf.inputs: bsdf.inputs[nm].default_value = v
    puddle_m = S.pmat("charco_mant", [(0.3, (1.0, 0.76, 0.14)), (0.7, (1.0, 0.86, 0.30))], scale=3, rough=0.15, bump=0.0)
    trail_m = S.pmat("estela_mant", [(0.3, (1.0, 0.76, 0.14)), (0.7, (1.0, 0.85, 0.28))], scale=3, rough=0.5, bump=0.0)
    panm = S.pmat("sarten", [(0.3, (0.06, 0.06, 0.07)), (0.7, (0.14, 0.14, 0.15))], scale=10, rough=0.32, bump=0.02)
    panm.node_tree.nodes["Principled BSDF"].inputs["Metallic"].default_value = 0.55
    steel = S.pmat("acero", [(0.3, (0.70, 0.72, 0.76)), (0.7, (0.85, 0.87, 0.90))], scale=4, rough=0.25, bump=0.0)
    steel.node_tree.nodes["Principled BSDF"].inputs["Metallic"].default_value = 0.6
    wood = S.pmat("madera_moli", [(0.3, (0.20, 0.10, 0.06)), (0.7, (0.33, 0.19, 0.11))], scale=9, rough=0.4, bump=0.05)
    cake = S.pmat("tortita", [(0.3, (0.80, 0.52, 0.20)), (0.7, (0.92, 0.68, 0.32))], scale=7, rough=0.7, bump=0.08)
    cream = S.pmat("tortita_capa", [(0.3, (0.93, 0.80, 0.55)), (0.7, (0.97, 0.88, 0.66))], scale=7, rough=0.7, bump=0.05)

    def O(prim, name, mat, loc, scale=(1, 1, 1), rot=(0, 0, 0), parent=None, smooth=True, **kw):
        o = S.obj(prim, name, "white", loc, scale, rot, parent, smooth, **kw); o.data.materials[0] = mat; return o

    def bevel(o, w=0.05, seg=3):
        m = o.modifiers.new("bisel", "BEVEL"); m.width = w; m.segments = seg
        try: m.limit_method = "ANGLE"
        except Exception: pass

    # --- plató distinto (mañana fría): encimera de cuarzo blanco-azulado, azulejos azul claro, ventana ---
    S.sc.world.node_tree.nodes["Background"].inputs[1].default_value = 0.03
    sun = bpy.data.objects["sun"]; sun.data.energy = 0.3; sun.data.color = (0.82, 0.90, 1.0)
    bpy.data.objects["encimera"].data.materials[0] = S.pmat("cuarzo", [(0.3, (0.78, 0.84, 0.86)), (0.7, (0.90, 0.94, 0.95))], scale=5, rough=0.2, bump=0.03)
    for o in S.sc.objects:
        if o.name.startswith("pared"): o.data.materials[0] = S.pmat("azulejo", [(0.3, (0.45, 0.72, 0.80)), (0.5, (0.55, 0.80, 0.86)), (0.7, (0.40, 0.66, 0.76))], scale=14, rough=0.15, bump=0.12)
        if o.name.startswith("foco"): o.data.color = (0.80, 0.90, 1.0); o.data.energy = 18
        if o.name == "armario": o.data.materials[0] = S.pmat("armario_claro", [(0.3, (0.82, 0.84, 0.84)), (0.7, (0.92, 0.93, 0.92))], scale=6, rough=0.4, bump=0.03)
    win = bpy.data.materials.new("ventana"); win.use_nodes = True; wb = win.node_tree.nodes["Principled BSDF"]
    wb.inputs["Base Color"].default_value = (0.85, 0.93, 1.0, 1); wb.inputs["Emission Color"].default_value = (0.80, 0.92, 1.0, 1); wb.inputs["Emission Strength"].default_value = 1.6
    wx0 = -0.9
    O("cube", "ventana", win, (wx0, 3.08, 0.75), (0.7, 0.02, 0.5), smooth=False)
    O("cube", "marco_v", S.pmat("marco", [(0.3, (0.92, 0.92, 0.9)), (0.7, (0.97, 0.97, 0.95))], scale=4, rough=0.4, bump=0.0), (wx0, 3.05, 0.75), (0.015, 0.02, 0.5), smooth=False)
    O("cube", "marco_h", S.pmat("marco", [(0.3, (0.92, 0.92, 0.9)), (0.7, (0.97, 0.97, 0.95))], scale=4, rough=0.4, bump=0.0), (wx0, 3.05, 0.75), (0.7, 0.02, 0.015), smooth=False)

    # --- luces extra: relleno frontal frío ---
    lf = bpy.data.objects.new("relleno", bpy.data.lights.new("relleno", "AREA")); S.sc.collection.objects.link(lf)
    lf.location = (0.1, -1.3, 0.9); lf.rotation_euler = (rad(70), 0, 0); lf.data.energy = 14; lf.data.size = 1.4; lf.data.color = (0.92, 0.96, 1.0)
    lf2 = bpy.data.objects.new("contra", bpy.data.lights.new("contra", "AREA")); S.sc.collection.objects.link(lf2)
    lf2.location = (-0.6, 0.9, 0.9); lf2.rotation_euler = (rad(-60), 0, rad(-20)); lf2.data.energy = 8; lf2.data.size = 1.0; lf2.data.color = (0.85, 0.93, 1.0)

    # --- sartén ---
    O("cylinder", "sarten", panm, (PAN_X, 0.0, PZ / 2), radius=0.6, depth=PZ, vertices=64, smooth=False)
    O("torus", "borde_sarten", panm, (PAN_X, 0.0, 0.05), major_radius=0.62, minor_radius=0.03, major_segments=64, minor_segments=12)
    O("cylinder", "mango", steel, (PAN_X - 0.85, 0.0, 0.05), rot=(0, rad(90), 0), radius=0.024, depth=0.55, vertices=24)

    # --- molinillo de pimienta (con cara) ---
    M = S.empty("molinillo", (CX, CY, PZ))
    O("cone", "cuerpo_m", wood, (0, 0, 0.12), parent=M, radius1=0.062, radius2=0.045, depth=0.20, vertices=40, smooth=True)
    O("uv_sphere", "tapa_m", wood, (0, 0, 0.225), (0.05, 0.05, 0.04), parent=M, segments=32, ring_count=16)
    O("cylinder", "aro_m", steel, (0, 0, 0.022), radius=0.066, depth=0.014, vertices=40, parent=M, smooth=False)
    O("uv_sphere", "pomo_m", steel, (0, 0, 0.268), (0.014, 0.014, 0.014), parent=M, segments=16, ring_count=10)
    mf = mkface(S, M, 0.55); mf["root"].location = (0, -0.052, 0.135)
    face_mood(S, mf, 1, "neutral"); face_look(S, mf, 1, 0.0, 0.0)

    # --- tortita (3 capas, con cara) ---
    PK = S.empty("tortita", (PK_X, 0.0, PZ))
    lh = PK_H / 3
    for i in range(3):
        c = O("cylinder", "capa", cake, (0, 0, lh * (i + 0.5)), radius=0.2, depth=lh * 0.96, vertices=64, parent=PK, smooth=True); bevel(c, 0.012, 3)
        if i < 2: O("cylinder", "masa", cream, (0, 0, lh * (i + 1)), radius=0.196, depth=lh * 0.12, vertices=64, parent=PK, smooth=True)
    kf = mkface(S, PK, 0.9); kf["root"].location = (0, -0.218, 0.10)
    happy_face(S, kf)
    face_mood(S, kf, 1, "neutral"); face_look(S, kf, 1, -0.02, 0.0)

    # --- mantequilla ---
    BZ0 = 0.06                                        # alto de las piernas: el cuerpo empieza aquí
    B = S.empty("mantequilla", (-0.42, 0.06, PZ + 0.09))
    body = O("cube", "cuerpo_b", butter, (0, 0, BZ0 + 0.10), (0.22, 0.16, 0.20), parent=B, smooth=True, size=1); bevel(body, 0.07, 4)
    puddle = O("uv_sphere", "charco", puddle_m, (0, 0, 0.004), (0.001,) * 3, parent=B, segments=48, ring_count=16)
    legs = []; arms = []
    for sx in (-1, 1):
        hip = S.empty("cadera", (0.07 * sx, 0, BZ0 + 0.005), parent=B)
        O("cylinder", "pierna", steel, (0, 0, -0.03), radius=0.011, depth=0.06, vertices=16, parent=hip)
        O("uv_sphere", "cuchilla", steel, (0, -0.012, -0.062), (0.034, 0.016, 0.007), parent=hip, segments=20, ring_count=10)
        legs.append((hip, sx))
        sh = S.empty("hombro", (0.105 * sx, 0, BZ0 + 0.10), parent=B)
        O("cylinder", "brazo", butter, (0.035 * sx, 0, 0), rot=(0, rad(90), 0), radius=0.012, depth=0.07, vertices=16, parent=sh)
        O("uv_sphere", "mano", butter, (0.075 * sx, 0, 0), (0.02, 0.02, 0.02), parent=sh, segments=16, ring_count=10)
        arms.append((sh, sx)); sh.scale = (0.001, 0.001, 0.001)   # sin bracitos: solo patines (más propio, menos "personaje de serie")
    bf = mkface(S, B, 1.0); bf["root"].location = (0, -0.079, BZ0 + 0.108)
    happy_face(S, bf)

    # --- cámara ---
    S.cam.data.lens = 50; S.cam.data.keyframe_insert("lens", frame=1)
    BZC = 0.16                                          # altura de la cara de la mantequilla

    def track(f0, f1, d, step=6, z=BZC, elev=0.06, fx=lambda x: x):
        for f in range(f0, f1, step):
            bx, by = bpos(f)
            shot(S, f, fx(bx), z, d=d, elev=elev, y=by * 0.5, interp="LINEAR")
        bx, by = bpos(f1 - 1)
        shot(S, f1 - 1, fx(bx), z, d=d, elev=elev, y=by * 0.5, interp="CONSTANT")

    track(1, 36, 0.62, fx=lambda x: x + 0.04)                                                       # gancho: aterriza y patina (primer plano)
    shot(S, 36, 0.08, 0.10, d=1.45, elev=0.25)                              # plano abierto (~1 s): sartén, molinillo, tortita
    track(63, 97, 0.62, fx=lambda x: CX + 0.5 * (x - CX), z=0.15, elev=0.12) # esquiva el molinillo
    track(97, 131, 0.55)                                                     # vuelve al frente
    shot(S, F_POSE0, CX, 0.11, d=0.48, elev=0.04, y=-0.08 * 0.5)            # pose de patinadora, orgullosa
    shot(S, F_D, CX, 0.05, d=0.48, elev=0.26, y=-0.08 * 0.5)                # el charco quieto
    shot(S, F_PK, PK_X, 0.14, d=0.46, elev=0.04)                            # la tortita mira desde el lado
    shot(S, F_E, 0.12, 0.10, d=0.80, elev=0.20, y=-0.03, interp="LINEAR")   # el charco se desliza hacia la tortita
    shot(S, F_FIN - 1, 0.20, 0.11, d=0.80, elev=0.20, y=-0.03)
    shot(S, F_FIN, PK_X, 0.16, d=0.52, elev=0.15)                           # final: dos caras juntas

    # --- 1: gancho, cae y patina (cara ENORME ya en el fotograma 1) ---
    for hip, sx in legs: S.key(hip, 1, rot=(0, 0, 0))
    S.key(B, 1, loc=(-0.42, 0.06, PZ + 0.09), rot=(0, rad(12), 0), scale=(0.95, 0.95, 1.08))
    face_mood(S, bf, 1, "oh"); face_look(S, bf, 1, 0.0, -0.01, pop=1.5)
    for sh, sx in arms: S.key(sh, 1, rot=(0, rad(-sx * 55), 0))
    S.cue("boing", 4, vol=-4); S.cue("slide_down", 5, vol=-3)
    # órbita
    f = F_O0
    while f <= F_O1:
        t = th(f); x, y = bpos(f); s = bscale(f)
        u = (f - F_O0) / (F_O1 - F_O0)
        lean = -math.sin(t) * 12 * (1.0 if u < 0.85 else max(0.0, 1 - (u - 0.85) / 0.15))
        sq = 1.0 + 0.04 * math.cos(t * 2)
        if f == F_O0:
            S.key(B, f, loc=(x, y, PZ), rot=(0, rad(lean), 0), scale=(s * 1.15, s * 1.1, s * 0.82))
        else:
            S.key(B, f, loc=(x, y, PZ), rot=(0, rad(lean), 0), scale=(s * sq, s * sq, s / sq), interp="LINEAR")
        for sh, sx in arms:
            S.key(sh, f, rot=(0, rad(-sx * (28 + 14 * math.sin(f / 5.0 + (0 if sx > 0 else 1.5)))), 0))
        f += 3
    # estela de mantequilla derretida (charquitos planos)
    for f in range(10, F_O1 - 6, 8):
        x, y = bpos(f)
        r = 0.05 * bscale(f)
        d = O("cylinder", "estela", trail_m, (x, y, PZ + 0.0025 + 0.0004 * (f % 7)), (r, r * 0.8, 1), radius=1.0, depth=0.005, vertices=24, smooth=False)
        S.key(d, f - 1, scale=(0.001, 0.001, 1)); S.key(d, f + 4, scale=(r * 1.2, r, 1)); S.key(d, f + 8, scale=(r, r * 0.8, 1))
    # caras en la órbita
    smile_at(S, bf, 24)
    face_look(S, bf, 12, 0.0, 0.0, pop=1.35); face_look(S, bf, 26, 0.0, 0.0, pop=1.1)
    face_look(S, bf, 56, 0.01, 0.0, pop=1.1)
    face_look(S, bf, 100, 0.0, -0.02, pop=1.1)                                    # nota que encoge un poco
    face_look(S, bf, 112, 0.0, 0.0, pop=1.1)
    face_blink(S, bf, 76)
    # el molinillo se asusta en cada pasada
    for fp in (24, 126):
        face_mood(S, mf, fp, "wide"); face_look(S, mf, fp, 0.0, 0.0, pop=1.4)
    face_mood(S, mf, 38, "worry"); face_look(S, mf, 38, 0.02, 0.0, pop=1.0)
    face_mood(S, mf, 70, "wide"); face_look(S, mf, 70, 0.02, 0.0, pop=1.3)
    face_mood(S, mf, 88, "worry"); face_look(S, mf, 88, -0.02, 0.0, pop=1.1)
    face_blink(S, mf, 98)
    for f0 in (27, 79, 129):
        S.key(M, f0 - 1, rot=(0, 0, 0)); S.key(M, f0 + 2, rot=(0, rad(-6), 0)); S.key(M, f0 + 6, rot=(0, rad(5), 0)); S.key(M, f0 + 10, rot=(0, 0, 0))
    S.cue("whoosh", 28, vol=-9); S.cue("whoosh", 104, vol=-10)
    # la tortita sigue a la mantequilla con la mirada
    for f in range(4, 128, 12):
        bx, by = bpos(f)
        face_look(S, kf, f, max(-0.03, min(0.03, (bx - PK_X) * 0.04)), 0.0)
    face_blink(S, kf, 90)

    # --- 130-172: pose de patinadora, un pie alto, orgullosa ---
    F = F_POSE0
    S.cue("whoosh", F + 8, vol=-6)
    bx, by = bpos(F_O1); s = bscale(F_O1)
    S.key(B, F_O1 + 1, loc=(bx, by, PZ), rot=(0, 0, 0), scale=(s * 1.12, s * 1.12, s * 0.86))                # derrape final
    S.key(B, F_O1 + 5, loc=(bx, by, PZ), rot=(0, 0, 0), scale=(s * 0.96, s * 0.96, s * 1.05))
    S.key(B, F + 9, loc=(bx, by, PZ), rot=(0, 0, 0), scale=(s, s, s))
    S.key(B, F + 12, loc=(bx, by, PZ), rot=(0, rad(-5), 0), scale=(s * 1.04, s * 1.04, s * 0.94))              # anticipación
    S.key(B, F + 18, loc=(bx, by, PZ + 0.0), rot=(0, rad(-9), 0), scale=(s * 0.97, s * 0.97, s * 1.04), interp="BACK")
    S.key(B, F + 40, loc=(bx, by, PZ), rot=(0, rad(-10), 0), scale=(s * 0.98, s * 0.98, s * 1.03))
    for hip, sx in legs:
        S.key(hip, F_O1, rot=(0, 0, 0))
        S.key(hip, F + 12, rot=(0, 0, 0))
        S.key(hip, F + 19, rot=(0, rad(-78 * sx) if sx > 0 else rad(8), 0), interp="BACK")
        S.key(hip, F + 41, rot=(0, rad(-78 * sx) if sx > 0 else rad(8), 0))
    for sh, sx in arms:
        S.key(sh, F + 12, rot=(0, rad(-sx * 40), 0)); S.key(sh, F + 20, rot=(0, rad(-sx * 70), 0), interp="BACK")
        S.key(sh, F + 41, rot=(0, rad(-sx * 66), 0))
    face_look(S, bf, F + 10, 0.0, 0.0, pop=1.0); face_blink(S, bf, F + 28, hold=4)
    for sx, b in zip((-1, 1), bf["brows"]): S.key(b, F + 18, rot=(0, rad(8 * sx), 0))
    S.cue("pop", F + 19, vol=-8)

    # --- 173-224: se derrite en un charco liso y quieto (silencio) ---
    sB = 0.65
    k_pud = (0.31, 0.23, 0.02)
    S.key(body, F_D - 1, scale=(0.22, 0.16, 0.20)); S.key(body, F_D, scale=(0.001,) * 3)
    for hip, sx in legs: S.key(hip, F_D - 1, scale=(1, 1, 1)); S.key(hip, F_D, scale=(0.001,) * 3)
    for sh, sx in arms: S.key(sh, F_D - 1, scale=(0.001,) * 3); S.key(sh, F_D, scale=(0.001,) * 3)
    S.key(B, F_D - 1, loc=(bx, by, PZ), rot=(0, rad(-10), 0), scale=(s * 0.98, s * 0.98, s * 1.03))
    S.key(B, F_D, loc=(bx, by, PZ), rot=(0, 0, 0), scale=(sB, sB, sB))
    S.key(puddle, F_D - 1, scale=(0.001,) * 3); S.key(puddle, F_D, scale=(k_pud[0] * 0.92, k_pud[1] * 0.92, k_pud[2]))
    S.key(puddle, F_PK - 1, scale=(k_pud[0], k_pud[1], k_pud[2]))
    S.key(bf["root"], F_D - 1, loc=(0, -0.079, BZ0 + 0.108), rot=(0, 0, 0))
    S.key(bf["root"], F_D, loc=(0, -0.04, 0.06), rot=(rad(-60), 0, 0))
    S.key(bf["smile"], F_D, scale=(1, 1, 1))              # sigue sonriendo al derretirse (alegre)
    face_look(S, bf, F_D, 0.0, 0.0, pop=1.0)
    face_blink(S, bf, F_D + 22); face_look(S, bf, F_D + 34, 0.0, 0.01); face_blink(S, bf, F_D + 44)
    for sx, b in zip((-1, 1), bf["brows"]): S.key(b, F_D + 6, rot=(0, rad(5 * sx), 0))
    S.cue("clunk", F_D, vol=-14)
    face_mood(S, mf, F_D + 4, "worry"); face_look(S, mf, F_D + 4, 0.0, -0.025, pop=1.15)
    face_blink(S, mf, F_D + 28)
    # la mirada de la tortita, preocupada
    face_mood(S, kf, F_D + 2, "worry"); face_look(S, kf, F_D + 2, -0.03, 0.0)

    # --- 225-258: la tortita mira desde el lado ---
    face_look(S, kf, F_PK, -0.03, 0.0, pop=1.15); face_mood(S, kf, F_PK, "worry")
    face_blink(S, kf, F_PK + 12); face_look(S, kf, F_PK + 22, -0.032, -0.01, pop=1.15)
    face_mood(S, kf, F_PK + 26, "oh")
    S.key(PK, F_PK + 20, loc=(PK_X, 0, PZ), scale=(1, 1, 1)); S.key(PK, F_PK + 24, loc=(PK_X, 0, PZ), scale=(0.97, 0.97, 1.04)); S.key(PK, F_PK + 29, loc=(PK_X, 0, PZ), scale=(1, 1, 1))

    # --- 259-322: el charco se desliza y se extiende sobre la tortita ---
    sE = 0.85
    S.cue("whoosh", F_E + 2, vol=-6)
    S.key(B, F_E - 1, loc=(bx, by, PZ), scale=(sB, sB, sB))
    S.key(B, F_E + 6, loc=(bx - 0.02, by, PZ), scale=(sB * 0.95, sB * 0.95, sB * 1.0))
    S.key(B, F_E + 28, loc=(0.09, -0.03, PZ), scale=(sB * 1.05, sB * 0.95, sB), interp="LINEAR")
    S.key(B, F_E + 36, loc=(0.12, -0.05, PZ), scale=(sB * 1.12, sB * 0.9, sB))                      # empuja contra el borde
    S.key(B, F_E + 48, loc=(PK_X, -0.01, PZ + PK_H), scale=(sE, sE, sE), interp="BEZIER")           # trepa sobre la tortita
    S.key(B, F_E + 56, loc=(PK_X, -0.0, PZ + PK_H), scale=(sE, sE, sE))
    S.key(puddle, F_E + 28, scale=(k_pud[0], k_pud[1], k_pud[2])); S.key(puddle, F_E + 36, scale=(k_pud[0] * 0.8, k_pud[1] * 1.0, k_pud[2] * 1.8))
    S.key(puddle, F_E + 48, scale=(k_pud[0] * 0.65, k_pud[1] * 0.85, k_pud[2] * 1.5))
    S.key(puddle, F_E + 60, scale=(0.20, 0.20, 0.022), interp="BACK")                               # cubre la tapa
    S.key(bf["root"], F_E + 48, loc=(0, -0.04, 0.06), rot=(rad(-60), 0, 0)); S.key(bf["root"], F_E + 60, loc=(0, -0.05, 0.065), rot=(rad(-60), 0, 0))
    face_look(S, bf, F_E + 2, 0.02, 0.0, pop=1.2)
    face_look(S, bf, F_E + 30, 0.0, 0.0, pop=1.1)
    S.cue("pop", F_E + 46, vol=-6)
    face_mood(S, kf, F_E + 8, "wide"); face_look(S, kf, F_E + 8, -0.02, 0.0, pop=1.3)
    face_look(S, kf, F_E + 40, 0.0, 0.03, pop=1.25)
    # gotas por el costado
    for gx, gy, gf in ((-0.15, -0.132, F_E + 50), (0.16, -0.12, F_E + 54), (-0.19, -0.06, F_E + 58)):
        g = O("uv_sphere", "gota", puddle_m, (gx, gy, PK_H - 0.02), (0.001,) * 3, parent=PK, segments=16, ring_count=10)
        S.key(g, gf, scale=(0.001,) * 3); S.key(g, gf + 8, scale=(0.017, 0.012, 0.012)); S.key(g, gf + 16, scale=(0.017, 0.013, 0.04), interp="BACK")
        S.key(g, gf + 18, loc=(gx, gy, PK_H - 0.02)); S.key(g, gf + 22, loc=(gx, gy, PK_H - 0.04))

    # --- 323-408: final, la tortita sonríe dorada y la mantequilla guiña ---
    F = F_FIN
    face_look(S, kf, F, 0.0, 0.0, pop=1.0); face_mood(S, kf, F, "calm")
    smile_at(S, kf, F + 12)
    S.key(PK, F + 12, loc=(PK_X, 0, PZ), scale=(1, 1, 1)); S.key(PK, F + 16, loc=(PK_X, 0, PZ), scale=(1.04, 1.04, 0.97)); S.key(PK, F + 22, loc=(PK_X, 0, PZ), scale=(1, 1, 1))
    S.cue("tada", F + 13, vol=-3)
    face_blink(S, kf, F + 40)
    face_look(S, bf, F + 30, 0.0, 0.0, pop=1.0)
    S.cue("pop", F + 52, vol=-6)
    face_blink(S, bf, F + 52, hold=26, only=1)                                                         # guiño: ojo derecho cerrado
    face_look(S, kf, F + 54, 0.0, 0.0)
    pr = bf["r"]; pb = (pr * 0.5, pr * 0.25, pr * 0.55)
    S.key(bf["pupils"][1], F + 52, scale=pb); S.key(bf["pupils"][1], F + 53, scale=(0.001,) * 3)
    S.key(bf["pupils"][1], F + 80, scale=(0.001,) * 3); S.key(bf["pupils"][1], F + 82, scale=pb)
    S.key(B, F, loc=(PK_X, 0.0, PZ + PK_H), scale=(sE, sE, sE)); S.key(B, F_END - 10, loc=(PK_X, 0.0, PZ + PK_H), scale=(sE * 1.02, sE * 1.02, sE * 0.98))
    S.f = F_END - 10
    return B


LEVELS = [(0, l1)]
