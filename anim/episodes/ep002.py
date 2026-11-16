"""ep002 — Objetos vivos: una cerilla calienta a un cubito de hielo (mesa, sin diálogo). Un solo nivel, sin rótulo."""
import math
import bpy

TITLE = "A Match Warms Up an Ice Cube"
CAPTION = None            # sin rótulo de IQ
ENV = "mesa"              # run_level.py crea Stage(env=ENV)
CUSTOM_CAMERA = True      # el nivel keyea su propia cámara (sin S.follow)

CX, MX = 0.20, -0.30      # x del cubito y de la cerilla
F_ON, F_OFF = 80, 351     # llama encendida / apagada por el abrazo
F_HUG = 351


def mkface(S, parent, k=1.0, gap=0.055, lid_col=None):
    """Cara de objeto: ojos, pupilas, párpados, cejas y boca. Devuelve dict de partes."""
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


def face_mood(S, P, f, mood):
    """mood: cold (tiembla, cejas preocupadas), smile, sad, neutral, wide"""
    k = P["k"]
    mo = {"cold": ((0.034, 0.008, 0.006), 14), "smile": ((0.05, 0.010, 0.032), -10), "sad": ((0.026, 0.008, 0.007), 22),
          "neutral": ((0.03, 0.008, 0.006), 0), "wide": ((0.02, 0.008, 0.02), 18)}[mood]
    S.key(P["mouth"], f, scale=tuple(v * k for v in mo[0]))
    for sx, b in zip((-1, 1), P["brows"]):
        S.key(b, f, rot=(0, math.radians(-mo[1] * sx), 0))


def face_blink(S, P, f, hold=0):
    for lid, r in P["lids"]:
        lx, ly = r * 1.1, r * 0.8
        S.key(lid, f - 1, scale=(lx, ly, 0.001)); S.key(lid, f + 1, scale=(lx, ly, r * 1.1))
        S.key(lid, f + 1 + 2 + hold, scale=(lx, ly, r * 1.1)); S.key(lid, f + 3 + 2 + hold, scale=(lx, ly, 0.001))


def face_look(S, P, f, dx, dz=0.0):
    r = P["r"]
    for sx, p in zip((-1, 1), P["pupils"]): S.key(p, f, loc=(P["gap"] * sx + dx, -r * 0.55, dz))


def shot(S, f, cam, tgt, lens=50, tg_interp="CONSTANT"):
    S.key(S.cam, f, loc=cam, interp="CONSTANT"); S.cam.data.lens = lens; S.cam.data.keyframe_insert("lens", frame=f)
    S.key(S.tgt, f, loc=tgt, interp=tg_interp)


def mist(S, name, alpha=0.55):
    return S.pmat(name, [(0.3, (0.92, 0.95, 1.0)), (0.7, (1.0, 1.0, 1.0))], scale=5, rough=0.9, bump=0.0, alpha=alpha)


def l1(S):
    S.cam.data.dof.aperture_fstop = 5.0; S.cam.data.dof.focus_object = S.tgt
    ice = S.pmat("hielo", [(0.3, (0.55, 0.80, 0.97)), (0.7, (0.72, 0.92, 1.0))], scale=4, rough=0.08, bump=0.04, alpha=0.7)
    water = S.pmat("charco", [(0.3, (0.40, 0.72, 0.95)), (0.7, (0.55, 0.85, 1.0))], scale=3, rough=0.05, bump=0.0, alpha=0.75)
    # --- objetos ---
    box = S.obj("cube", "caja", "red", (-0.64, 0.14, 0.26), (0.05, 0.08, 0.26), smooth=False)       # caja de cerillas de pie
    S.obj("cube", "tira", "black", (0.052, 0, 0.0), (0.004, 0.06, 0.2), parent=box, smooth=False)
    S.obj("cube", "etiqueta", "yellow", (-0.052, 0, 0.0), (0.004, 0.07, 0.10), parent=box, smooth=False)
    hielo = S.empty("hielo", (CX, 0, 0))
    block = S.empty("bloque", (0, 0, 0), parent=hielo)
    cube = S.obj("cube", "cubito", "white", (0, 0, 0.15), (0.15, 0.15, 0.15), parent=block); cube.data.materials[0] = ice
    for p in cube.data.polygons: p.use_smooth = False
    puddle = S.obj("cylinder", "charco", "water", (CX, -0.02, 0.006), (0.001, 0.001, 0.006), vertices=48); puddle.data.materials[0] = water
    cf = mkface(S, hielo, 1.0); S.key(cf["root"], 1, loc=(0, -0.158, 0.19))
    pf = mkface(S, puddle, 1.0); pf["root"].parent = hielo                                      # cara del charco (aparece al final del derretido)
    pf["root"].location = (0, -0.07, 0.05); S.key(pf["root"], 1, scale=(0.001,) * 3)
    drop = S.empty("gota", (CX, -0.05, 0.012)); S.key(drop, 1, scale=(0.001,) * 3)
    dm = S.obj("uv_sphere", "gota_cuerpo", "water", (0, 0, 0.08), (0.075, 0.075, 0.09), parent=drop); dm.data.materials[0] = water
    df = mkface(S, drop, 0.9, gap=0.05); df["root"].location = (0, -0.07, 0.10)
    face_mood(S, cf, 1, "cold"); face_mood(S, df, 1, "smile"); face_mood(S, pf, 1, "sad")

    m = S.actor(look={"kind": "cerilla", "color": "red"}, x=-1.0, size=0.6)
    headmat = S.mat("red").copy(); next(o for o in m.head.children if o.name.startswith("fosforo")).data.materials[0] = headmat
    bsdf = headmat.node_tree.nodes["Principled BSDF"]

    # --- cámara: primer plano del cubito / plano medio / (plano del vapor) ---
    shot(S, 1, (CX, -1.15, 0.30), (CX, 0, 0.20))
    shot(S, 49, (-0.12, -2.0, 0.42), (-0.12, 0, 0.32))
    shot(S, 241, (-0.02, -1.55, 0.36), (-0.02, 0, 0.30))
    shot(S, 337, (-0.05, -1.75, 0.42), (-0.05, 0, 0.36))
    shot(S, 400, (-0.05, -1.75, 0.42), (-0.05, 0, 0.36), tg_interp="BEZIER")
    shot(S, 470, (-0.05, -1.75, 0.80), (-0.05, 0, 1.15), tg_interp="BEZIER")

    # --- 0-2 s: primer plano, tirita con aliento ---
    for f in range(1, 50, 2):
        s = 1 if (f // 2) % 2 else -1
        S.key(hielo, f, loc=(CX + 0.007 * s, 0, 0), rot=(0, 0, 0.035 * s))
    S.cue("creak", 4, vol=-8); S.cue("creak", 30, vol=-10)
    face_blink(S, cf, 18); face_look(S, cf, 34, -0.02); face_look(S, cf, 46, -0.03)
    for i, (f0, dx) in enumerate(((6, -0.03), (26, 0.03))):                                        # nubecitas de aliento
        pf_ = S.obj("uv_sphere", "aliento", "white", (CX + dx, -0.20, 0.17), (0.001,) * 3); pf_.data.materials[0] = mist(S, "vaho", 0.5)
        S.key(pf_, f0, loc=(CX + dx, -0.20, 0.17), scale=(0.001,) * 3)
        S.key(pf_, f0 + 10, loc=(CX + dx * 1.5, -0.27, 0.19), scale=(0.05, 0.04, 0.04))
        S.key(pf_, f0 + 24, loc=(CX + dx * 2.5, -0.30, 0.27), scale=(0.001,) * 3)

    # --- 2-5 s: la cerilla entra, mira la caja, se frota y enciende ---
    S.f = 36; m.hop_to(-0.7, dur=8); m.hop_to(MX - 0.05, dur=8)                                    # ~f 36-64
    S.f = 64; m.look(-0.03, 0.0, 64); m.tilt(-12, 66); S.wait(8); m.blink(S.f)                       # mira la caja
    m.tilt(-30, 76); m.tilt(-4, 80, interp="BACK")                                                   # raspa la cabeza
    S.flame(m.head, F_ON, F_OFF)
    m.look(0.0, 0.0, 82); m.tilt(36, 92, interp="BACK"); m.look(0.03, 0.0, 94)                       # se inclina hacia el cubito
    face_mood(S, cf, 94, "cold"); face_mood(S, cf, 100, "smile"); face_blink(S, cf, 104); face_look(S, cf, 96, -0.03)
    S.key(hielo, 49, loc=(CX, 0, 0), rot=(0, 0, 0)); S.key(hielo, 52, loc=(CX, 0, 0), rot=(0, 0, 0))   # deja de tiritar al ver la luz

    # --- 5-10 s: se derrite ---
    S.cue("drain", 132, vol=-6); S.cue("drain", 176, vol=-8)
    ks = [(121, 1.0, 1.0, -0.158, 0.19), (150, 1.12, 0.82, -0.178, 0.17), (185, 1.32, 0.52, -0.205, 0.11), (225, 1.6, 0.2, -0.14, 0.06)]
    for f, kxy, kz, fy, fz in ks:
        S.key(block, f, scale=(kxy, kxy, kz)); S.key(cf["root"], f, loc=(0, fy, fz))
    S.key(block, 233, scale=(1.6, 1.6, 0.2)); S.key(block, 235, scale=(0.001,) * 3)                    # el cubo desaparece bajo el charco
    S.key(puddle, 125, scale=(0.001, 0.001, 0.006)); S.key(puddle, 175, scale=(0.20, 0.20, 0.006)); S.key(puddle, 232, scale=(0.30, 0.30, 0.006))
    face_mood(S, cf, 140, "smile"); face_mood(S, cf, 160, "sad"); face_mood(S, cf, 190, "sad")
    face_blink(S, cf, 150); face_look(S, cf, 150, 0.0, 0.0)                                           # duda: mira a cámara
    face_look(S, cf, 170, -0.035, 0.0)
    S.key(cf["root"], 236, scale=(1, 1, 1)); S.key(cf["root"], 238, scale=(0.001,) * 3)             # su cara pasa al charco
    S.key(pf["root"], 233, scale=(0.001,) * 3); S.key(pf["root"], 238, scale=(1, 1, 1), interp="BACK")
    face_mood(S, pf, 238, "sad"); face_blink(S, pf, 246)
    S.f = 124; m.look(0.03, 0.0, 124); m.tilt(40, 130)
    S.f = 160; m.hop_to(MX + 0.05, dur=6, sound="boing")                                             # acerca más la llama, sin entender
    m.tilt(50, S.f + 6, interp="BACK"); m.look(0.0, 0.0, S.f + 12); m.blink(S.f + 14)                # duda: mira a cámara (pausa antes del fracaso)
    m.tilt(50, 215); m.look(0.0, -0.01, 220)

    # --- 10-14 s: sólo el charco; la cerilla abanica; la gota nace ---
    for i, f in enumerate(range(246, 296, 5)):                                                       # abanica desesperada
        m.tilt(32 if i % 2 else 66, f, interp="BACK")
        if i % 3 == 0: S.cue("whoosh", f, vol=-12)
    m.tilt(52, 298, interp="BACK"); m.blink(300)
    S.key(pf["root"], 296, scale=(1, 1, 1)); S.key(pf["root"], 299, scale=(0.001,) * 3)             # el charco entrega los ojos a la gota
    S.cue("pop", 296, vol=-4)
    S.key(drop, 296, loc=(CX, -0.05, 0.012), scale=(0.001,) * 3); S.key(drop, 306, loc=(CX, -0.05, 0.012), scale=(1, 1, 1), interp="BACK")
    face_look(S, df, 312, -0.03, 0.0); face_blink(S, df, 322); face_mood(S, df, 300, "neutral"); face_mood(S, df, 330, "smile")

    # --- 14-17 s: la gota abraza y apaga la llama; silencio ---
    S.key(drop, 337, loc=(CX, -0.05, 0.012), scale=(1.15, 1.15, 0.8))
    S.key(drop, 343, loc=(0.08, -0.05, 0.50), scale=(0.9, 0.9, 1.2))
    hx, hz = MX + 0.05 + 0.318 * math.sin(math.radians(52)), 0.27 + 0.318 * math.cos(math.radians(52))
    S.key(drop, F_HUG, loc=(hx - 0.01, -0.07, hz - 0.07), scale=(1.5, 1.2, 0.7), interp="BACK")
    S.cue("whoosh", F_HUG, vol=0)
    S.key(drop, F_HUG + 8, loc=(hx - 0.01, -0.07, hz - 0.10), scale=(1.2, 1.1, 0.85))
    face_mood(S, df, F_HUG, "wide"); face_mood(S, df, F_HUG + 12, "smile")
    face_blink(S, df, F_HUG + 14)
    S.key(m.pivot, F_HUG, rot=(0, math.radians(52), 0)); m.tilt(40, F_HUG + 14)                       # la cerilla se queda quieta
    bsdf.inputs["Base Color"].default_value = (0.85, 0.12, 0.10, 1); bsdf.inputs["Base Color"].keyframe_insert("default_value", frame=F_HUG - 1)
    bsdf.inputs["Base Color"].default_value = (0.04, 0.03, 0.03, 1); bsdf.inputs["Base Color"].keyframe_insert("default_value", frame=F_HUG + 6)
    m.look(0.0, 0.0, F_HUG + 4); m.blink(F_HUG + 20); m.tilt(8, F_HUG + 30)

    # --- 17-21 s: del abrazo sube una nube con dos caritas ---
    nube = S.empty("nube", (hx - 0.02, -0.06, hz - 0.05)); S.key(nube, 1, scale=(0.001,) * 3)
    mm = mist(S, "vapor", 0.62)
    for i, (dx, dz, r) in enumerate(((0, 0, 0.09), (-0.09, -0.03, 0.07), (0.09, -0.02, 0.075), (0.03, 0.08, 0.07), (-0.05, 0.06, 0.06))):
        s_ = S.obj("uv_sphere", "vapor", "white", (dx, 0, dz), (r, r, r), parent=nube); s_.data.materials[0] = mm
    nf1 = mkface(S, nube, 0.8, gap=0.05); nf1["root"].location = (-0.07, -0.085, -0.01)
    nf2 = mkface(S, nube, 0.8, gap=0.05); nf2["root"].location = (0.08, -0.08, 0.0)
    for nf in (nf1, nf2): face_mood(S, nf, 1, "smile")
    S.key(drop, F_HUG + 30, scale=(1.2, 1.1, 0.85)); S.key(drop, F_HUG + 40, scale=(0.001,) * 3)       # la gota se vuelve vapor
    S.key(nube, F_HUG + 28, loc=(hx - 0.02, -0.06, hz - 0.05), scale=(0.001,) * 3)
    S.key(nube, F_HUG + 42, loc=(hx - 0.02, -0.06, hz + 0.05), scale=(0.8, 0.8, 0.8), interp="BACK")
    S.key(nube, F_HUG + 70, loc=(0.0, -0.06, 0.95), scale=(1.2, 1.2, 1.2))
    S.key(nube, F_HUG + 125, loc=(0.05, -0.06, 2.6), scale=(1.5, 1.5, 1.5))
    S.cue("pop", F_HUG + 32, vol=-4); S.cue("tada", F_HUG + 52, vol=-3)
    face_blink(S, nf1, F_HUG + 60); face_blink(S, nf2, F_HUG + 66)
    S.f = F_HUG + 120                                                                                    # remate; el kit añade +10 de margen
    return m


LEVELS = [(0, l1)]
