"""ep009 — Cada nivel de IQ ante una nube de lluvia personal. Parque junto al río: una nubecita simpática sigue a un hombre y le llueve solo a él.
-450 corre y frena en seco (la nube le pasa por delante y vuelve); -80 salta muy alto, la nube sube con él y cae suave al suelo (charco);
120 se esconde bajo el diminuto árbol (la nube se estira y se coloca encima: una sola gota por la nariz); 900 arranca el banco y lo lleva de tejado;
5400 se queda quieto, la nube riega el parterre de flores marchitas, que se abren; él se sienta en el banco, seco, y saluda."""
import math
import random
import bpy
from mathutils import Vector

TITLE = "Every IQ Level Stays Dry Under a Personal Rain Cloud"
ONSCREEN = "Every IQ level vs a rain cloud"

BNX, BNY = -5.0, 0.66          # banco
FBX, FBY = -3.35, 1.50         # parterre
TRX, TRY = -7.4, 0.55          # arbolito
HOVER = 2.7                    # altura del centro de la nube sobre la cabeza


def R(d): return math.radians(d)


def ss(t): t = max(0.0, min(1.0, t)); return t * t * (3 - 2 * t)


def lerp(a, b, t): return a + (b - a) * t


# ------------------------------------------------------------------ materiales y utilidades
def cmat(S, name, rgb, rough=0.6, alpha=None):
    k = "c_" + name
    if k in S.mats: return S.mats[k]
    m = bpy.data.materials.new(k); m.use_nodes = True
    b = m.node_tree.nodes["Principled BSDF"]
    b.inputs["Base Color"].default_value = (*rgb, 1); b.inputs["Roughness"].default_value = rough
    if alpha is not None:
        b.inputs["Alpha"].default_value = alpha
        try: m.blend_method = "BLEND"
        except Exception: pass
    S.mats[k] = m
    return m


def pose(S, a, f, lean=0, thigh=(0, 0), knee=(0, 0), arm=(0, 0), elbow=(-12, -12), spread=(0, 0), interp="BEZIER"):
    """Pose completa (índice 0 = lado -x del personaje). Muslo negativo = adelante; brazo negativo = adelante/arriba."""
    for i in (0, 1):
        S.key(a.legs[i], f, rot=(R(thigh[i]), 0, 0), interp=interp); S.key(a.knees[i], f, rot=(R(knee[i]), 0, 0), interp=interp)
        S.key(a.arms[i], f, rot=(R(arm[i]), R(spread[i]), 0), interp=interp); S.key(a.elbows[i], f, rot=(R(elbow[i]), 0, 0), interp=interp)
    S.key(a.pivot, f, rot=(R(lean), 0, 0), interp=interp)


def head_pos(S, a, f):
    S.sc.frame_set(f); bpy.context.view_layer.update()
    return a.head.matrix_world.translation.copy()


def dust(S, x, z, f, n=5, spread=0.4, size=0.09, y=-0.25, seed=0, rise=0.25):
    rr = random.Random(seed + int(x * 10) + f); m = S.mat("khaki")
    for i in range(n):
        d = S.obj("uv_sphere", "polvo", "khaki", (x, y, z), (0.001,) * 3, segments=8, ring_count=6); d.data.materials[0] = m
        dx = rr.uniform(-spread, spread); sz = size * rr.uniform(0.7, 1.3); dy = rr.uniform(-0.15, 0.1)
        S.key(d, f - 1, loc=(x, y + dy, z), scale=(0.001,) * 3)
        S.key(d, f + 4, loc=(x + dx * 0.6, y + dy, z + rise * 0.4), scale=(sz, sz * 0.8, sz * 0.8))
        S.key(d, f + 15, loc=(x + dx, y + dy, z + rise), scale=(sz * 1.3, sz, sz))
        S.key(d, f + 20, loc=(x + dx * 1.1, y + dy, z + rise * 1.1), scale=(0.001,) * 3)


def ground_splash(S, x, y, f, n=9, big=1.0):
    """Gotitas que saltan suave desde el suelo (charco): arco corto y vuelven a caer."""
    rr = random.Random(int(x * 7) + f); wm = S.mat("water")
    for i in range(n):
        d = S.obj("uv_sphere", "gotita", "water", (x, y, 0.03), (0.001,) * 3, segments=8, ring_count=6); d.data.materials[0] = wm
        ang = rr.uniform(0, 2 * math.pi); rad = rr.uniform(0.2, 0.55) * big; hh = rr.uniform(0.18, 0.4) * big; sz = rr.uniform(0.022, 0.035)
        px, py = x + math.cos(ang) * rad, y + math.sin(ang) * rad * 0.55
        S.key(d, f - 1, loc=(x, y, 0.03), scale=(0.001,) * 3)
        S.key(d, f + 1, loc=(x + (px - x) * 0.1, y + (py - y) * 0.1, 0.06), scale=(sz, sz, sz * 1.3))
        S.key(d, f + 6, loc=(x + (px - x) * 0.6, y + (py - y) * 0.6, 0.03 + hh), scale=(sz, sz, sz * 1.2))
        S.key(d, f + 12, loc=(px, py, 0.03), scale=(sz, sz, sz))
        S.key(d, f + 13, loc=(px, py, 0.02), scale=(0.001,) * 3)


def puddle(S, x, y, f0, f1, r, ry=0.55):
    """Charco que crece de f0 a f1 (aplanado, brillante)."""
    m = cmat(S, "charco", (0.20, 0.32, 0.42), rough=0.03)
    o = S.obj("cylinder", "charco", "white", (x, y, 0.016), (0.001, 0.001, 0.004), vertices=28, smooth=False); o.data.materials[0] = m
    S.key(o, f0 - 1, loc=(x, y, 0.016), scale=(0.001, 0.001, 0.004))
    S.key(o, f1, loc=(x, y, 0.016), scale=(r, r * ry, 0.004))
    for k in range(3):                       # el charco "respira" mientras le llueve
        S.key(o, f1 + 8 + k * 8, loc=(x, y, 0.016), scale=(r * (1.03 if k % 2 == 0 else 1.0), r * ry * (1.03 if k % 2 == 0 else 1.0), 0.004))
    return o


def wet(S, a, keys):
    """Pelo mojado: oscurece el color base del pelo. keys = [(fotograma, factor)]."""
    try:
        m = S.mat(S.look["hair_color"]); b = m.node_tree.nodes["Principled BSDF"]
        c0 = tuple(b.inputs["Base Color"].default_value)[:3]
        for f, k in keys:
            b.inputs["Base Color"].default_value = (c0[0] * k, c0[1] * k, c0[2] * (k ** 0.8), 1)
            b.inputs["Base Color"].keyframe_insert("default_value", frame=f)
        b.inputs["Base Color"].default_value = (*c0, 1)
    except Exception as e:
        print("[ep009] pelo mojado no animado:", e)


def drips(S, a, frames):
    """Gotas que resbalan por la sien y gotas que caen de la barbilla."""
    wm = S.mat("water")
    for k, f in enumerate(frames):
        p = head_pos(S, a, f)
        sx = 0.17 if a.yaw > 0 else -0.17
        if k % 2 == 0:       # sien -> mejilla
            d = S.obj("uv_sphere", "gota_cara", "water", (p.x + sx, p.y - 0.12, p.z + 0.12), (0.001,) * 3, segments=8, ring_count=6)
            S.key(d, f - 1, loc=(p.x + sx, p.y - 0.12, p.z + 0.12), scale=(0.001,) * 3)
            S.key(d, f + 2, loc=(p.x + sx, p.y - 0.12, p.z + 0.1), scale=(0.022, 0.022, 0.032))
            S.key(d, f + 11, loc=(p.x + sx * 1.1, p.y - 0.12, p.z - 0.2), scale=(0.02, 0.02, 0.038))
            S.key(d, f + 16, loc=(p.x + sx * 1.2, p.y - 0.12, p.z - 0.5), scale=(0.001,) * 3)
        else:                # barbilla -> suelo
            q = (p.x - 0.03, p.y - 0.17, p.z - 0.27)
            d = S.obj("uv_sphere", "gota_barbilla", "water", q, (0.001,) * 3, segments=8, ring_count=6)
            S.key(d, f - 1, loc=q, scale=(0.001,) * 3)
            S.key(d, f + 3, loc=q, scale=(0.026, 0.026, 0.034))
            S.key(d, f + 5, loc=(q[0], q[1], q[2] - 0.08), scale=(0.022, 0.022, 0.04))
            S.key(d, f + 12, loc=(q[0], q[1], max(0.1, q[2] - 1.2)), scale=(0.02, 0.02, 0.045))
            S.key(d, f + 13, loc=(q[0], q[1], max(0.1, q[2] - 1.2)), scale=(0.001,) * 3)


# ------------------------------------------------------------------ la nube
class Cloud: pass


def make_cloud(S, loc):
    """Nube con volumen suave (ico_spheres agrupadas) y cara simpática: ojos, cejas, boca, sonrisa y mofletes ocultos hasta el remate."""
    cm = S.pmat("nube", [(0.3, (0.36, 0.43, 0.55)), (0.6, (0.45, 0.52, 0.64)), (0.85, (0.54, 0.61, 0.73))], scale=2.5, rough=0.95, bump=0.12, detail=4)
    cl = Cloud(); C = cl.C = S.empty("nube", loc)
    puffs = ((0, 0, 0, 0.46), (-0.44, 0.02, -0.06, 0.34), (0.44, 0.02, -0.06, 0.35), (-0.20, 0.06, 0.26, 0.34), (0.22, 0.06, 0.28, 0.32),
             (-0.72, 0.05, -0.14, 0.22), (0.74, 0.05, -0.14, 0.23), (0, 0.22, -0.02, 0.38), (0, -0.10, -0.12, 0.36), (-0.02, 0.0, 0.42, 0.22))
    for (dx, dy, dz, r) in puffs:
        o = S.obj("ico_sphere", "puff", "white", (dx, dy, dz), (r, r * 0.9, r * 0.85), parent=C, subdivisions=3); o.data.materials[0] = cm
    cl.eyes, cl.pupils, cl.brows, cl.cheeks = [], [], [], []
    for sx in (-1, 1):
        cl.eyes.append(S.obj("uv_sphere", "nube_ojo", "white", (0.15 * sx, -0.385, 0.08), (0.085, 0.06, 0.10), parent=C, segments=14, ring_count=8))
        cl.pupils.append(S.obj("uv_sphere", "nube_pupila", "black", (0.15 * sx, -0.432, 0.07), (0.045, 0.025, 0.055), parent=C, segments=10, ring_count=6))
        cl.brows.append(S.obj("cube", "nube_ceja", "navy", (0.15 * sx, -0.415, 0.22), (0.075, 0.014, 0.014), rot=(0, 0, 0), parent=C, smooth=False))
        ch = S.obj("uv_sphere", "nube_moflete", "pink", (0.27 * sx, -0.36, -0.04), (0.001,) * 3, parent=C, segments=10, ring_count=6)
        ch.data.materials[0] = cmat(S, "moflete", (0.95, 0.55, 0.62), rough=0.9); cl.cheeks.append(ch)
    cl.mouth = S.obj("uv_sphere", "nube_boca", "black", (0, -0.425, -0.10), (0.04, 0.012, 0.02), parent=C, segments=10, ring_count=6)
    cl.smile = []
    for i in range(9):
        t = (i - 4) / 4.0; x = 0.14 * t; z = -0.165 + 0.075 * t * t
        cl.smile.append(S.obj("uv_sphere", "nube_sonrisa", "black", (x, -0.422, z), (0.001,) * 3, parent=C, segments=8, ring_count=5))
    cl.rest = {}
    mood(S, cl, 1, "sad")
    return cl


def mood(S, cl, f, kind):
    """sad: cejas preocupadas, boquita; ok: cejas neutras; happy: cejas arriba, sonrisa, mofletes."""
    deg = {"sad": 14, "ok": 4, "happy": -12, "shy": 20}[kind]
    for sx, b in zip((-1, 1), cl.brows):
        S.key(b, f, loc=(0.15 * sx, -0.415, 0.22 + (0.03 if kind == "happy" else 0.0)), rot=(0, R(deg * sx), 0))
    sm = kind == "happy"
    for o in cl.smile: S.key(o, f, scale=((0.016,) * 3 if sm else (0.001,) * 3))
    S.key(cl.mouth, f, scale=((0.001,) * 3 if sm else (0.04, 0.012, 0.02 if kind != "shy" else 0.012)))
    for c in cl.cheeks: S.key(c, f, scale=((0.07, 0.02, 0.045) if sm else (0.001,) * 3))


def cloud_look(S, cl, f, dx=0.0, dz=0.0):
    for sx, p in zip((-1, 1), cl.pupils): S.key(p, f, loc=(0.15 * sx + dx, -0.432, 0.07 + dz))


def cloud_blink(S, cl, f):
    for e in cl.eyes:
        S.key(e, f - 1, scale=(0.085, 0.06, 0.10)); S.key(e, f + 1, scale=(0.085, 0.06, 0.012)); S.key(e, f + 3, scale=(0.085, 0.06, 0.10))


def cloud_squash(S, cl, f, s=(1, 1, 1)):
    S.key(cl.C, f, scale=s)


# ------------------------------------------------------------------ lluvia
def make_rain(S, C, f0, f1, n=28, rx=0.6, ry=0.3, off=(0, 0, -0.38), p=8, seed=1):
    """Muchas gotas finas translúcidas (cilindros alargados) que caen en bucle. El vacío de escala Z del empty controla hasta dónde llueve."""
    Rr = S.empty("lluvia", off, parent=C)
    rm = cmat(S, "gota", (0.55, 0.78, 0.98), rough=0.1, alpha=0.75)
    rnd = random.Random(seed)
    for i in range(n):
        x = rnd.uniform(-rx, rx); y = rnd.uniform(-ry, ry)
        d = S.obj("cylinder", "gota", "white", (x, y, 0), (0.013, 0.013, 0.14), parent=Rr, vertices=6, smooth=False); d.data.materials[0] = rm
        c = f0 - rnd.randrange(p + 2)
        while c <= f1:
            S.key(d, c, loc=(x, y, -0.05), scale=(0.013, 0.013, 0.001), interp="LINEAR")
            S.key(d, c + 1, loc=(x, y, -0.08), scale=(0.013, 0.013, 0.14), interp="LINEAR")
            S.key(d, c + p, loc=(x, y, -2.3), scale=(0.013, 0.013, 0.14), interp="LINEAR")
            S.key(d, c + p + 1, loc=(x, y, -2.3), scale=(0.013, 0.013, 0.001), interp="LINEAR")
            c += p + 2
    return Rr


def track(S, cl, a, f0, f1, hover=HOVER, lag=3, off=None, rain=(), step=2, pos=None, bob=0.035):
    """La nube sigue al actor (muestreo cada `step` fotogramas, con retraso). off(f) -> (dx,dy,dz); pos(f, p, default) -> (x,y,z) la reemplaza.
    rain = [(empty_lluvia, fn)] con fn(f) -> z del suelo donde acaba la lluvia (None = sin lluvia)."""
    fr = list(range(f0, f1, step)) + [f1]
    for f in fr:
        g = max(1, f - lag)
        S.sc.frame_set(g); bpy.context.view_layer.update()
        p = a.root.matrix_world.translation.copy()
        dx, dy, dz = off(f) if off else (0, 0, 0)
        d = (p.x + dx, p.y + dy, hover + 0.9 * max(0.0, p.z) + dz + bob * math.sin(f * 0.19))
        x, y, z = pos(f, p, d) if pos else d
        S.key(cl.C, f, loc=(x, y, z), interp="LINEAR")
        for Rr, fn in rain:
            zt = fn(f)
            sz = 0.001 if zt is None else max(0.04, (z - 0.38 - zt) / 2.3)
            S.key(Rr, f, scale=((0.001, 0.001, 0.001) if zt is None else (1, 1, sz)), interp="LINEAR")


def blinks(S, a, frames):
    for f in frames: a.blink(f)


# ------------------------------------------------------------------ escenario
def build_set(S, flowers=True):
    """Sendero de tierra, hierba, banco de madera con patas, arbolito, parterre de flores marchitas, arbustos y piedrecitas."""
    rnd = random.Random(9)
    ground = S.mats["p_suelo"]
    dirt = S.pmat("tierra", [(0.30, (0.40, 0.27, 0.15)), (0.55, (0.50, 0.36, 0.21)), (0.75, (0.34, 0.23, 0.13))], scale=9, rough=0.95, bump=0.5)
    wood = S.pmat("madera_banco", [(0.25, (0.36, 0.20, 0.09)), (0.50, (0.50, 0.31, 0.15)), (0.80, (0.30, 0.17, 0.08))], scale=16, rough=0.7, bump=0.35, detail=8)
    iron = S.pmat("hierro_banco", [(0.3, (0.10, 0.11, 0.12)), (0.7, (0.2, 0.21, 0.22))], scale=8, rough=0.5, bump=0.1)
    stone = S.pmat("guijarro", [(0.25, (0.30, 0.29, 0.28)), (0.65, (0.47, 0.45, 0.42))], scale=4.0, rough=0.92, bump=1.0, detail=10)
    leafm = S.pmat("arbusto", [(0.25, (0.10, 0.26, 0.06)), (0.55, (0.20, 0.40, 0.09)), (0.85, (0.34, 0.48, 0.12))], scale=9, rough=0.8, bump=0.5, detail=8)
    bark = S.pmat("corteza_p", [(0.3, (0.20, 0.13, 0.07)), (0.7, (0.36, 0.26, 0.15))], scale=26, rough=0.9, bump=0.8, detail=8)
    soil = S.pmat("tierra_oscura", [(0.3, (0.17, 0.10, 0.05)), (0.7, (0.27, 0.17, 0.09))], scale=14, rough=0.95, bump=0.6, detail=6)
    stem = S.pmat("tallo", [(0.3, (0.15, 0.40, 0.08)), (0.7, (0.25, 0.52, 0.12))], scale=3, rough=0.7, bump=0.0)
    stemd = cmat(S, "tallo_seco", (0.36, 0.30, 0.13), rough=0.9)
    brown = cmat(S, "petalo_seco", (0.34, 0.20, 0.09), rough=0.95)
    browd = cmat(S, "petalo_seco2", (0.42, 0.30, 0.13), rough=0.95)

    def O(prim, name, mat, loc, scale=(1, 1, 1), rot=(0, 0, 0), parent=None, smooth=True, **kw):
        o = S.obj(prim, name, "white", loc, scale, rot, parent, smooth, **kw); o.data.materials[0] = mat; return o

    bpy.data.objects["prado_cerca"].modifiers.clear()
    bl = bpy.data.objects["brizna"]
    regs = (("hA", -9.2, -2.55, -6.5, -0.66, 13500), ("hB", -9.2, -6.3, 0.66, 3.0, 3200), ("hC", -6.3, -3.95, 1.3, 3.0, 2300),
            ("hD", -3.75, -2.55, 0.66, 1.2, 800), ("hE", -3.95, -2.55, 1.8, 3.0, 1100))
    for k, (nm, x0, x1, y0, y1, n) in enumerate(regs):
        bpy.ops.mesh.primitive_plane_add(size=1, location=((x0 + x1) / 2, (y0 + y1) / 2, 0.003)); pr = bpy.context.object; pr.name = nm
        pr.scale = (x1 - x0, y1 - y0, 1); pr.data.materials.append(ground); S._scatter(pr, bl, n, 31 + k)

    # sendero + explanada del banco + manchas
    O("cube", "sendero", dirt, (-6.2, 0, 0.008), (3.7, 0.64, 0.008), smooth=False)
    O("cube", "explanada", dirt, (BNX, 0.78, 0.011), (1.3, 0.40, 0.007), smooth=False)
    for i in range(16):
        x = rnd.uniform(-9.6, -2.8); y = -rnd.uniform(0.55, 0.78)
        O("cylinder", "mancha", dirt, (x, y, 0.009), (rnd.uniform(0.18, 0.4), rnd.uniform(0.1, 0.2), 0.006), vertices=14, smooth=False)
    for i in range(34):
        x = rnd.uniform(-9.5, -2.9); y = rnd.uniform(-0.62, 0.62); r_ = rnd.uniform(0.018, 0.045)
        O("ico_sphere", "guijarro", stone, (x, y, 0.012 + r_ * 0.3), (r_ * 1.3, r_, r_ * 0.7), subdivisions=1)

    # banco de madera con patas de hierro
    B = S.empty("banco", (BNX, BNY, 0.0))
    for yy in (-0.17, -0.06, 0.05, 0.16):
        O("cube", "asiento", wood, (0, yy, 0.50), (0.95, 0.050, 0.020), parent=B, smooth=False)
    for zz in (0.78, 0.93):
        O("cube", "respaldo", wood, (0, 0.24, zz), (0.95, 0.018, 0.058), rot=(R(-12), 0, 0), parent=B, smooth=False)
    for sx in (-1, 1):
        O("cube", "pata_d", iron, (0.80 * sx, -0.14, 0.25), (0.030, 0.026, 0.25), parent=B, smooth=False)
        O("cube", "pata_t", iron, (0.80 * sx, 0.22, 0.25), (0.030, 0.026, 0.25), parent=B, smooth=False)
        O("cube", "apoyabrazos", iron, (0.88 * sx, 0.04, 0.68), (0.026, 0.22, 0.020), parent=B, smooth=False)
        O("cube", "poste", iron, (0.88 * sx, 0.20, 0.60), (0.024, 0.024, 0.20), parent=B, smooth=False)
    # huecos de las patas (se ven al arrancar el banco)
    holes = []
    for sx in (-1, 1):
        for yy in (-0.14, 0.22):
            h = O("cylinder", "hueco", soil, (BNX + 0.80 * sx, BNY + yy, 0.011), (0.001, 0.001, 0.003), vertices=12, smooth=False); holes.append(h)

    # arbolito: tronco con corteza y copa pequeña de bolas de hojas
    tr = O("cylinder", "tronco_peque", bark, (TRX, TRY, 1.1), (0.085, 0.085, 1.1), vertices=10)
    O("cylinder", "rama", bark, (TRX + 0.16, TRY, 2.25), (0.035, 0.035, 0.22), rot=(0, R(35), 0), vertices=8)
    canopy = S.empty("copa", (TRX, TRY, 2.5))
    for (dx, dy, dz, r) in ((0, 0, 0, 0.5), (-0.42, 0.05, -0.05, 0.36), (0.42, -0.02, -0.04, 0.38), (0.1, 0.2, 0.2, 0.34), (-0.15, -0.18, 0.12, 0.33), (0.26, 0.08, 0.28, 0.26)):
        O("ico_sphere", "copa_p", leafm, (dx, dy, dz), (r, r, r * 0.78), parent=canopy, subdivisions=3)
    for i in range(9):
        a_ = rnd.uniform(0, 6.28); O("ico_sphere", "hoja_p", leafm, (0.55 * math.cos(a_), 0.4 * math.sin(a_), rnd.uniform(-0.1, 0.25)), (0.12,) * 3, parent=canopy, subdivisions=1)

    # arbustos y flores sueltas
    for (x, y, sc) in ((-8.8, 1.9, 0.7), (-6.6, 2.0, 0.6), (-5.4, 2.1, 0.7), (-2.8, 2.5, 0.8), (-9.0, -1.6, 0.5)):
        for j in range(5):
            O("ico_sphere", "arb", leafm, (x + rnd.uniform(-0.35, 0.35) * sc * 2, y + rnd.uniform(-0.25, 0.25), 0.28 * sc + rnd.uniform(0, 0.25) * sc), (sc * rnd.uniform(0.35, 0.55),) * 3, subdivisions=2)
    cols = ("white", "pink", "yellow", "coral", "purple", "red")
    for _ in range(24):
        x, y = rnd.uniform(-9.3, -2.8), rnd.uniform(-1.5, -0.85); h = rnd.uniform(0.16, 0.30); c = rnd.choice(cols)
        O("cylinder", "tallo_s", stem, (x, y, h / 2), (0.007, 0.007, h / 2), vertices=6, smooth=False)
        O("uv_sphere", "flor_s", S.mat(c), (x, y - 0.004, h + 0.005), (0.035, 0.03, 0.02), segments=10, ring_count=6)

    # parterre: tierra elevada y flores marchitas (caídas, marrones) que podrán abrirse
    O("cube", "parterre", soil, (FBX, FBY, 0.04), (0.66, 0.30, 0.04), smooth=False)
    for sx in (-1, 1): O("cube", "borde_p", wood, (FBX + 0.68 * sx, FBY, 0.07), (0.025, 0.31, 0.07), smooth=False)
    for sy in (-1, 1): O("cube", "borde_p2", wood, (FBX, FBY + 0.31 * sy, 0.07), (0.69, 0.025, 0.07), smooth=False)
    fl = []
    bloom_cols = ("red", "pink", "yellow", "coral", "purple", "white", "yellow", "red", "pink", "coral", "purple")
    for i in range(11):
        x = FBX - 0.56 + 0.112 * i; y = FBY + (0.12 if i % 2 else -0.10) + rnd.uniform(-0.04, 0.04)
        h = rnd.uniform(0.34, 0.46)
        F = S.empty("flor", (x, y, 0.07))
        s_d = O("cylinder", "tallo_marchito", stemd, (0, 0, h / 2), (0.009, 0.009, h / 2), parent=F, vertices=6, smooth=False)
        s_g = O("cylinder", "tallo_vivo", stem, (0, 0, h / 2), (0.001, 0.001, h / 2), parent=F, vertices=6, smooth=False)
        for sx in (-1, 1):
            O("ico_sphere", "hojita", stem, (0.05 * sx, 0, h * 0.35), (0.05, 0.016, 0.018), rot=(0, R(25 * sx), 0), parent=F, subdivisions=1)
        HD = S.empty("cabeza_flor", (0, 0, h), parent=F)
        wil = S.empty("marchita", (0, 0, 0), parent=HD)
        O("uv_sphere", "centro_seco", brown, (0, 0, 0), (0.035, 0.035, 0.03), parent=wil, segments=8, ring_count=6)
        for k in range(6):
            ang = k * math.pi / 3
            O("uv_sphere", "petalo_seco", (browd if k % 2 else brown), (0.058 * math.cos(ang), 0.058 * math.sin(ang), -0.045), (0.04, 0.016, 0.01), rot=(0, R(55), ang), parent=wil, segments=8, ring_count=5)
        opn = S.empty("abierta", (0, 0, 0), parent=HD); opn.scale = (0.001,) * 3
        cc = bloom_cols[i]
        O("uv_sphere", "centro", S.mat("orange" if cc == "yellow" else "yellow"), (0, -0.01, 0.0), (0.035, 0.03, 0.03), parent=opn, segments=10, ring_count=6)
        for k in range(8):
            ang = k * math.pi / 4
            O("uv_sphere", "petalo", S.mat(cc), (0.06 * math.cos(ang), 0.06 * math.sin(ang) - 0.01, 0.0), (0.045, 0.02, 0.012), rot=(0, 0, ang), parent=opn, segments=8, ring_count=5)
        tilt = (R(52 + rnd.uniform(-8, 12)), 0, R(rnd.uniform(-35, 35)))
        S.key(F, 1, rot=tilt, scale=(1, 1, 0.82))
        S.key(HD, 1, rot=(R(55), 0, 0))
        fl.append(dict(F=F, HD=HD, wil=wil, opn=opn, s_d=s_d, s_g=s_g, tilt=tilt, h=h))
    sc = type("Set", (), {})()
    sc.B, sc.holes, sc.flowers, sc.canopy = B, holes, fl, canopy
    return sc


def bloom(S, fl, f):
    """Una flor pasa de marchita a abierta y de colores."""
    S.key(fl["F"], f, rot=fl["tilt"], scale=(1, 1, 0.82))
    S.key(fl["F"], f + 9, rot=(R(-6), 0, 0), scale=(1, 1, 1.1), interp="BACK")
    S.key(fl["F"], f + 15, rot=(0, 0, 0), scale=(1, 1, 1))
    S.key(fl["HD"], f, rot=(R(55), 0, 0)); S.key(fl["HD"], f + 9, rot=(R(-10), 0, 0), interp="BACK"); S.key(fl["HD"], f + 15, rot=(0, 0, 0))
    S.key(fl["wil"], f + 4, scale=(1, 1, 1)); S.key(fl["wil"], f + 5, scale=(0.001,) * 3)
    S.key(fl["opn"], f + 4, scale=(0.001,) * 3); S.key(fl["opn"], f + 10, scale=(1.25, 1.25, 1.25), interp="BACK"); S.key(fl["opn"], f + 15, scale=(1, 1, 1))
    S.key(fl["s_d"], f + 4, scale=(0.009, 0.009, fl["h"] / 2)); S.key(fl["s_d"], f + 5, scale=(0.001,) * 3)
    S.key(fl["s_g"], f + 4, scale=(0.001, 0.001, fl["h"] / 2)); S.key(fl["s_g"], f + 8, scale=(0.009, 0.009, fl["h"] / 2))


# ------------------------------------------------------------------ nivel -450
def l1(S):
    """-450: corre ya en el fotograma 1 con la nube encima; frena en seco, la nube le pasa por delante; vuelve y le moja; mira al cielo, empapado, y sigue corriendo."""
    sc = build_set(S)
    x0 = -9.2
    a = S.actor(x=x0); a.yaw = 75; S.key(a.root, 1, rot=(0, 0, R(75)), loc=(x0, 0, 0))
    cl = make_cloud(S, (x0, 0, HOVER)); mood(S, cl, 1, "sad")
    xb = -5.9
    n = a.mocap("correr", travel_to=xb, start=0.4)
    for k in range(3, n, 6): S.cue("step", 1 + k, vol=-8)
    S.cue("whoosh", 1, vol=-12)
    fb = S.f
    # frenazo
    S.cue("slide_down", fb, vol=-10)
    S.key(a.root, fb, loc=(xb, 0, 0)); S.key(a.root, fb + 6, loc=(xb + 0.35, 0, 0)); S.key(a.root, fb + 9, loc=(xb + 0.35, 0, 0))
    pose(S, a, fb + 3, lean=-24, thigh=(-32, 14), knee=(24, 36), arm=(40, -40), elbow=(-20, -30))
    pose(S, a, fb + 7, lean=-14, thigh=(-20, 8), knee=(14, 20), arm=(28, 30), elbow=(-25, -25))
    pose(S, a, fb + 12, lean=0, thigh=(0, 0), knee=(4, 4), arm=(5, 5), elbow=(-25, -25))
    dust(S, xb + 0.2, 0.02, fb + 3, n=6, spread=0.45, size=0.1, y=-0.3)
    xs = xb + 0.35; a.x = xs
    # la nube se pasa de largo: mira atrás, avergonzada
    cloud_look(S, cl, fb + 4, -0.03, 0.0); mood(S, cl, fb + 6, "shy"); cloud_blink(S, cl, fb + 22)
    S.key(cl.C, fb + 5, scale=(1.12, 0.92, 1.0)); S.key(cl.C, fb + 10, scale=(0.95, 1.06, 1.0)); S.key(cl.C, fb + 14, scale=(1, 1, 1))
    # él, a salvo: se gira a cámara, respira, levanta el puño (¡funciona!)
    a.face(-30, fb + 12, turn=5)
    a.look(0.03, 0.03, fb + 16); a.blink(fb + 20)
    S.key(a.head, fb + 14, rot=(R(-10), 0, R(-8))); S.key(a.head, fb + 26, rot=(R(-4), 0, R(6)))
    pose(S, a, fb + 18, lean=0, arm=(5, 5), elbow=(-25, -25))
    pose(S, a, fb + 24, lean=-4, arm=(-10, -80), elbow=(-25, -95), interp="BACK")
    pose(S, a, fb + 34, lean=-4, arm=(-10, -80), elbow=(-25, -95))
    S.cue("pop", fb + 24, vol=-9)
    # duda: la nube vuelve despacito; él nota la sombra y mira hacia arriba
    S.key(a.head, fb + 38, rot=(R(-28), 0, 0)); a.look(0, 0.0, fb + 38)
    pose(S, a, fb + 42, lean=2, arm=(5, 5), elbow=(-25, -25))
    cloud_look(S, cl, fb + 38, 0.03, 0.0)
    # empapado: hombros caídos, cabeza gacha, tirita; luego mira al cielo con ojos tristes
    pose(S, a, fb + 52, lean=10, thigh=(0, 0), knee=(8, 8), arm=(8, 8), elbow=(-30, -30))
    S.key(a.head, fb + 52, rot=(R(24), 0, 0)); a.blink(fb + 56)
    for k in range(5):
        S.key(a.pivot, fb + 56 + k * 2, rot=(R(10), (R(4) if k % 2 else R(-4)), 0))
    S.key(a.pivot, fb + 66, rot=(R(6), 0, 0))
    S.key(a.head, fb + 70, rot=(R(-30), 0, 0)); a.blink(fb + 76)
    pose(S, a, fb + 74, lean=2, arm=(6, 6), elbow=(-30, -30))
    mood(S, cl, fb + 60, "sad")
    # anticipación y sale corriendo otra vez
    S.key(a.head, fb + 82, rot=(R(2), 0, 0))
    S.f = fb + 84
    a.face(75, S.f, turn=3)
    pose(S, a, fb + 88, lean=18, thigh=(-20, 10), knee=(40, 10), arm=(30, -30), elbow=(-60, -60))
    S.f = fb + 89
    f2 = S.f
    n2 = a.mocap("correr", travel_to=-3.6, start=0.4)
    for k in range(3, n2, 6): S.cue("step", f2 + k, vol=-8)
    S.cue("whoosh", f2, vol=-12)
    fe = S.f
    # nube, lluvia, charcos, pelo mojado, gotas
    ft1, ft2 = fb + 36, fb + 52

    def off(f):
        if f < fb: return (0, 0, 0)
        if f < fb + 9: t = ss((f - fb) / 9.0); return (1.9 * t, 0, 0.08 * t)
        if f < ft1: return (1.9, 0, 0.0)
        if f < ft2: t = ss((f - ft1) / 16.0); return (1.9 * (1 - t), 0, 0.0)
        return (0, 0, 0)
    rr = make_rain(S, cl.C, 1, fe + 12, n=28, rx=0.6, seed=2)
    track(S, cl, a, 1, fe, hover=HOVER, lag=2, off=off, rain=[(rr, lambda f: 0.0)])
    puddle(S, xs + 1.9, -0.05, fb + 8, fb + 34, 0.55)
    puddle(S, xs, 0.02, ft2 + 4, ft2 + 36, 0.5)
    ground_splash(S, xs, 0.0, ft2 + 10, n=5, big=0.5)
    wet(S, a, [(1, 0.9), (fb, 0.7), (fb + 34, 0.62), (fb + 70, 0.4), (fe, 0.35)])
    drips(S, a, [fb + 58, fb + 64, fb + 78, fb + 84, fe - 28])
    mood(S, cl, fb + 40, "ok")
    S.f = fe
    return a


# ------------------------------------------------------------------ nivel -80
def l2(S):
    """-80: salta muy alto para salir del chorro; la nube sube con él y cae SUAVE al suelo con un charco (sin golpe seco); vuelve a saltar con cara de confianza."""
    sc = build_set(S)
    x0 = -7.9
    a = S.actor(x=x0); a.yaw = 75; S.key(a.root, 1, rot=(0, 0, R(75)), loc=(x0, 0, 0))
    cl = make_cloud(S, (x0, 0, HOVER)); mood(S, cl, 1, "sad")
    # salto 1 (arranca en el fotograma 1)
    a.hop_to(x0 + 0.8, h=1.5, dur=20, sound=None)
    S.cue("boing", 4, vol=-8)
    S.cue("step", S.f - 3, vol=-12)
    f_l1 = S.f
    x1 = a.x
    # aterriza empapado: mira arriba, parpadea, traga saliva
    a.face(-30, f_l1, turn=5); a.look(0, 0.03, f_l1 + 4); a.blink(f_l1 + 8)
    S.key(a.head, f_l1 + 6, rot=(R(-26), 0, R(-6))); S.key(a.head, f_l1 + 20, rot=(R(-8), 0, R(6)))
    pose(S, a, f_l1 + 8, lean=2, arm=(6, 6), elbow=(-30, -30))
    S.cue("pop", f_l1 + 18, vol=-14)
    S.f = f_l1 + 22
    # salto 2, más alto
    f_h2 = S.f
    dur2 = 24
    a.hop_to(x1, h=2.0, dur=dur2, sound=None)
    S.cue("boing", f_h2 + 3, vol=-8)
    f_apex = f_h2 + 5 + dur2 // 2
    f_land2 = S.f
    # la nube cae suave: desciende flotando, se aplasta un poquito en el suelo y suelta gotitas
    f_fall0 = f_apex - 2
    f_touch = f_apex + 30
    f_rest = f_touch + 4
    S.cue("splash", f_touch, vol=-7)
    cloud_look(S, cl, f_fall0, 0.0, 0.0); mood(S, cl, f_fall0 + 6, "shy")
    S.key(cl.C, f_fall0, scale=(1, 1, 1)); S.key(cl.C, f_fall0 + 10, scale=(0.92, 0.92, 1.1))
    S.key(cl.C, f_touch - 1, scale=(0.95, 0.95, 1.05)); S.key(cl.C, f_touch + 2, scale=(1.18, 1.14, 0.72)); S.key(cl.C, f_touch + 8, scale=(0.97, 0.97, 1.04)); S.key(cl.C, f_touch + 14, scale=(1, 1, 1))
    xr = x1 + 1.05
    ground_splash(S, xr, 0.0, f_touch, n=10, big=1.0)
    puddle(S, xr, 0.0, f_touch, f_touch + 30, 0.62)
    # él aterriza, mira a la nube en el charco, y pone cara de confianza (manos a la cadera, barbilla arriba)
    S.f = f_land2 + 2
    a.face(-30, S.f, turn=5)
    ff = S.f
    S.key(a.head, ff + 3, rot=(R(18), 0, R(-10))); a.look(0.03, -0.03, ff + 3); a.blink(ff + 10)
    pose(S, a, ff + 3, lean=4, arm=(6, 6), elbow=(-30, -30))
    pose(S, a, ff + 14, lean=-3, arm=(-4, -4), elbow=(-90, -90), spread=(28, 28), interp="BACK")
    S.key(a.head, ff + 14, rot=(R(-10), 0, R(8))); a.look(0.03, 0.0, ff + 14); a.blink(ff + 22)
    S.cue("pop", ff + 14, vol=-10)
    S.f = ff + 26
    f_rise = ff + 8
    # salto 3: confianza total, por encima del charco
    f_h3 = S.f
    pose(S, a, f_h3, lean=0, arm=(6, 6), elbow=(-30, -30))
    a.hop_to(x1 + 1.5, h=1.8, dur=22, sound=None)
    S.cue("boing", f_h3 + 3, vol=-8)
    S.key(a.head, f_h3 + 5, rot=(R(-12), 0, 0))
    S.f += 4
    fe = S.f

    def pos(f, p, d):
        if f < f_fall0: return d
        if f < f_touch:
            t = ss((f - f_fall0) / float(f_touch - f_fall0)); return (d[0] + 1.05 * t, d[1], lerp(d[2], 0.50, t))
        if f < f_rise: return (xr, 0.0, 0.50)
        t = ss((f - f_rise) / 20.0); return (lerp(xr, d[0], t), lerp(0.0, d[1], t), lerp(0.50, d[2], t))
    rr = make_rain(S, cl.C, 1, fe + 12, n=28, rx=0.6, seed=3)
    track(S, cl, a, 1, fe, hover=HOVER, lag=4, pos=pos, rain=[(rr, lambda f: 0.0)])
    mood(S, cl, f_touch + 6, "shy"); cloud_blink(S, cl, f_touch + 12); cloud_look(S, cl, f_touch + 6, -0.03, 0.02)
    mood(S, cl, f_rise, "ok"); cloud_look(S, cl, f_rise, 0.03, 0.03)
    wet(S, a, [(1, 0.85), (f_l1, 0.62), (f_land2, 0.5), (fe, 0.42)])
    drips(S, a, [f_l1 + 6, f_l1 + 14, f_land2 + 4, ff + 6])
    S.f = fe
    return a


# ------------------------------------------------------------------ nivel 120
def l3(S):
    """120: camina bajo la lluvia hasta el arbolito; la nube se estira y se coloca encima; solo cae una gota fina por su nariz y él, casi seco, se pone orgulloso."""
    sc = build_set(S)
    x0 = -9.3
    a = S.actor(x=x0); a.yaw = 75; S.key(a.root, 1, rot=(0, 0, R(75)), loc=(x0, 0, 0))
    cl = make_cloud(S, (x0, 0, HOVER)); mood(S, cl, 1, "sad")
    f0 = 1
    # camina rápido hacia el árbol, la lluvia sobre su cabeza desde el primer fotograma
    n = a.mocap("caminar", travel_to=TRX - 0.3, start=0.3)
    for k in range(5, n, 12): S.cue("step", f0 + k, vol=-8)
    fa = S.f
    # llega, se gira a cámara y espera (se mira: ¿funciona?)
    a.face(-30, fa, turn=5)
    pose(S, a, fa + 4, lean=0, arm=(4, 4), elbow=(-28, -28))
    a.look(0.03, 0.03, fa + 4); a.blink(fa + 8)
    S.key(a.head, fa + 6, rot=(R(-30), 0, R(-6)))                       # mira hacia arriba: la nube sigue encima
    f_s = fa + 12                                                       # la nube empieza a estirarse
    S.key(a.head, f_s + 4, rot=(R(-18), 0, 0)); S.cue("whoosh", f_s, vol=-12)
    S.key(a.head, f_s + 26, rot=(R(-10), 0, R(6)))
    cloud_blink(S, cl, f_s - 6)
    S.key(cl.C, f_s, scale=(1, 1, 1)); S.key(cl.C, f_s + 9, scale=(0.86, 0.9, 1.3), interp="BACK"); S.key(cl.C, f_s + 20, scale=(0.9, 0.94, 1.18)); S.key(cl.C, f_s + 40, scale=(1, 1, 1))
    mood(S, cl, f_s + 6, "ok"); cloud_look(S, cl, f_s + 8, 0.0, -0.02)
    f_c = f_s + 22                                                      # la nube está colocada: lluvia sobre la copa
    # hojas se mueven con la lluvia; la copa tiembla un pelo
    for k in range(6):
        g = f_c + k * 7
        S.key(sc.canopy, g, loc=(TRX, TRY, 2.5), scale=(1, 1, 1)); S.key(sc.canopy, g + 3, loc=(TRX, TRY, 2.5 - 0.02), scale=(1.02, 1.02, 0.97)); S.key(sc.canopy, g + 6, loc=(TRX, TRY, 2.5), scale=(1, 1, 1))
    # él, quieto, mira alrededor; ¡todo seco!
    S.cue("pop", f_c + 4, vol=-14)
    a.blink(f_c + 6)
    pose(S, a, f_c + 10, lean=0, arm=(4, 4), elbow=(-28, -28))
    # la gota fina: cuelga de una hoja, cae por delante de la cara y se posa en la nariz
    f_d = f_c + 18
    ph = head_pos(S, a, f_d + 14)
    nx, ny, nz = ph.x - 0.10, ph.y - 0.20, ph.z - 0.045
    dr = S.obj("uv_sphere", "gota_nariz", "water", (nx, ny, 2.15), (0.001,) * 3, segments=10, ring_count=6)
    S.key(dr, f_d - 8, loc=(nx, ny, 2.1), scale=(0.001,) * 3)
    S.key(dr, f_d - 2, loc=(nx, ny, 2.08), scale=(0.03, 0.03, 0.04))
    S.key(dr, f_d + 2, loc=(nx, ny, 2.05), scale=(0.028, 0.028, 0.05))
    S.key(dr, f_d + 12, loc=(nx, ny, nz + 0.05), scale=(0.022, 0.022, 0.05), interp="LINEAR")
    S.key(dr, f_d + 14, loc=(nx, ny, nz), scale=(0.03, 0.03, 0.03))
    S.key(dr, f_d + 20, loc=(nx, ny, nz), scale=(0.034, 0.034, 0.034))
    S.key(dr, f_d + 30, loc=(nx, ny + 0.01, nz - 0.18), scale=(0.02, 0.02, 0.04))
    S.key(dr, f_d + 34, loc=(nx, ny + 0.01, nz - 0.4), scale=(0.001,) * 3)
    S.cue("pop", f_d + 14, vol=-10)
    # sigue la gota con los ojos (bizco): cabeza gacha, pupilas abajo, parpadeo
    S.key(a.head, f_d, rot=(R(-6), 0, R(4))); S.key(a.head, f_d + 14, rot=(R(10), 0, R(-4)))
    a.look(0.0, -0.03, f_d + 8); a.blink(f_d + 24)
    S.key(a.head, f_d + 30, rot=(R(4), 0, 0))
    # orgulloso: pecho fuera, barbilla arriba, puño al pecho; la nube guiña
    fp = f_d + 30
    pose(S, a, fp, lean=0, arm=(4, 4), elbow=(-28, -28))
    pose(S, a, fp + 10, lean=-5, arm=(-8, -62), elbow=(-30, -105), spread=(14, 0), interp="BACK")
    pose(S, a, fp + 30, lean=-5, arm=(-8, -62), elbow=(-30, -105), spread=(14, 0))
    S.key(a.head, fp + 10, rot=(R(-14), 0, R(8))); a.look(0.03, 0.0, fp + 10); a.blink(fp + 18)
    S.key(a.pivot, fp + 10, rot=(R(-5), 0, 0), scale=(1.03, 1.03, 1.03)); S.cue("tada", fp + 12, vol=-9)
    cloud_blink(S, cl, fp + 16); mood(S, cl, fp + 14, "happy")
    S.key(a.root, fp, loc=(TRX - 0.3, 0, 0), rot=(0, 0, R(-30)))
    S.f = fp + 32
    fe = S.f

    def pos(f, p, d):
        if f < f_s: return d
        t = ss((f - f_s) / 18.0)
        return (lerp(d[0], TRX, t), lerp(d[1], 0.3, t), lerp(d[2], 3.5, t))
    rc = make_rain(S, cl.C, 1, fe + 12, n=26, rx=0.5, seed=4)
    re1 = make_rain(S, cl.C, 1, fe + 12, n=8, rx=0.1, ry=0.2, off=(-0.98, 0, -0.38), seed=5)
    re2 = make_rain(S, cl.C, 1, fe + 12, n=8, rx=0.1, ry=0.2, off=(0.98, 0, -0.38), seed=6)
    track(S, cl, a, 1, fe, hover=HOVER, lag=3, pos=pos, rain=[(rc, lambda f: 0.0 if f < f_s + 6 else (2.88 if f < fe - 20 else None)),
                                                               (re1, lambda f: 0.0 if f >= f_s + 12 else None), (re2, lambda f: 0.0 if f >= f_s + 12 else None)])
    puddle(S, TRX - 1.0, 0.25, f_c, f_c + 36, 0.35); puddle(S, TRX + 1.0, 0.25, f_c + 4, f_c + 42, 0.38)
    wet(S, a, [(1, 0.9), (f_s, 0.6), (f_c, 0.6), (f_c + 40, 0.75), (fe, 0.85)])
    drips(S, a, [10, 20, f_s - 6])
    S.f = fe
    return a


# ------------------------------------------------------------------ nivel 900
def l4(S):
    """900: llega corriendo, arranca el banco, lo levanta con ambos brazos (reach_up) y lo lleva de tejado; la nube llueve a cántaros encima del banco y él, seco, sonríe."""
    sc = build_set(S)
    B = sc.B
    x0 = -9.0
    a = S.actor(x=x0); a.yaw = 75; S.key(a.root, 1, rot=(0, 0, R(75)), loc=(x0, 0, 0))
    cl = make_cloud(S, (x0, 0, HOVER)); mood(S, cl, 1, "sad")
    S.key(B, 1, loc=(BNX, BNY, 0), rot=(0, 0, 0))
    n = a.mocap("correr", travel_to=BNX - 0.4, start=0.4)
    for k in range(3, n, 6): S.cue("step", 1 + k, vol=-8)
    S.cue("whoosh", 1, vol=-12)
    fa = S.f
    xa = BNX - 0.0
    # frena y se gira hacia el banco (de espaldas a cámara), mira la nube y piensa
    S.key(a.root, fa, loc=(BNX - 0.4, 0, 0)); S.key(a.root, fa + 6, loc=(xa, 0, 0))
    pose(S, a, fa + 3, lean=-16, thigh=(-22, 8), knee=(16, 22), arm=(26, 30), elbow=(-25, -25))
    pose(S, a, fa + 8, lean=0, arm=(5, 5), elbow=(-25, -25))
    a.face(165, fa + 3, turn=6); a.x = xa
    S.cue("slide_down", fa, vol=-10)
    dust(S, BNX - 0.2, 0.02, fa + 3, n=4, spread=0.35, size=0.08, y=-0.3)
    S.key(a.head, fa + 10, rot=(R(-26), 0, R(10))); a.blink(fa + 12)
    S.key(a.head, fa + 22, rot=(R(6), 0, R(-8)))
    pose(S, a, fa + 20, lean=0, arm=(5, 5), elbow=(-25, -25))
    pose(S, a, fa + 28, lean=0, arm=(-30, -3), elbow=(-110, -25))        # ¡idea! (se frota la barbilla)
    S.cue("pop", fa + 26, vol=-8)
    S.key(a.head, fa + 30, rot=(R(2), 0, 0))
    # se agacha y agarra el asiento
    fg = fa + 34
    pose(S, a, fg, lean=0, arm=(5, 5), elbow=(-25, -25))
    pose(S, a, fg + 6, lean=30, thigh=(-62, -62), knee=(100, 100), arm=(-75, -75), elbow=(-30, -30), spread=(4, -4), interp="BACK")
    S.key(a.root, fg, loc=(xa, 0, 0)); S.key(a.root, fg + 6, loc=(xa, 0, -0.24))
    S.key(a.head, fg + 6, rot=(R(-14), 0, 0))
    S.key(B, fg + 6, loc=(BNX, BNY, 0), rot=(0, 0, 0))
    S.cue("creak", fg + 6, vol=-8)
    S.f = fg + 10
    # arranca el banco con reach_up (captura real): sube hasta quedar sobre su cabeza
    fl = S.f
    a.z = 0.0
    a.reach_up(dur=26)
    f_top = fl + 26
    bz = {}
    for f in range(fl - 10, f_top + 1):
        if f <= fl + 3: bz[f] = 0.0; yb = BNY; rx_ = 0.0
        else:
            t = ss((f - fl - 3) / 21.0); bz[f] = 1.50 * t + (0.28 * math.sin(math.pi * min(1, t)) if t < 1 else 0); yb = lerp(BNY, 0.0, ss((f - fl - 3) / 21.0)); rx_ = -8 * math.sin(math.pi * t)
        S.key(B, f, loc=(BNX, yb, bz[f]), rot=(R(rx_), 0, 0), interp="LINEAR" if f % 2 else "BEZIER")
    S.cue("creak", fl + 3, vol=-8); S.cue("clunk", fl + 6, vol=-14); S.cue("pop", f_top, vol=-8)
    for h in sc.holes:                                                       # los huecos que deja el banco
        S.key(h, fl + 3, scale=(0.001, 0.001, 0.003)); S.key(h, fl + 6, scale=(0.08, 0.06, 0.003))
    dust(S, BNX, 0.03, fl + 4, n=6, spread=0.9, size=0.08, y=BNY - 0.2, rise=0.2)
    # sostiene con ambos brazos (manos bajo el asiento) y se gira a cámara
    S.f = f_top
    a.face(-30, f_top - 2, turn=6)
    ZB = 1.47
    S.key(B, f_top + 4, loc=(BNX, 0.0, ZB), rot=(0, 0, 0))
    for f in range(f_top, f_top + 8):
        for i in (0, 1):
            S.key(a.arms[i], f, rot=(R(-168), R((5 if i == 0 else -5)), 0)); S.key(a.elbows[i], f, rot=(R(-8), 0, 0))
    S.f = f_top + 8
    f_hold = S.f
    # camina con el banco (tejado), paso firme, mirando a cámara
    S.cue("step", f_hold + 8, vol=-8)
    a.face(75, f_hold, turn=4); S.wait(4)
    fw = S.f
    nw = a.mocap("caminar", travel_to=xa + 1.5)
    for k in range(5, nw, 12): S.cue("step", fw + k, vol=-8)
    for f in range(fw, fw + nw):
        for i in (0, 1):
            S.key(a.arms[i], f, rot=(R(-168 + 3 * math.sin((f - fw) * 0.5)), R((5 if i == 0 else -5)), 0)); S.key(a.elbows[i], f, rot=(R(-8), 0, 0))
        S.key(a.head, f, rot=(R(-4), 0, 0))
    # el banco acompaña a las manos (muestreo fotograma a fotograma)
    for f in range(f_hold - 4, fw + nw + 1):
        S.sc.frame_set(f); bpy.context.view_layer.update()
        p = a.root.matrix_world.translation
        z = ZB + (p.z if p.z < 0.3 else 0.0) * 0.8
        bz[f] = z
        S.key(B, f, loc=(p.x, 0.0, z), rot=(0, 0, 0), interp="LINEAR")
    fz = S.f
    # se para, vuelve a cámara y sonríe: guiño a la nube
    a.face(-30, fz, turn=5)
    S.key(a.root, fz, loc=(xa + 1.5, 0, 0), rot=(0, 0, R(75))); S.key(a.root, fz + 5, loc=(xa + 1.5, 0, 0), rot=(0, 0, R(-30)))
    for f in range(fz, fz + 22):
        for i in (0, 1):
            S.key(a.arms[i], f, rot=(R(-168), R((5 if i == 0 else -5)), 0)); S.key(a.elbows[i], f, rot=(R(-8), 0, 0))
        bz[f] = ZB
    S.key(B, fz, loc=(xa + 1.5, 0, ZB)); S.key(B, fz + 22, loc=(xa + 1.5, 0, ZB + 0.0))
    a.look(0.03, 0.0, fz + 4); a.blink(fz + 9); S.key(a.head, fz + 6, rot=(R(-8), 0, R(8)))
    S.key(a.pivot, fz + 6, rot=(R(-3), 0, 0), scale=(1.02, 1.02, 1.02)); S.cue("tada", fz + 6, vol=-9)
    cloud_blink(S, cl, fz + 12); mood(S, cl, fz + 10, "happy")
    S.f = fz + 22
    fe = S.f
    # nube y lluvia: antes del banco llueve a él; con el banco encima llueve a cántaros sobre el banco (y alrededor)
    f_on = fl + 12

    def zt_c(f):
        if f < f_on: return 0.0
        return bz.get(f, ZB) + 0.53
    rc = make_rain(S, cl.C, 1, fe + 12, n=44, rx=0.88, ry=0.3, seed=7, p=7)
    re1 = make_rain(S, cl.C, 1, fe + 12, n=10, rx=0.12, ry=0.25, off=(-1.12, 0, -0.38), seed=8, p=7)
    re2 = make_rain(S, cl.C, 1, fe + 12, n=10, rx=0.12, ry=0.25, off=(1.12, 0, -0.38), seed=9, p=7)
    hv = HOVER + 0.55

    def off(f):
        if f < f_on - 4: return (0, 0, 0)
        t = ss((f - f_on + 4) / 14.0); return (0, 0, 0.55 * t)
    track(S, cl, a, 1, fe, hover=HOVER, lag=3, off=off,
          rain=[(rc, zt_c), (re1, lambda f: 0.0 if f >= f_on else None), (re2, lambda f: 0.0 if f >= f_on else None)])
    puddle(S, BNX - 1.15, 0.1, f_on, f_on + 40, 0.42); puddle(S, BNX + 1.15, 0.1, f_on + 4, f_on + 46, 0.45)
    wet(S, a, [(1, 0.9), (fl, 0.5), (fl + 14, 0.45), (fe, 0.5)])
    drips(S, a, [18, 28, fa + 14])
    S.f = fe
    return a


# ------------------------------------------------------------------ nivel 5400
def l5(S):
    """5400: quieto, mira alrededor; la nube se desliza al parterre de flores marchitas y las riega con cariño: se abren de colores; él se sienta en el banco, seco, y saluda."""
    sc = build_set(S)
    x0 = -8.9
    a = S.actor(x=x0); a.yaw = 75; S.key(a.root, 1, rot=(0, 0, R(75)), loc=(x0, 0, 0))
    cl = make_cloud(S, (x0, 0, HOVER)); mood(S, cl, 1, "sad")
    xs = -6.5
    n = a.mocap("caminar", travel_to=xs, start=0.3)
    for k in range(5, n, 12): S.cue("step", 1 + k, vol=-8)
    fa = S.f
    # se queda quieto y mira alrededor (captura "mirar")
    a.face(-30, fa, turn=5)
    f_m = fa + 4
    S.f = f_m
    nm = a.mocap("mirar", frames=34, root=False, start=1.0, strength=0.75)
    blinks(S, a, [f_m + 8, f_m + 24])
    f_slide = f_m + 6                                                     # la nube se desliza hacia las flores
    cloud_look(S, cl, f_slide - 4, 0.04, 0.0); cloud_blink(S, cl, f_slide - 2)
    S.cue("whoosh", f_slide, vol=-12)
    f_arr = f_slide + 34
    # el hombre nota que ya no llueve: mira la mano, el cielo, y por fin el parterre
    S.f = f_m + nm
    fn = S.f
    a.face(40, fn, turn=6)
    S.key(a.head, fn + 4, rot=(R(-20), 0, R(-10))); a.look(0.03, 0.03, fn + 4)
    pose(S, a, fn + 6, lean=0, arm=(6, 6), elbow=(-30, -30))
    pose(S, a, fn + 12, lean=-3, arm=(6, -50), elbow=(-30, -70))          # palma abierta: ya no llueve
    S.key(a.head, fn + 14, rot=(R(-6), 0, R(-22))); a.blink(fn + 16)
    S.cue("pop", fn + 12, vol=-10)
    pose(S, a, fn + 22, lean=2, arm=(6, 6), elbow=(-30, -30))
    S.key(a.head, fn + 26, rot=(R(2), 0, R(-18)))
    # flores: se abren una a una mientras la nube las riega
    for i, fl in enumerate(sc.flowers):
        bloom(S, fl, f_arr + 10 + 4 * i)
    S.cue("tada", f_arr + 18, vol=-8); S.cue("pop", f_arr + 26, vol=-12); S.cue("pop", f_arr + 38, vol=-12)
    f_open = f_arr + 10 + 4 * 10 + 15                                    # todas abiertas
    # él camina hasta el banco, se gira, se sienta (de espaldas) y saluda
    S.f = fn + 30
    a.face(75, S.f, turn=4); S.wait(4)
    fw = S.f
    nw = a.mocap("caminar", travel_to=BNX - 0.2)
    for k in range(5, nw, 12): S.cue("step", fw + k, vol=-8)
    fq = S.f
    hip = a._dims["hip"]
    zs = 0.52 - hip
    a.face(-30, fq, turn=5)
    S.key(a.root, fq, loc=(BNX - 0.2, 0, 0), rot=(0, 0, R(75))); S.key(a.root, fq + 5, loc=(BNX - 0.2, 0, 0), rot=(0, 0, R(-30)))
    pose(S, a, fq + 5, lean=-4, arm=(6, 6), elbow=(-30, -30))
    pose(S, a, fq + 11, lean=-12, thigh=(-30, -30), knee=(50, 50), arm=(20, 20), elbow=(-25, -25), interp="BACK")
    S.key(a.root, fq + 11, loc=(BNX - 0.2, 0.25, -0.12))
    S.key(a.root, fq + 17, loc=(BNX - 0.2, BNY - 0.04, zs + 0.03)); S.cue("pop", fq + 17, vol=-8)
    a.sit(fq + 17, knee=88); S.key(a.pivot, fq + 17, rot=(R(-3), 0, 0), scale=(1.03, 1.03, 0.96))
    for i in (0, 1): S.key(a.arms[i], fq + 17, rot=(R(-12), R((10 if i == 0 else -10)), 0)); S.key(a.elbows[i], fq + 17, rot=(R(-35), 0, 0))
    a.sit(fq + 22, knee=88); S.key(a.pivot, fq + 22, rot=(0, 0, 0), scale=(1, 1, 1))
    S.key(a.root, fq + 22, loc=(BNX - 0.2, BNY - 0.04, zs + 0.03))
    S.key(a.head, fq + 22, rot=(R(-4), 0, R(14)))
    a.look(0.03, 0.0, fq + 22); a.blink(fq + 26)
    # gira un poco el cuerpo hacia la nube y saluda (captura "saludar"), con las piernas sentadas
    a.face(10, fq + 24, turn=6)
    S.f = fq + 26
    fwv = S.f
    nv = a.mocap("saludar", frames=34, root=False, start=0.6, strength=0.9)
    for f in range(fwv, fwv + nv + 1):
        a.sit(f, knee=88)
        S.key(a.root, f, loc=(BNX - 0.2, BNY - 0.04, zs + 0.03), rot=(0, 0, R(10)))
    S.key(a.head, fwv + 4, rot=(R(-2), 0, R(10)))
    S.cue("pop", fwv + 12, vol=-10)
    a.blink(fwv + 20)
    f_e = fwv + nv
    S.f = f_e + 8
    for i in (0, 1): S.key(a.arms[i], f_e + 8, rot=(R(-10), R((10 if i == 0 else -10)), 0)); S.key(a.elbows[i], f_e + 8, rot=(R(-35), 0, 0))
    fe = S.f
    # la nube: se desliza a las flores, baja, riega feliz; al final, bobea y devuelve el saludo
    for k in range(3):                                                   # saltito feliz al ver el saludo
        S.key(cl.C, fwv + 14 + k * 8, scale=(1, 1, 1)); S.key(cl.C, fwv + 18 + k * 8, scale=(1.1, 1.1, 0.88)); S.key(cl.C, fwv + 22 + k * 8, scale=(0.96, 0.96, 1.06))
    S.key(cl.C, fwv + 38, scale=(1, 1, 1))
    mood(S, cl, f_arr - 4, "ok"); mood(S, cl, f_arr + 18, "happy"); cloud_blink(S, cl, f_arr + 28); cloud_look(S, cl, f_arr + 40, -0.03, -0.01)
    cloud_look(S, cl, fwv + 10, -0.035, 0.0)

    def pos(f, p, d):
        t = ss((f - f_slide) / 34.0)
        if f < f_slide: return d
        return (lerp(d[0], FBX, t), lerp(d[1], FBY - 0.1, t), lerp(d[2], 1.75, t))
    rr = make_rain(S, cl.C, 1, fe + 12, n=34, rx=0.55, ry=0.28, seed=11)
    track(S, cl, a, 1, fe, hover=HOVER, lag=3, pos=pos, rain=[(rr, lambda f: 0.0 if f < f_slide + 6 else (0.55 if f < fe - 24 else None))])
    puddle(S, FBX + 0.05, FBY - 0.52, f_arr + 8, f_arr + 50, 0.35, ry=0.45)
    wet(S, a, [(1, 0.9), (f_slide, 0.55), (f_arr + 30, 0.75), (fe, 1.0)])
    drips(S, a, [14, 22, f_slide + 2])
    S.f = fe
    return a


LEVELS = [(-450, l1), (-80, l2), (120, l3), (900, l4), (5400, l5)]
