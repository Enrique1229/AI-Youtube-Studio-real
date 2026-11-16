"""ep004 — Objetos vivos: una pompa nace de una esponja, esquiva un tenedor y un lápiz, y el lápiz la revienta; la esponja saca una pompita.
Encimera (mesa), sin diálogo, un solo nivel, sin rótulo."""
import math
import random
import bpy

TITLE = "The Little Bubble Who Stayed"
CAPTION = None
SPEED = 1.0
CTA = "follow for more"
ENV = "mesa"
CUSTOM_CAMERA = True

SX = -0.21                 # x de la esponja
FX = 0.04                  # x del tenedor
PX = 0.59                  # x de la base del lápiz
WX = 0.38                  # x del centro de la ventana
BX, BZ = 0.35, 0.54        # posición de la pompa junto a la ventana
F_POP = 186
F_END = 390


# ---------------------------------------------------------------- caras (como ep002)
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


def happy_face(S, P):
    k, r = P["k"], P["r"]
    P["mouth"].scale = (0.001, 0.001, 0.001)
    bpy.ops.mesh.primitive_torus_add(major_radius=0.026 * k, minor_radius=0.0045 * k, major_segments=24, minor_segments=8,
                                     location=(0, -0.004 * k, -r * 2.2), rotation=(math.radians(90), 0, 0))
    sm = bpy.context.object; sm.name = "sonrisa"; sm.parent = P["root"]; sm.data.materials.append(S.mat("black"))
    import bmesh
    bm = bmesh.new(); bm.from_mesh(sm.data)
    bmesh.ops.delete(bm, geom=[v for v in bm.verts if v.co.y > 0.002 * k], context="VERTS")
    bm.to_mesh(sm.data); bm.free()
    for sx, br in zip((-1, 1), P["brows"]):
        br.location.z += r * 0.35; br.rotation_euler = (0, math.radians(12 * sx), 0)


def face_mood(S, P, f, mood):
    k = P["k"]
    mo = {"cold": ((0.022, 0.006, 0.005), 14), "smile": ((0.034, 0.008, 0.015), -4), "sad": ((0.018, 0.006, 0.005), 22),
          "neutral": ((0.02, 0.006, 0.005), 0), "wide": ((0.012, 0.007, 0.012), 18)}[mood]
    S.key(P["mouth"], f, scale=tuple(v * k for v in mo[0]))
    for sx, b in zip((-1, 1), P["brows"]):
        S.key(b, f, rot=(0, math.radians(mo[1] * sx), 0))


def face_blink(S, P, f, hold=0):
    for lid, r in P["lids"]:
        lx, ly = r * 1.1, r * 0.8
        S.key(lid, f - 1, scale=(lx, ly, 0.001)); S.key(lid, f + 1, scale=(lx, ly, r * 1.1))
        S.key(lid, f + 3 + hold, scale=(lx, ly, r * 1.1)); S.key(lid, f + 5 + hold, scale=(lx, ly, 0.001))


def face_wink(S, P, f, idx=1):
    lid, r = P["lids"][idx]; lx, ly = r * 1.1, r * 0.8
    S.key(lid, f - 1, scale=(lx, ly, 0.001)); S.key(lid, f + 1, scale=(lx, ly, r * 1.1))      # se queda cerrado hasta el final


def face_look(S, P, f, dx, dz=0.0):
    r = P["r"]
    for sx, p in zip((-1, 1), P["pupils"]): S.key(p, f, loc=(P["gap"] * sx + dx, -r * 0.55, dz))


def swap(S, a, b, f):
    """a se apaga y b se enciende en el fotograma f (cambio de cara)."""
    S.key(a["root"], f - 1, scale=(1, 1, 1)); S.key(a["root"], f, scale=(0.001,) * 3)
    S.key(b["root"], f - 1, scale=(0.001,) * 3); S.key(b["root"], f, scale=(1, 1, 1))


# ---------------------------------------------------------------- cámara
def _kps(o):
    ad = o.animation_data
    if not ad or not ad.action: return
    act = ad.action
    if hasattr(act, "fcurves"): fcs = list(act.fcurves)
    else: fcs = [fc for l in act.layers for st in l.strips for cb in st.channelbags for fc in cb.fcurves]
    for fc in fcs:
        if fc.data_path == "location": yield from fc.keyframe_points


def shot(S, f, x, z, d=0.85, tz=None, interp="CONSTANT"):
    S.key(S.cam, f, loc=(x, -d * 1.75, z), interp=interp)
    S.key(S.tgt, f, loc=(x, 0, z if tz is None else tz), interp=interp)
    for o in (S.cam, S.tgt):
        for kp in _kps(o):
            if int(round(kp.co[0])) == f: kp.interpolation = interp


# ---------------------------------------------------------------- materiales
def bubble_mat(S):
    m = S.pmat("pompa", [(0.25, (0.55, 0.80, 1.0)), (0.5, (1.0, 0.62, 0.85)), (0.75, (0.62, 1.0, 0.78))], scale=2.0, rough=0.03, bump=0.0)
    b = m.node_tree.nodes["Principled BSDF"]
    b.inputs["Alpha"].default_value = 1.0
    b.inputs["Transmission Weight"].default_value = 0.85
    b.inputs["IOR"].default_value = 1.08
    b.inputs["Roughness"].default_value = 0.03
    if "Thin Film Thickness" in b.inputs:                       # iridiscencia leve
        b.inputs["Thin Film Thickness"].default_value = 420.0
        if "Thin Film IOR" in b.inputs: b.inputs["Thin Film IOR"].default_value = 1.4
    if "Emission Strength" in b.inputs:
        b.inputs["Emission Color"].default_value = (0.75, 0.9, 1.0, 1); b.inputs["Emission Strength"].default_value = 0.0
    return m


def make_bubble(S, name, mat, R=0.14, fk=1.0):
    root = S.empty(name, (0, 0, 0.5))
    body = S.obj("uv_sphere", name + "_cuerpo", "white", (0, 0, 0), (R, R, R), parent=root, segments=48, ring_count=24)
    body.data.materials[0] = mat
    return root


# ---------------------------------------------------------------- nivel
def l1(S):
    S.cam.data.dof.aperture_fstop = 6.0; S.cam.data.dof.focus_object = S.tgt
    random.seed(4)
    for i in range(3): bpy.data.objects[f"foco{i}"].data.energy = 14
    bm = bubble_mat(S)

    # --- esponja (amarilla con poros, base verde) ---
    sp_y = S.pmat("esponja", [(0.25, (0.93, 0.74, 0.10)), (0.55, (1.0, 0.86, 0.22)), (0.8, (0.88, 0.66, 0.06))], scale=14, rough=0.9, bump=0.6, detail=8)
    sp_g = S.pmat("estropajo", [(0.3, (0.12, 0.45, 0.16)), (0.7, (0.22, 0.62, 0.22))], scale=40, rough=0.95, bump=0.8, detail=8)
    sponge = S.empty("esponja", (SX, 0, 0))
    body = S.obj("cube", "esponja_cuerpo", "yellow", (0, 0, 0.125), (0.13, 0.10, 0.115), parent=sponge); body.data.materials[0] = sp_y
    bv = body.modifiers.new("bisel", "BEVEL"); bv.width = 0.25; bv.segments = 4; bv.limit_method = "NONE"
    base = S.obj("cube", "estropajo", "green", (0, 0, 0.012), (0.134, 0.104, 0.012), parent=sponge); base.data.materials[0] = sp_g
    bv2 = base.modifiers.new("bisel", "BEVEL"); bv2.width = 0.3; bv2.segments = 3; bv2.limit_method = "NONE"
    for i in range(9):                                                                     # poros
        px = random.uniform(-0.10, 0.10); pz = random.uniform(0.05, 0.22)
        if abs(px) < 0.075 and 0.07 < pz < 0.215 and px * 0 == 0 and random.random() < 0.85 and abs(px) < 0.08: px = math.copysign(random.uniform(0.09, 0.115), px)
        o = S.obj("uv_sphere", "poro", "brown", (px, -0.098, pz), (0.011, 0.004, 0.008), parent=sponge, segments=10, ring_count=6)
    for i in range(5):
        px = random.uniform(-0.1, 0.1); py = random.uniform(-0.07, 0.07)
        S.obj("uv_sphere", "poro", "brown", (px, py, 0.238), (0.012, 0.012, 0.004), parent=sponge, segments=10, ring_count=6)
    fA = mkface(S, sponge, 1.1); fA["root"].location = (0, -0.1, 0.138)
    fB = mkface(S, sponge, 1.1); fB["root"].location = (0, -0.1, 0.138); happy_face(S, fB)
    S.key(fA["root"], 1, scale=(1, 1, 1)); S.key(fB["root"], 1, scale=(0.001,) * 3)

    # --- tenedor ---
    fm = S.mat("metal").copy(); fm.name = "tenedor"
    fb = fm.node_tree.nodes["Principled BSDF"]; fb.inputs["Metallic"].default_value = 0.55; fb.inputs["Roughness"].default_value = 0.28
    fb.inputs["Base Color"].default_value = (0.78, 0.8, 0.84, 1)
    fork = S.empty("tenedor", (FX, 0.0, 0.0))
    parts = [((0, 0, 0.085), (0.017, 0.008, 0.085)), ((0, 0, 0.19), (0.011, 0.007, 0.022)), ((0, 0, 0.24), (0.056, 0.007, 0.03))]
    for tx in (-0.0405, -0.0135, 0.0135, 0.0405): parts.append(((tx, 0, 0.325), (0.0085, 0.007, 0.056)))
    for loc, sc in parts:
        o = S.obj("cube", "tenedor_p", "metal", loc, sc, parent=fork, smooth=False); o.data.materials[0] = fm
    for tx in (-0.0405, -0.0135, 0.0135, 0.0405):                                           # puntas redondeadas
        o = S.obj("uv_sphere", "punta", "metal", (tx, 0, 0.38), (0.0085, 0.007, 0.008), parent=fork, segments=10, ring_count=6); o.data.materials[0] = fm

    # --- lápiz (detrás), pivote en la base ---
    pen = S.empty("lapiz", (PX, 0.10, 0.0))
    S.obj("cylinder", "goma", "pink", (0, 0, 0.02), (0.018, 0.018, 0.02), parent=pen, vertices=12)
    S.obj("cylinder", "virola", "metal", (0, 0, 0.055), (0.0185, 0.0185, 0.015), parent=pen, vertices=12)
    S.obj("cylinder", "lapiz_cuerpo", "yellow", (0, 0, 0.285), (0.018, 0.018, 0.215), parent=pen, vertices=6)
    S.obj("cone", "madera", "cream", (0, 0, 0.5425), (0.018, 0.018, 0.0425), parent=pen, vertices=6)
    S.obj("cone", "mina", "black", (0, 0, 0.5765), (0.0085, 0.0085, 0.0235), parent=pen, vertices=8)

    # --- ventana soleada al fondo ---
    wm = bpy.data.materials.new("sol"); wm.use_nodes = True; wb = wm.node_tree.nodes["Principled BSDF"]
    wb.inputs["Base Color"].default_value = (0.5, 0.75, 1.0, 1); wb.inputs["Emission Color"].default_value = (0.55, 0.78, 1.0, 1); wb.inputs["Emission Strength"].default_value = 1.4
    pane = S.obj("cube", "cristal", "white", (WX, 0.45, 0.30), (0.19, 0.004, 0.30), smooth=False); pane.data.materials[0] = wm
    for loc, sc in (((WX - 0.195, 0.44, 0.30), (0.012, 0.012, 0.31)), ((WX + 0.195, 0.44, 0.30), (0.012, 0.012, 0.31)),
                    ((WX, 0.44, 0.615), (0.20, 0.012, 0.012)), ((WX, 0.44, 0.0), (0.20, 0.012, 0.012)),
                    ((WX, 0.44, 0.31), (0.007, 0.01, 0.30)), ((WX, 0.44, 0.31), (0.19, 0.01, 0.007))):
        S.obj("cube", "marco", "white", loc, sc, smooth=False)

    # --- pompa principal ---
    pom = make_bubble(S, "pompa", bm)
    pH = mkface(S, pom, 1.0); pH["root"].location = (0, -0.098, 0.004); happy_face(S, pH)
    pW = mkface(S, pom, 1.0); pW["root"].location = (0, -0.098, 0.004)
    S.key(pH["root"], 1, scale=(1, 1, 1)); S.key(pW["root"], 1, scale=(0.001,) * 3)
    face_mood(S, pW, 1, "wide")

    # --- pompita final ---
    pit = make_bubble(S, "pompita", bm)
    qH = mkface(S, pit, 1.0); qH["root"].location = (0, -0.098, 0.004); happy_face(S, qH)
    S.key(pit, 1, loc=(SX, 0, 0.3), scale=(0.001,) * 3)

    # --- gotitas ---
    drops = []
    for i in range(14):
        rr = random.uniform(0.012, 0.024)
        d = S.obj("uv_sphere", "gota", "white", (0, 0, 0), (rr, rr, rr), segments=14, ring_count=8); d.data.materials[0] = bm
        S.key(d, 1, loc=(BX, 0, BZ), scale=(0.001,) * 3); drops.append((d, rr))

    # --- cámara: cortes entre planos cerrados ---
    S.cam.data.lens = 50; S.cam.data.keyframe_insert("lens", frame=1)
    shot(S, 1, SX + 0.115, 0.42, d=0.78)          # A: nace la pompa sobre el tenedor
    shot(S, 30, 0.15, 0.45, d=0.65)              # B: roza las puntas
    shot(S, 70, WX, 0.40, d=0.75)                # C: el lápiz casi la toca
    shot(S, 102, SX, 0.26, d=0.55)               # D: la esponja mira preocupada
    shot(S, 124, WX, 0.40, d=0.75)               # E: ventana, sonríe, pop
    shot(S, 207, SX, 0.30, d=0.50)               # F: esponja triste, giro, imagen final

    # --- esponja ---
    S.key(sponge, 1, scale=(1.08, 1.05, 0.8)); S.key(sponge, 4, scale=(0.92, 0.94, 1.1)); S.key(sponge, 10, scale=(1.03, 1.03, 0.97)); S.key(sponge, 16, scale=(1, 1, 1))
    S.cue("boing", 2, vol=-4); S.cue("pop", 3, vol=-8)
    face_mood(S, fA, 1, "wide"); face_mood(S, fA, 20, "cold"); face_look(S, fA, 8, 0.03, 0.03); face_look(S, fA, 24, 0.035, 0.0)
    face_blink(S, fA, 44); face_look(S, fA, 105, 0.035, 0.0); face_blink(S, fA, 112)

    # --- pompa: nacimiento, graze, deriva, lápiz ---
    P = [(1, (SX, 0, 0.27), (0.7, 0.7, 0.7)), (4, (SX + 0.02, 0, 0.38), (0.9, 0.9, 1.2)), (10, (-0.10, 0, 0.58), (1.05, 1.05, 0.95)),
         (17, (0.0, 0, 0.58), (1, 1, 1)), (24, (FX, 0, 0.535), (1, 1, 1)), (32, (FX, 0, 0.52), (1, 1, 1)), (40, (FX, 0, 0.50), (1, 1, 1)),
         (46, (FX, 0, 0.51), (1.06, 1.06, 0.86)), (50, (FX + 0.01, 0, 0.525), (0.95, 0.95, 1.06)),
         (54, (0.08, 0, 0.51), (0.96, 0.96, 0.97)), (58, (0.12, 0, 0.53), (1.02, 1.02, 1.0)), (62, (0.17, 0, 0.51), (0.96, 0.96, 0.97)),
         (66, (0.22, 0, 0.53), (1.02, 1.02, 1.0)), (72, (0.27, 0, 0.55), (0.97, 0.97, 0.98)), (80, (0.30, 0, 0.53), (1, 1, 1)),
         (86, (0.325, 0, 0.525), (0.88, 1.0, 1.04)), (92, (BX - 0.01, 0, 0.52), (1.02, 1.0, 1.0)), (98, (BX, 0, 0.52), (1, 1, 1)),
         (112, (BX, 0, 0.53), (1, 1, 1)), (130, (BX + 0.01, 0, 0.515), (1.02, 1.02, 0.99)), (150, (BX, 0, 0.53), (1, 1, 1)),
         (170, (BX, 0, 0.52), (1.02, 1.02, 0.99)), (F_POP - 1, (BX, 0, BZ), (1.15, 1.15, 1.15)), (F_POP, (BX, 0, BZ), (0.001,) * 3)]
    for f, l, s_ in P:
        dz = 0.02 if (24 <= f < F_POP - 1 and f != 46) else 0.0
        S.key(pom, f, loc=(l[0], l[1], l[2] + dz), scale=s_)
    S.cue("boing", 46, vol=-14); S.cue("whoosh", 60, vol=-14); S.cue("whoosh", 84, vol=-12)
    face_look(S, pH, 1, 0.0, 0.01); face_blink(S, pH, 30); face_look(S, pH, 132, 0.025, 0.012); face_look(S, pH, 150, 0.0, 0.0); face_blink(S, pH, 160)
    swap(S, pH, pW, 44); face_look(S, pW, 44, 0.0, 0.0); face_look(S, pW, 60, 0.02, 0.0); face_look(S, pW, 80, 0.03, 0.01)
    swap(S, pW, pH, 112)
    S.key(fork, 44, rot=(0, 0, 0)); S.key(fork, 47, rot=(0, 0.05, 0)); S.key(fork, 51, rot=(0, -0.04, 0)); S.key(fork, 55, rot=(0, 0.02, 0)); S.key(fork, 60, rot=(0, 0, 0))

    # --- lápiz: asoma, casi roza, amenaza y revienta ---
    a = math.radians
    for f, deg in ((1, -5), (74, -5), (84, -13.5), (88, -13), (98, -5), (168, -5), (180, -15), (F_POP - 1, -19), (200, -19), (216, -6), (230, -6)):
        S.key(pen, f, rot=(0, a(deg), 0))
    S.cue("creak", 82, vol=-10); S.cue("creak", 170, vol=-12)

    # --- pop y gotitas ---
    S.cue("pop", F_POP, vol=-2)
    for i, (d, rr) in enumerate(drops):
        ang = 2 * math.pi * i / len(drops) + random.uniform(-0.2, 0.2)
        ox, oz = math.cos(ang), math.sin(ang)
        t0 = F_POP; tl = F_POP + random.randint(18, 26)
        S.key(d, F_POP - 1, loc=(BX, 0, BZ), scale=(0.001,) * 3)
        S.key(d, F_POP, loc=(BX + ox * 0.10, random.uniform(-0.03, 0.03), BZ + oz * 0.10), scale=(rr,) * 3)
        S.key(d, t0 + 7, loc=(BX + ox * 0.17, random.uniform(-0.04, 0.04), BZ + max(oz, -0.2) * 0.15 + 0.03), scale=(rr,) * 3)
        S.key(d, tl, loc=(BX + ox * 0.22, random.uniform(-0.05, 0.05), 0.012), scale=(rr * 1.0,) * 3)
        S.key(d, tl + 2, scale=(rr * 1.5, rr * 1.5, rr * 0.4)); S.key(d, tl + 12, scale=(rr * 1.6, rr * 1.6, rr * 0.3)); S.key(d, tl + 16, scale=(0.001,) * 3)
    S.cue("splash", F_POP + 18, vol=-18); S.cue("splash", F_POP + 24, vol=-20)

    # --- esponja triste, giro ---
    face_mood(S, fA, 128, "cold"); face_mood(S, fA, 150, "cold"); face_mood(S, fA, F_POP + 2, "wide")
    face_look(S, fA, 140, 0.035, 0.0); face_look(S, fA, F_POP + 2, 0.035, 0.0)
    face_mood(S, fA, 210, "sad"); face_look(S, fA, 214, 0.0, -0.025)
    S.key(sponge, 207, rot=(0, 0, 0), scale=(1, 1, 1)); S.key(sponge, 220, rot=(-0.14, 0, 0), scale=(1.02, 1.02, 0.94))
    S.key(sponge, 266, rot=(-0.14, 0, 0), scale=(1.02, 1.02, 0.94))
    face_blink(S, fA, 238)
    S.key(sponge, 274, rot=(0, 0, 0), scale=(1, 1, 1))                                                # respira antes de estrujar
    face_look(S, fA, 262, 0.0, 0.0); face_look(S, fA, 270, 0.0, 0.0)
    face_blink(S, fA, 280, hold=14)                                                                  # cierra los ojos con el esfuerzo
    S.key(sponge, 296, scale=(1.10, 1.07, 0.62), interp="BEZIER")                                    # un solo estrujón, lento
    S.key(sponge, 302, scale=(0.96, 0.96, 1.08)); S.key(sponge, 308, scale=(1, 1, 1))
    S.cue("slide_down", 276, vol=-14)
    swap(S, fA, fB, 304); face_look(S, fB, 304, 0.0, 0.0)
    face_blink(S, fB, 342)
    # pompita
    S.key(pit, 295, loc=(SX, 0.0, 0.16), scale=(0.001,) * 3)
    S.key(pit, 300, loc=(SX, 0.0, 0.22), scale=(0.25, 0.25, 0.25))
    S.key(pit, 308, loc=(SX, -0.005, 0.40), scale=(0.62, 0.62, 0.68))
    S.key(pit, 318, loc=(SX, -0.005, 0.36), scale=(0.6, 0.6, 0.6))
    S.key(pit, 328, loc=(SX, -0.005, 0.316), scale=(0.64, 0.64, 0.54))
    S.key(pit, 334, loc=(SX, -0.005, 0.318), scale=(0.6, 0.6, 0.6))
    S.cue("pop", 299, vol=-8); S.cue("tada", 326, vol=-5)
    face_look(S, qH, 300, 0.0, 0.0); face_look(S, qH, 330, 0.0, 0.0)
    face_wink(S, qH, 358)
    S.f = F_END
    return sponge


LEVELS = [(0, l1)]
