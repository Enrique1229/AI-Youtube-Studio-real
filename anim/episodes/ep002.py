"""ep002 — Objetos vivos: una cerilla calienta a un cubito de hielo (mesa, sin diálogo). Un solo nivel, sin rótulo."""
import math
import bpy

TITLE = "A Match Warms Up an Ice Cube"
CAPTION = None            # sin rótulo de IQ
SPEED = 1.0               # velocidad real: a 1.5x quedaría en 13 s y se pierde el gag
CTA = "follow for more"
ENV = "mesa"              # run_level.py crea Stage(env=ENV)
CUSTOM_CAMERA = True      # el nivel keyea su propia cámara (sin S.follow)

CX, MX = 0.20, -0.30      # x del cubito y de la cerilla
F_ON, F_OFF = 80, 335     # llama encendida / apagada por el abrazo
F_HUG = 335


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


def happy_face(S, P):
    """Sonrisa de verdad (medio aro) y cejas altas y relajadas: una esfera aplastada no sonríe."""
    k, r = P["k"], P["r"]
    P["mouth"].scale = (0.001, 0.001, 0.001)
    bpy.ops.mesh.primitive_torus_add(major_radius=0.026 * k, minor_radius=0.0045 * k, major_segments=24, minor_segments=8,
                                     location=(0, -0.004 * k, -r * 2.2), rotation=(math.radians(90), 0, 0))
    sm = bpy.context.object; sm.name = "sonrisa"; sm.parent = P["root"]; sm.data.materials.append(S.mat("black"))
    import bmesh
    bm = bmesh.new(); bm.from_mesh(sm.data)
    bmesh.ops.delete(bm, geom=[v for v in bm.verts if v.co.y > 0.002 * k], context="VERTS")     # se queda la mitad de abajo: ‿
    bm.to_mesh(sm.data); bm.free()
    for sx, br in zip((-1, 1), P["brows"]):
        br.location.z += r * 0.35; br.rotation_euler = (0, math.radians(12 * sx), 0)


def face_mood(S, P, f, mood):
    """mood: cold (tiembla, cejas preocupadas), smile, sad, neutral, wide"""
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
        S.key(lid, f + 1 + 2 + hold, scale=(lx, ly, r * 1.1)); S.key(lid, f + 3 + 2 + hold, scale=(lx, ly, 0.001))


def face_look(S, P, f, dx, dz=0.0):
    r = P["r"]
    for sx, p in zip((-1, 1), P["pupils"]): S.key(p, f, loc=(P["gap"] * sx + dx, -r * 0.55, dz))


def _kps(o):
    ad = o.animation_data
    if not ad or not ad.action: return
    act = ad.action
    if hasattr(act, "fcurves"): fcs = list(act.fcurves)
    else: fcs = [fc for l in act.layers for st in l.strips for cb in st.channelbags for fc in cb.fcurves]
    for fc in fcs:
        if fc.data_path == "location": yield from fc.keyframe_points


def shot(S, f, x, z, d=0.85, tz=None, interp="CONSTANT"):
    """Corte de cámara (lens fijo 50): centro x,z; d = distancia. d=0.85 -> ancho de cuadro ~0.6, alto ~1.07."""
    S.key(S.cam, f, loc=(x, -d * 1.75, z), interp=interp)   # el sensor encaja por la altura: ancho = 0.405*dist
    S.key(S.tgt, f, loc=(x, 0, z if tz is None else tz), interp=interp)
    for o in (S.cam, S.tgt):                                  # fuerza la interpolación del último key (la preferencia de Blender no siempre se aplica)
        for kp in _kps(o):
            if int(round(kp.co[0])) == f: kp.interpolation = interp


def mist(S, name, alpha=0.55):
    return S.pmat(name, [(0.3, (0.92, 0.95, 1.0)), (0.7, (1.0, 1.0, 1.0))], scale=5, rough=0.9, bump=0.0, alpha=alpha)


def l1(S):
    S.cam.data.dof.aperture_fstop = 5.0; S.cam.data.dof.focus_object = S.tgt
    ice = S.pmat("hielo", [(0.3, (0.40, 0.68, 0.95)), (0.7, (0.58, 0.82, 1.0))], scale=4, rough=0.08, bump=0.04, alpha=0.8)
    water = S.pmat("charco", [(0.3, (0.20, 0.55, 0.92)), (0.7, (0.35, 0.70, 1.0))], scale=3, rough=0.05, bump=0.0, alpha=0.85)
    for m_, tr, ior, rg in ((ice, 0.85, 1.31, 0.12), (water, 0.9, 1.33, 0.03)):   # hielo y agua translúcidos de verdad (transmisión)
        b_ = m_.node_tree.nodes["Principled BSDF"]
        b_.inputs["Alpha"].default_value = 1.0; b_.inputs["Transmission Weight"].default_value = tr
        b_.inputs["IOR"].default_value = ior; b_.inputs["Roughness"].default_value = rg
        if "Subsurface Weight" in b_.inputs: b_.inputs["Subsurface Weight"].default_value = 0.15
    # --- objetos ---
    box = S.obj("cube", "caja", "red", (-0.64, 0.14, 0.26), (0.05, 0.08, 0.26), smooth=False)       # caja de cerillas de pie
    S.obj("cube", "tira", "black", (0.052, 0, 0.0), (0.004, 0.06, 0.2), parent=box, smooth=False)
    S.obj("cube", "tira_f", "black", (0, -0.082, -0.1), (0.04, 0.004, 0.09), parent=box, smooth=False)
    S.obj("cube", "etiqueta", "yellow", (-0.052, 0, 0.0), (0.004, 0.07, 0.10), parent=box, smooth=False)
    hielo = S.empty("hielo", (CX, 0, 0))
    block = S.empty("bloque", (0, 0, 0), parent=hielo)
    cube = S.obj("cube", "cubito", "white", (0, 0, 0.15), (0.15, 0.15, 0.15), parent=block); cube.data.materials[0] = ice
    bv = cube.modifiers.new("bisel", "BEVEL"); bv.width = 0.18; bv.segments = 4; bv.limit_method = "NONE"   # aristas redondeadas de hielo
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
    for b in (o for o in m.head.children if o.name.startswith("ceja")):                          # cejas amables (por defecto parecen enfadadas)
        S.key(b, 1, rot=(0, math.radians(9 * (1 if b.location.x > 0 else -1)), 0))
    headmat = S.mat("red").copy(); next(o for o in m.head.children if o.name.startswith("fosforo")).data.materials[0] = headmat
    bsdf = headmat.node_tree.nodes["Principled BSDF"]

    # --- cámara: cortes entre planos cerrados (lens 50); el plano abierto solo sitúa ~1 s ---
    S.cam.data.lens = 50; S.cam.data.keyframe_insert("lens", frame=1)
    shot(S, 1, CX, 0.24)                       # cubito tiritando
    shot(S, 36, -0.25, 0.50, d=1.7)            # abierto: entra la cerilla (1 s)
    shot(S, 62, -0.32, 0.46)                   # cerilla mira la caja, raspa y se enciende
    shot(S, 94, 0.09, 0.30, d=0.95)                    # el cubito sonríe y empieza a derretirse
    shot(S, 150, -0.10, 0.44)                  # cerilla duda, mira a cámara
    shot(S, 190, 0.09, 0.28, d=0.92)             # cubito aplastándose
    shot(S, 238, 0.29, 0.11, d=0.55)             # charco con cara
    shot(S, 266, -0.10, 0.40)                  # cerilla abanica
    shot(S, 280, 0.27, 0.13, d=0.55)             # nace la gota y mira
    shot(S, 318, 0.08, 0.48)                   # salto y abrazo
    shot(S, F_HUG + 34, 0.0, 0.48, interp="BEZIER")
    shot(S, F_HUG + 75, 0.0, 0.70, interp="BEZIER")   # sigue la nube hacia arriba

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
    for i, f in enumerate(range(246, 276, 5)):                                                       # abanica desesperada
        m.tilt(32 if i % 2 else 66, f, interp="BACK")
        if i % 3 == 0: S.cue("whoosh", f, vol=-12)
    m.tilt(52, 278, interp="BACK"); m.blink(280)
    S.key(pf["root"], 280, scale=(1, 1, 1)); S.key(pf["root"], 283, scale=(0.001,) * 3)             # el charco entrega los ojos a la gota
    S.cue("pop", 280, vol=-4)
    S.key(drop, 280, loc=(CX, -0.05, 0.012), scale=(0.001,) * 3); S.key(drop, 290, loc=(CX, -0.05, 0.012), scale=(1, 1, 1), interp="BACK")
    face_look(S, df, 296, -0.03, 0.0); face_blink(S, df, 306); face_mood(S, df, 284, "neutral"); face_mood(S, df, 314, "smile")

    # --- 14-17 s: la gota abraza y apaga la llama; silencio ---
    S.key(drop, 321, loc=(CX, -0.05, 0.012), scale=(1.15, 1.15, 0.8))
    S.key(drop, 327, loc=(0.08, -0.05, 0.36), scale=(0.9, 0.9, 1.2))
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
    mm = mist(S, "vapor", 0.9)
    for i, (dx, dz, r) in enumerate(((0, 0.01, 0.10), (-0.13, -0.02, 0.085), (0.13, -0.02, 0.085), (0.0, 0.09, 0.08), (-0.07, 0.07, 0.07), (0.07, 0.07, 0.07))):
        s_ = S.obj("uv_sphere", "vapor", "white", (dx, 0, dz), (r, r, r), parent=nube); s_.data.materials[0] = mm
    nf1 = mkface(S, nube, 0.75, gap=0.04); nf1["root"].location = (-0.13, -0.088, -0.01)
    nf2 = mkface(S, nube, 0.75, gap=0.04); nf2["root"].location = (0.13, -0.088, -0.01)
    for nf in (nf1, nf2): happy_face(S, nf)                                                          # remate: caras FELICES (sonrisa en arco)
    S.key(drop, F_HUG + 30, scale=(1.2, 1.1, 0.85)); S.key(drop, F_HUG + 40, scale=(0.001,) * 3)       # la gota se vuelve vapor
    S.key(nube, F_HUG + 28, loc=(hx - 0.02, -0.06, hz - 0.05), scale=(0.001,) * 3)
    S.key(nube, F_HUG + 42, loc=(hx - 0.02, -0.06, hz + 0.05), scale=(0.8, 0.8, 0.8), interp="BACK")
    S.key(nube, F_HUG + 60, loc=(0.0, -0.06, 0.82), scale=(1.2, 1.2, 1.2))
    S.key(nube, F_HUG + 75, loc=(0.02, -0.06, 0.92), scale=(1.25, 1.25, 1.25))
    S.cue("pop", F_HUG + 32, vol=-4); S.cue("tada", F_HUG + 48, vol=-3)
    face_blink(S, nf1, F_HUG + 60); face_blink(S, nf2, F_HUG + 66)
    m.blink(F_HUG + 62)
    S.f = F_HUG + 75                                                                                    # remate; el kit añade +10 de margen
    return m


LEVELS = [(0, l1)]
