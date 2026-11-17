"""ep008 — Cada nivel de IQ mueve una roca. Parque junto al río: una roca enorme tapa el camino de tierra hacia el banco.
-500 la empuja con la espalda y se estrella (rebote suave, estrellas y pajaritos 1 s); -80 salta encima y se queda colgado del borde;
130 empuja con todo el cuerpo y se tumba exhausto; 900 palanca con un tablón; 5200 la toca con un dedo: es de espuma."""
import math
import random
import bpy
from mathutils import Vector

TITLE = "Every IQ Level Moves a Boulder"
ONSCREEN = "Every IQ level moves a boulder"

BX = -5.2          # x de la roca
RZ = 0.88          # altura del centro de la roca
RSC = (0.92, 0.80, 0.90)   # escala de la roca


def R(d): return math.radians(d)


def ss(t): t = max(0.0, min(1.0, t)); return t * t * (3 - 2 * t)


# ------------------------------------------------------------------ escenario
def build_set(S, plank=False):
    """Camino de tierra, hierba alrededor, banco de madera, flores, arbustos, piedrecitas y la roca. Devuelve (rk, stone, foam, rockx)."""
    rnd = random.Random(8)
    ground = S.mats["p_suelo"]
    dirt = S.pmat("tierra", [(0.30, (0.40, 0.27, 0.15)), (0.55, (0.50, 0.36, 0.21)), (0.75, (0.34, 0.23, 0.13))], scale=9, rough=0.95, bump=0.5)
    wood = S.pmat("madera_banco", [(0.25, (0.36, 0.20, 0.09)), (0.50, (0.50, 0.31, 0.15)), (0.80, (0.30, 0.17, 0.08))], scale=16, rough=0.7, bump=0.35, detail=8)
    woodp = S.pmat("tablon", [(0.25, (0.62, 0.43, 0.22)), (0.5, (0.74, 0.53, 0.29)), (0.8, (0.52, 0.35, 0.17))], scale=12, rough=0.75, bump=0.4, detail=9)
    iron = S.pmat("hierro_banco", [(0.3, (0.10, 0.11, 0.12)), (0.7, (0.2, 0.21, 0.22))], scale=8, rough=0.5, bump=0.1)
    stone = S.pmat("roca_dura", [(0.25, (0.30, 0.29, 0.28)), (0.45, (0.47, 0.45, 0.42)), (0.65, (0.36, 0.35, 0.34)), (0.85, (0.55, 0.52, 0.47))], scale=4.0, rough=0.92, bump=1.1, detail=12)
    foamm = S.pmat("roca_espuma", [(0.25, (0.86, 0.66, 0.22)), (0.5, (0.96, 0.82, 0.38)), (0.8, (0.88, 0.70, 0.26))], scale=16, rough=0.9, bump=0.9, detail=5)
    moss = S.pmat("musgo", [(0.3, (0.12, 0.28, 0.06)), (0.7, (0.28, 0.42, 0.10))], scale=18, rough=0.9, bump=0.5, detail=6)
    leafm = S.pmat("arbusto", [(0.25, (0.10, 0.26, 0.06)), (0.55, (0.20, 0.40, 0.09)), (0.85, (0.34, 0.48, 0.12))], scale=9, rough=0.8, bump=0.5, detail=8)
    stem = S.pmat("tallo", [(0.3, (0.15, 0.40, 0.08)), (0.7, (0.25, 0.52, 0.12))], scale=3, rough=0.7, bump=0.0)

    def O(prim, name, mat, loc, scale=(1, 1, 1), rot=(0, 0, 0), parent=None, smooth=True, **kw):
        o = S.obj(prim, name, "white", loc, scale, rot, parent, smooth, **kw); o.data.materials[0] = mat; return o

    # hierba: se quita la del prado cercano y se reparte alrededor del camino (el camino queda sin briznas)
    bpy.data.objects["prado_cerca"].modifiers.clear()
    bl = bpy.data.objects["brizna"]
    for k, (nm, x0, x1, y0, y1, n) in enumerate((("hA", -9.2, -2.55, -6.5, -0.66, 13500), ("hB", -9.2, -4.2, 0.66, 3.0, 4200), ("hC", -4.2, -2.55, 1.6, 3.0, 1300))):
        bpy.ops.mesh.primitive_plane_add(size=1, location=((x0 + x1) / 2, (y0 + y1) / 2, 0.003)); pr = bpy.context.object; pr.name = nm
        pr.scale = (x1 - x0, y1 - y0, 1); pr.data.materials.append(ground); S._scatter(pr, bl, n, 21 + k)

    # camino de tierra: franja principal + ensanche junto al banco + manchas irregulares en los bordes
    O("cube", "camino", dirt, (-6.2, 0, 0.008), (3.7, 0.64, 0.008), smooth=False)
    O("cube", "plaza", dirt, (-3.3, 0.55, 0.008), (0.95, 1.05, 0.008), smooth=False)
    for i in range(16):
        x = rnd.uniform(-9.6, -2.8); y = rnd.choice((-1, 1)) * rnd.uniform(0.55, 0.78)
        if x > -4.2 and y > 0: continue
        O("cylinder", "mancha", dirt, (x, y, 0.009), (rnd.uniform(0.18, 0.4), rnd.uniform(0.1, 0.2), 0.006), vertices=14, smooth=False)
    for i in range(34):   # piedrecitas y terrones en el camino
        x = rnd.uniform(-9.5, -2.9); y = rnd.uniform(-0.62, 0.62)
        if abs(x - BX) < 1.2 and abs(y) < 0.8: continue
        r_ = rnd.uniform(0.018, 0.045)
        O("ico_sphere", "guijarro", stone, (x, y, 0.012 + r_ * 0.3), (r_ * 1.3, r_, r_ * 0.7), subdivisions=1)

    # banco de madera con patas de hierro, tablas con veta y respaldo
    bx0, by0 = -3.25, 1.0
    B = S.empty("banco", (bx0, by0, 0.0))
    for k, yy in enumerate((-0.17, -0.06, 0.05, 0.16)):
        O("cube", "asiento", wood, (0, yy, 0.50), (0.95, 0.050, 0.020), parent=B, smooth=False)
    for k, zz in enumerate((0.78, 0.93)):
        O("cube", "respaldo", wood, (0, 0.24, zz), (0.95, 0.018, 0.058), rot=(R(-12), 0, 0), parent=B, smooth=False)
    for sx in (-1, 1):
        O("cube", "pata_d", iron, (0.80 * sx, -0.14, 0.25), (0.030, 0.026, 0.25), parent=B, smooth=False)
        O("cube", "pata_t", iron, (0.80 * sx, 0.22, 0.25), (0.030, 0.026, 0.25), parent=B, smooth=False)
        O("cube", "apoyabrazos", iron, (0.88 * sx, 0.04, 0.68), (0.026, 0.22, 0.020), parent=B, smooth=False)
        O("cube", "poste", iron, (0.88 * sx, 0.20, 0.60), (0.024, 0.024, 0.20), parent=B, smooth=False)

    # arbustos con florecitas
    for (x, y, sc) in ((-8.0, 1.8, 0.7), (-6.4, 1.9, 0.55), (-4.7, 1.7, 0.62), (-2.9, 2.2, 0.8), (-9.0, -1.6, 0.5)):
        for j in range(5):
            O("ico_sphere", "arb", leafm, (x + rnd.uniform(-0.35, 0.35) * sc * 2, y + rnd.uniform(-0.25, 0.25), 0.28 * sc + rnd.uniform(0, 0.25) * sc), (sc * rnd.uniform(0.35, 0.55),) * 3, subdivisions=2)
        for j in range(7):
            O("uv_sphere", "flor_arb", S.mat(rnd.choice(("white", "pink", "yellow"))), (x + rnd.uniform(-0.5, 0.5) * sc, y - 0.3 * sc, 0.30 * sc + rnd.uniform(0, 0.35) * sc), (0.03,) * 3, segments=8, ring_count=6)
    # flores sueltas junto al camino y alrededor del banco
    cols = ("white", "pink", "yellow", "coral", "purple", "red")
    spots = [(rnd.uniform(-9.3, -2.8), rnd.uniform(-1.5, -0.8)) for _ in range(30)] + [(rnd.uniform(-9, -4.5), rnd.uniform(0.85, 1.3)) for _ in range(10)] + [(rnd.uniform(-4.3, -2.2), rnd.uniform(1.65, 2.0)) for _ in range(6)]
    for (x, y) in spots:
        h = rnd.uniform(0.16, 0.34); c = rnd.choice(cols)
        O("cylinder", "tallo", stem, (x, y, h / 2), (0.007, 0.007, h / 2), vertices=6, smooth=False)
        O("uv_sphere", "flor", S.mat(c), (x, y - 0.004, h + 0.005), (0.035, 0.03, 0.02), segments=10, ring_count=6)
        O("uv_sphere", "centro", S.mat("yellow" if c != "yellow" else "orange"), (x, y - 0.03, h + 0.012), (0.014, 0.01, 0.012), segments=6, ring_count=4)

    # la roca: ico_sphere deformada tipo bloque redondeado + musgo
    def rock_mesh(name, mat):
        o = S.obj("ico_sphere", name, "rock", (0, 0, 0), RSC, subdivisions=4, radius=1.0); o.data.materials[0] = mat
        r2 = random.Random(5)
        for v in o.data.vertices:
            d = v.co.normalized(); p = 3.4
            n = (abs(d.x) ** p + abs(d.y) ** p + abs(d.z) ** p) ** (1 / p)
            w = 1 + 0.07 * math.sin(3.1 * d.x + 1.3) * math.cos(2.7 * d.y + 0.4) + 0.05 * math.sin(5.3 * d.z + 2 * d.x) + 0.03 * math.sin(9 * d.x + 4 * d.y)
            v.co = d / n * w
            if v.co.z < -0.7: v.co.z = -0.7 + (v.co.z + 0.7) * 0.25
        return o
    rk = S.empty("roca", (BX, 0, RZ))
    st = rock_mesh("roca_dura", stone); st.parent = rk
    fo = rock_mesh("roca_espuma", foamm); fo.parent = rk; S.key(fo, 1, scale=(0.001,) * 3)
    for (mx, my, mz, ms) in ((0.2, 0.15, 0.80, 0.30), (-0.45, -0.1, 0.72, 0.2), (0.62, -0.5, 0.15, 0.17)):
        O("ico_sphere", "musgo", moss, (mx * RSC[0], my, mz * RSC[2] * 1.0), (ms, ms * 0.8, ms * 0.35), parent=rk, subdivisions=2)
    verts = [(v.co.x * RSC[0], v.co.z * RSC[2] + RZ) for v in st.data.vertices if abs(v.co.y) < 0.35]
    vertsy = [(v.co.y * RSC[1], v.co.z * RSC[2] + RZ) for v in st.data.vertices if abs(v.co.x) < 0.45]

    def rockx(z, side=1):
        """x (relativa al centro de la roca) del contorno de la roca a la altura z."""
        c = [vx * side for vx, vz in verts if abs(vz - z) < 0.06]
        return max(c) if c else 0.7
    def rocky(z):
        """distancia (>0) de la cara delantera (hacia la cámara) de la roca al centro, a la altura z."""
        c = [-vy for vy, vz in vertsy if abs(vz - z) < 0.06]
        return max(c) if c else 0.6
    S.rockx = rockx; S.rocky = rocky

    if plank:
        pass
    return rk, st, fo, rockx


# ------------------------------------------------------------------ poses y efectos
def pose(S, a, f, lean=0, thigh=(0, 0), knee=(0, 0), arm=(0, 0), elbow=(-12, -12), spread=(0, 0), rz=None, interp="BEZIER"):
    """Pose completa (índice 0 = lado -x del personaje). Ángulos en grados; muslo negativo = adelante; brazo negativo = adelante/arriba."""
    for i in (0, 1):
        S.key(a.legs[i], f, rot=(R(thigh[i]), 0, 0), interp=interp); S.key(a.knees[i], f, rot=(R(knee[i]), 0, 0), interp=interp)
        S.key(a.arms[i], f, rot=(R(arm[i]), R(spread[i]), 0), interp=interp); S.key(a.elbows[i], f, rot=(R(elbow[i]), 0, 0), interp=interp)
    S.key(a.pivot, f, rot=(R(lean), 0, 0), interp=interp)


def head_pos(S, a, f):
    S.sc.frame_set(f); bpy.context.view_layer.update()
    return a.head.matrix_world.translation.copy()


def hand_pos(S, a, side, f):
    S.sc.frame_set(f); bpy.context.view_layer.update()
    return a.elbows[side].matrix_world @ Vector((0, 0, -(a._dims["fa"] + 0.07)))


def dust(S, x, z, f, n=7, spread=0.55, size=0.13, y=-0.25, seed=0, rise=0.35):
    """Polvo de tierra: bolitas que crecen, suben un poco y se encogen."""
    rr = random.Random(seed + int(x * 10) + f); m = S.mat("khaki")
    for i in range(n):
        d = S.obj("uv_sphere", "polvo", "khaki", (x, y, z), (0.001,) * 3, segments=8, ring_count=6); d.data.materials[0] = m
        dx = rr.uniform(-spread, spread); sz = size * rr.uniform(0.7, 1.3); dy = rr.uniform(-0.15, 0.1)
        S.key(d, f - 1, loc=(x, y + dy, z), scale=(0.001,) * 3)
        S.key(d, f + 4, loc=(x + dx * 0.6, y + dy, z + rise * 0.4), scale=(sz, sz * 0.8, sz * 0.8))
        S.key(d, f + 15, loc=(x + dx, y + dy, z + rise), scale=(sz * 1.3, sz, sz))
        S.key(d, f + 20, loc=(x + dx * 1.1, y + dy, z + rise * 1.1), scale=(0.001,) * 3)


def sweat(S, a, f, seed=0):
    """Gota de sudor que resbala desde la sien."""
    p = head_pos(S, a, f); ysgn = -1
    sx = 0.19 if a.yaw > 0 else -0.19
    d = S.obj("uv_sphere", "sudor", "water", (p.x + sx, p.y - 0.12, p.z + 0.12), (0.001,) * 3, segments=8, ring_count=6)
    S.key(d, f - 1, loc=(p.x + sx, p.y - 0.12, p.z + 0.12), scale=(0.001,) * 3)
    S.key(d, f + 2, loc=(p.x + sx, p.y - 0.12, p.z + 0.1), scale=(0.022, 0.022, 0.032))
    S.key(d, f + 10, loc=(p.x + sx * 1.15, p.y - 0.12, p.z - 0.18), scale=(0.02, 0.02, 0.036))
    S.key(d, f + 16, loc=(p.x + sx * 1.2, p.y - 0.12, p.z - 0.55), scale=(0.001,) * 3)


def daze(S, a, f0, n=22):
    """Estrellas y pajaritos girando alrededor de la cabeza: dura n (<= 24) fotogramas."""
    p = head_pos(S, a, f0 + 2); cx, cy, cz = p.x, p.y - 0.02, p.z + 0.36
    items = []
    for i in range(3):
        o = S.obj("uv_sphere", "estrella", "gold", (cx, cy, cz), (0.001,) * 3, segments=5, ring_count=3); items.append((o, 0.095, 2 * math.pi * i / 5))
    for i in range(2):
        b = S.empty("pajarito", (cx, cy, cz))
        S.obj("uv_sphere", "p_cuerpo", "blue", (0, 0, 0), (0.06, 0.085, 0.055), parent=b, segments=10, ring_count=6)
        S.obj("cone", "p_pico", "orange", (0, -0.085, 0), (0.02, 0.02, 0.04), rot=(R(90), 0, 0), parent=b, vertices=6)
        for sx in (-1, 1):
            S.obj("uv_sphere", "p_ala", "blue", (0.07 * sx, 0.01, 0.01), (0.07, 0.03, 0.012), rot=(0, R(18 * sx), 0), parent=b, segments=8, ring_count=4)
        items.append((b, 1.0, 2 * math.pi * (i + 0.5) / 5 + math.pi * 0.6))
    for o, sc, ph in items:
        for k in range(0, n + 1, 2):
            t = k / n; ang = ph + t * 2 * math.pi * 1.6
            rr = 0.34 + 0.03 * math.sin(ang * 2)
            loc = (cx + rr * math.cos(ang), cy + rr * 0.55 * math.sin(ang), cz + 0.05 * math.sin(ang * 2 + ph))
            s_ = sc * min(1.0, k / 3.0, (n - k) / 3.0 + 0.001)
            if sc == 1.0:
                S.key(o, f0 + k, loc=loc, rot=(0, 0, math.pi / 2 + ang), scale=(max(0.001, s_),) * 3)
            else:
                S.key(o, f0 + k, loc=loc, rot=(ang, ang * 0.5, 0), scale=(max(0.001, s_),) * 3)
        S.key(o, f0 + n + 1, scale=(0.001,) * 3)
    S.cue("pop", f0, vol=-9)


def wobble(S, rk, f, amp=3.0, base=(BX, 0, RZ), n=4):
    """La roca se mece un pelo (amortiguada)."""
    for k in range(n):
        sgn = 1 if k % 2 == 0 else -1
        S.key(rk, f + k * 3 + 1, loc=base, rot=(0, R(sgn * amp * (0.6 ** k)), 0), scale=(1 + 0.012 * (n - k) * sgn, 1, 1 - 0.012 * (n - k) * sgn))
    S.key(rk, f + n * 3 + 3, loc=base, rot=(0, 0, 0), scale=(1, 1, 1))


def blinks(S, a, frames):
    for f in frames: a.blink(f)


def rock_base(S, rk, loc=(BX, 0, RZ)):
    S.key(rk, 1, loc=loc, rot=(0, 0, 0), scale=(1, 1, 1))


# ------------------------------------------------------------------ nivel -500
def l1(S):
    """-500: empuja con la espalda (ya en el fotograma 1), no se mueve, corre y rebota suave con estrellas."""
    rk, stone, foam, rockx = build_set(S); rock_base(S, rk)
    xc = BX - rockx(1.1, -1) - 0.30                                   # espalda contra la roca
    a = S.actor(x=xc); a.yaw = -75; S.key(a.root, 1, rot=(0, 0, R(-75)), loc=(xc, 0, 0)); a.tilt(0, 1)
    # tres empujones de espalda: se echa atrás, aprieta las piernas, la roca ni se entera
    f = 1
    pose(S, a, f, lean=-10, thigh=(8, 28), knee=(30, 40), arm=(25, 18), elbow=(-30, -30))
    for k in range(3):
        f0 = 1 + k * 15
        pose(S, a, f0 + 5, lean=-20, thigh=(22, 40), knee=(56, 60), arm=(45, 40), elbow=(-50, -50))
        S.key(a.root, f0 + 5, loc=(xc + 0.03, 0, -0.02)); S.key(a.root, f0, loc=(xc, 0, 0))
        S.key(a.head, f0 + 5, rot=(R(-8), 0, 0))
        pose(S, a, f0 + 11, lean=-8, thigh=(6, 24), knee=(30, 34), arm=(22, 16), elbow=(-30, -30))
        S.key(a.root, f0 + 11, loc=(xc, 0, 0)); S.key(a.head, f0 + 11, rot=(R(2), 0, 0))
        S.cue("creak", f0 + 5, vol=-10)
        if k == 0: dust(S, BX - 0.5, 0.02, f0 + 6, n=4, spread=0.35, size=0.07, y=-0.55)
        if k == 2: wobble(S, rk, f0 + 6, amp=0.6, n=2)
    a.blink(18); a.look(0.02, 0, 40)
    S.f = 46
    pose(S, a, 46, lean=-8, thigh=(6, 24), knee=(30, 34), arm=(22, 16), elbow=(-30, -30))
    # duda: se gira, mira la roca y a cámara, se remanga
    a.face(-30, 47, turn=5); S.f = 50
    pose(S, a, 50, lean=2, thigh=(0, 0), knee=(0, 0), arm=(0, 0), elbow=(-25, -25), interp="BEZIER")
    a.look(0.03, 0.04, 50); a.blink(54); S.key(a.head, 52, rot=(R(6), 0, R(-12))); S.key(a.head, 60, rot=(0, 0, 0))
    S.wait(10)
    # corre lejos hacia la izquierda
    a.face(-75, S.f, turn=3); f0 = S.f
    n = a.mocap("correr", travel_to=BX - 3.3, start=0.4)
    for k in range(4, n, 6): S.cue("step", f0 + k, vol=-8)
    S.cue("whoosh", f0, vol=-12)
    # anticipación: da media vuelta, respira hondo y mira
    f1 = S.f
    a.face(0, f1, turn=4); pose(S, a, f1 + 2, lean=6, thigh=(-6, 4), knee=(8, 4), arm=(10, 10), elbow=(-35, -35))
    S.key(a.pivot, f1 + 8, rot=(R(16), 0, 0)); S.f = f1 + 9; a.blink(f1 + 5)
    a.face(75, S.f, turn=4); S.wait(3)
    # carrerón contra la roca
    f2 = S.f
    xa = BX - rockx(1.0, -1) - 0.42
    n = a.mocap("correr", travel_to=xa, start=0.4)
    for k in range(3, n, 6): S.cue("step", f2 + k, vol=-8)
    S.cue("whoosh", f2 + 2, vol=-10)
    fc = S.f                                                              # choque suave: rebote y cae sentado
    S.key(a.root, fc, loc=(xa, 0, 0), rot=(0, 0, R(75)))
    pose(S, a, fc, lean=14, thigh=(-15, 20), knee=(20, 30), arm=(-40, -40), elbow=(-30, -30))
    S.key(a.pivot, fc + 1, rot=(R(26), 0, 0), scale=(1.06, 1.0, 0.9))
    S.cue("boing", fc, vol=-4)
    wobble(S, rk, fc, amp=2.5, n=4)
    dust(S, BX - 0.9, 0.9, fc, n=6, spread=0.4, size=0.1, y=-0.6, rise=0.2)
    xs = xa - 1.1
    S.key(a.root, fc + 4, loc=(xa - 0.35, 0, 0.12)); S.key(a.pivot, fc + 4, rot=(R(-10), 0, 0), scale=(1, 1, 1))
    pose(S, a, fc + 4, lean=-18, thigh=(18, -4), knee=(30, 25), arm=(70, 85), elbow=(-20, -20), spread=(25, 25))
    hip = a._dims["hip"]
    S.key(a.root, fc + 12, loc=(xs, 0, 0.30)); a.face(-30, fc + 9, turn=6)
    pose(S, a, fc + 12, lean=-30, thigh=(-50, -50), knee=(30, 30), arm=(35, 35), elbow=(-10, -10), spread=(20, 20))
    S.key(a.root, fc + 18, loc=(xs - 0.1, 0, 0.12 - hip + 0.08))                 # se sienta de golpe
    a.sit(fc + 18, knee=10); S.key(a.pivot, fc + 18, rot=(R(-6), 0, 0), scale=(1.04, 1.04, 0.92)); S.cue("pop", fc + 17, vol=-5)
    S.key(a.pivot, fc + 22, rot=(R(-3), 0, 0), scale=(1, 1, 1))
    for i in (0, 1): S.key(a.arms[i], fc + 18, rot=(R(-8), R((12 if i == 0 else -12)), 0)); S.key(a.elbows[i], fc + 18, rot=(R(-30), 0, 0))
    S.key(a.head, fc + 18, rot=(R(10), 0, R(8))); S.key(a.head, fc + 36, rot=(R(5), 0, R(-8)))
    daze(S, a, fc + 18, n=22)
    S.f = fc + 18; a.look(0.03, -0.02, fc + 20); a.blink(fc + 30)
    S.f = fc + 44
    return a


# ------------------------------------------------------------------ nivel -80
def l2(S):
    """-80: salta encima para empujar con su peso, resbala hacia delante y se queda colgado del borde (de espaldas a cámara)."""
    rk, stone, foam, rockx = build_set(S); rock_base(S, rk)
    xs0 = BX - 3.2
    a = S.actor(x=xs0); a.yaw = 75; S.key(a.root, 1, rot=(0, 0, R(75)), loc=(xs0, 0, 0))
    f0 = S.f
    xl = BX - 2.0
    n = a.mocap("correr", travel_to=xl, start=0.4)                       # carrerilla
    for k in range(2, n, 6): S.cue("step", f0 + k, vol=-8)
    S.cue("whoosh", f0, vol=-12)
    xt = BX - 0.30; zt = RZ + RSC[2] * 0.97                                # encima de la roca
    a.hop_to(xt, z=zt - 0.04, h=0.9, dur=17, sound=None); S.cue("boing", S.f - 18, vol=-6)
    ft = S.f
    dust(S, BX - 0.2, zt, ft, n=3, spread=0.3, size=0.05, y=-0.4, rise=0.15)
    wobble(S, rk, ft, amp=0.8, n=2)
    # empuja con su peso: rebotes encima de la roca (la roca ni se inmuta)
    xz = BX - 0.30
    for k in range(3):
        g = ft + 4 + k * 10
        S.key(a.root, g, loc=(xz, 0, zt - 0.04)); S.key(a.root, g + 5, loc=(xz + 0.02, 0, zt - 0.22)); S.key(a.root, g + 9, loc=(xz, 0, zt - 0.04))
        pose(S, a, g, lean=4, thigh=(0, 0), knee=(0, 0), arm=(-10, -10), elbow=(-20, -20))
        pose(S, a, g + 5, lean=32, thigh=(-40, -40), knee=(78, 78), arm=(-70, -70), elbow=(-35, -35))
        pose(S, a, g + 9, lean=6, thigh=(-6, -6), knee=(8, 8), arm=(-12, -12), elbow=(-20, -20))
        S.cue("clunk", g + 5, vol=-12)
        if k == 0: S.key(a.head, g, rot=(0, 0, 0))
    S.f = ft + 36
    # duda: mira a la roca, a cámara, traga saliva
    a.face(-30, S.f, turn=5); pose(S, a, S.f + 5, lean=2, arm=(-6, -6), elbow=(-20, -20)); a.blink(S.f + 4); a.look(0.03, 0.03, S.f + 3)
    S.key(a.head, S.f + 6, rot=(R(4), 0, R(-10)))
    S.cue("pop", S.f + 18, vol=-14)
    S.wait(14); fs = S.f
    # resbala hacia el frente: los pies se le van, brazos al aire, se desliza por el lomo hasta el borde
    a.face(-5, fs, turn=2)
    pose(S, a, fs + 3, lean=-12, thigh=(10, -10), knee=(6, 40), arm=(60, 70), elbow=(-15, -15), spread=(30, 30))
    S.key(a.root, fs + 3, loc=(xz + 0.05, -0.1, zt - 0.06)); S.cue("slide_down", fs + 3, vol=-8)
    pose(S, a, fs + 8, lean=-35, thigh=(-40, -55), knee=(25, 20), arm=(-130, -140), elbow=(-15, -15), spread=(15, 15))
    S.key(a.root, fs + 8, loc=(xz + 0.1, -0.35, zt - 0.28))
    # cuelga del borde delantero: de cara a la roca (de espaldas a cámara), brazos arriba agarrados, piernas pataleando
    a.face(180, fs + 10, turn=5)
    hold_z = RZ + RSC[2] * 0.82
    xh0 = BX + 0.0; ext = S.rocky(hold_z)
    y0h, z0h = -(ext + 0.30), hold_z - 1.62
    pose(S, a, fs + 17, lean=-2, thigh=(-80, -74), knee=(100, 92), arm=(-146, -146), elbow=(-12, -12), spread=(0, 0), interp="BACK")
    S.key(a.root, fs + 17, loc=(xh0, y0h, z0h), rot=(0, 0, R(180)))
    hp = hand_pos(S, a, 1, fs + 17)                                      # las manos justo en el borde de la roca
    yh = -(S.rocky(1.0) + 0.15); zr = z0h + (hold_z - hp.z)
    S.key(a.root, fs + 17, loc=(xh0, yh, zr), rot=(0, 0, R(180))); S.cue("clunk", fs + 17, vol=-8)
    S.key(a.root, fs + 13, loc=(xh0, yh - 0.25, zr + 0.45), rot=(0, 0, R(180)))
    S.key(a.head, fs + 17, rot=(R(-10), 0, 0))
    for k in range(5):                                                   # pataleo
        g = fs + 22 + k * 8; sg = 1 if k % 2 == 0 else -1
        pose(S, a, g, lean=-2 + 3 * sg, thigh=(-76 - 12 * sg, -76 + 12 * sg), knee=(96 + 20 * sg, 96 - 20 * sg), arm=(-146, -146), elbow=(-12, -12))
        S.key(a.root, g, loc=(xh0, yh, zr - 0.02 * sg), rot=(0, 0, R(180)))
    S.key(a.head, fs + 30, rot=(R(-8), 0, R(10)))
    S.key(a.head, fs + 38, rot=(R(-8), 0, R(150)))                       # gira la cabeza hacia cámara con cara de circunstancias
    a.look(0.03, 0, fs + 36); a.blink(fs + 46); a.blink(fs + 60)
    S.key(rk, fs + 34, loc=(BX, 0, RZ), rot=(0, 0, 0), scale=(1, 1, 1))  # la roca, impertérrita
    S.f = fs + 64
    return a


# ------------------------------------------------------------------ nivel 130
def l3(S):
    """130: empuja con todo el cuerpo (centímetro a centímetro), la roca avanza; se tumba exhausto y orgulloso."""
    rk, stone, foam, rockx = build_set(S); rock_base(S, rk)
    d_push = 0.20                                                        # separación entre el pecho y la roca
    xa = BX - rockx(1.15, -1) - 0.92
    a = S.actor(x=xa); a.yaw = 75; S.key(a.root, 1, rot=(0, 0, R(75)), loc=(xa, 0, 0))
    S.f = 1
    n = 100
    a.mocap("empujar", frames=n, root=False, start=3.0, strength=0.5)   # empuje real (mitad de amplitud: la roca es alta); trayectoria propia
    for f in range(1, n + 1):                                            # brazos a la altura del pecho, manos sobre la roca
        w = 3 * math.sin(f * 0.33)
        for i in (0, 1):
            S.key(a.arms[i], f, rot=(R(-84 + w), R((4 if i == 0 else -4)), 0)); S.key(a.elbows[i], f, rot=(R(-14 - w), 0, 0))
    hp = hand_pos(S, a, 1, 30); dxh = BX - rockx(hp.z, -1) + 0.04 - hp.x
    xa += dxh; S.key(a.root, 1, loc=(xa, 0, 0), rot=(0, 0, R(75)))
    S.f = 1
    tot = 1.15; steps = 6; per = n // steps
    xr = [(0.0, 0.0)]
    for k in range(steps):
        g = 1 + k * per
        x0 = tot * k / steps; x1 = tot * (k + 1) / steps
        pairs = ((g, x0), (g + per * 0.45, x0 + (x1 - x0) * 1.12), (g + per * 0.62, x1 - (x1 - x0) * 0.08), (g + per - 1, x1))
        for (ff, dx) in pairs:
            S.key(a.root, int(ff), loc=(xa + dx, 0, 0), rot=(0, 0, R(75)))
            S.key(rk, int(ff), loc=(BX + dx, 0, RZ), rot=(0, R(-0.8 * (1 if k % 2 else -1)), 0))
        S.cue("creak", g + 3, vol=-9)
        dust(S, BX + x0 - 0.2, 0.05, g + 4, n=4, spread=0.45, size=0.08, y=-0.55, seed=k)
        if k % 2 == 0: sweat(S, a, g + 6, seed=k)
    sweat(S, a, 70); sweat(S, a, 96)
    for f in (22, 58, 90): a.blink(f)
    S.f = n; fx = xa + tot; fl = 1 + steps * per
    S.cue("clunk", fl, vol=-8)
    wobble(S, rk, fl + 2, amp=1.2, base=(BX + tot, 0, RZ), n=3)
    # suelta: se endereza jadeando, se da la vuelta, se aleja tambaleante y se deja caer de espaldas, exhausto
    S.f = fl
    pose(S, a, fl + 2, lean=14, thigh=(-18, 10), knee=(34, 10), arm=(-55, -55), elbow=(-40, -40))
    pose(S, a, fl + 10, lean=-2, thigh=(0, 0), knee=(4, 4), arm=(15, 15), elbow=(-25, -25))
    S.key(a.root, fl + 10, loc=(fx, 0, 0), rot=(0, 0, R(75)))
    S.f = fl + 12
    a.face(-75, S.f, turn=4); S.wait(4); f_w = S.f
    nw = a.mocap("caminar", travel_to=fx - 1.5)
    for k in range(5, nw, 12): S.cue("step", f_w + k, vol=-8)
    xl_ = fx - 1.5; fq = S.f
    hip = a._dims["hip"]; lz = 0.12 - hip
    pose(S, a, fq, lean=-2, thigh=(0, 0), knee=(4, 4), arm=(6, 6), elbow=(-30, -30))
    S.key(a.root, fq, loc=(xl_, 0, 0), rot=(0, 0, R(-75)))
    pose(S, a, fq + 6, lean=-6, thigh=(-6, -6), knee=(30, 30), arm=(10, 10), elbow=(-30, -30))
    S.key(a.root, fq + 6, loc=(xl_ - 0.05, 0, -0.04))
    S.key(a.root, fq + 12, loc=(xl_ - 0.25, 0, lz + 0.3))
    pose(S, a, fq + 12, lean=-40, thigh=(-55, -55), knee=(60, 60), arm=(25, 25), elbow=(-25, -25), interp="BACK")
    S.key(a.root, fq + 18, loc=(xl_ - 0.45, 0, lz)); S.cue("pop", fq + 18, vol=-6)
    pose(S, a, fq + 18, lean=-84, thigh=(-86, -86), knee=(6, 6), arm=(-10, -10), elbow=(-20, -20), spread=(35, 35), interp="BACK")
    dust(S, xl_ - 0.45, 0.05, fq + 18, n=5, spread=0.5, size=0.08, y=-0.3, rise=0.2)
    S.key(a.head, fq + 18, rot=(R(10), 0, 0)); S.key(a.head, fq + 36, rot=(R(10), 0, R(-15)))
    for k in range(3):                                                   # respira hondo
        g = fq + 22 + k * 10
        S.key(a.pivot, g, rot=(R(-84), 0, 0), scale=(1, 1, 1)); S.key(a.pivot, g + 5, rot=(R(-84), 0, 0), scale=(1.02, 1.0, 1.05))
    a.blink(fq + 24); sweat(S, a, fq + 24); sweat(S, a, fq + 40)
    # orgulloso: levanta el puño al cielo y sonríe a cámara
    g = fq + 42
    pose(S, a, g, lean=-84, thigh=(-86, -86), knee=(6, 6), arm=(-10, -10), elbow=(-20, -20), spread=(35, 35))
    pose(S, a, g + 8, lean=-84, thigh=(-86, -86), knee=(6, 6), arm=(-10, -165), elbow=(-20, -40), spread=(35, 5), interp="BACK")
    pose(S, a, g + 22, lean=-84, thigh=(-86, -86), knee=(6, 6), arm=(-10, -165), elbow=(-20, -40), spread=(35, 5))
    S.cue("tada", g + 8, vol=-8)
    S.key(a.head, g + 8, rot=(R(6), 0, R(-25))); a.blink(g + 14)
    S.f = g + 28
    return a


# ------------------------------------------------------------------ nivel 900
def l4(S):
    """900: tablón como palanca. Salta sobre el extremo, la roca sube y rueda a un lado; salta de alegría."""
    rk, stone, foam, rockx = build_set(S); rock_base(S, rk)
    woodp = S.mats["p_tablon"]
    lg = S.obj("cylinder", "tronco_palanca", "wood", (BX - 1.1, 0, 0.17), (0.17, 0.17, 0.5), rot=(R(90), 0, 0), vertices=18); lg.data.materials[0] = S.mats["p_madera_banco"]
    px, pz = BX - 1.1, 0.40
    pv = S.empty("palanca", (px, 0, pz))
    pl = S.obj("cube", "tablon", "wood", (-0.05, 0, 0.0), (0.70, 0.20, 0.035), parent=pv, smooth=False); pl.data.materials[0] = woodp
    for dx in (-0.70, -0.40, 0.45):
        S.obj("cube", "clavo", "metal", (dx - 0.05, 0, 0.037), (0.014, 0.014, 0.005), parent=pv, smooth=False)
    T0 = 14                                                              # ángulo de reposo: el extremo de la roca abajo
    S.key(pv, 1, loc=(px, 0, pz), rot=(0, R(T0), 0))
    xa = BX - 2.6
    a = S.actor(x=xa); a.yaw = 75; S.key(a.root, 1, rot=(0, 0, R(75)), loc=(xa, 0, 0))
    # f1: ya colocando el tablón (inclinado, manos en el extremo): lo desliza bajo la roca
    pose(S, a, 1, lean=36, thigh=(-30, 10), knee=(40, 16), arm=(-78, -78), elbow=(-30, -30))
    S.key(a.head, 1, rot=(R(-20), 0, 0))
    S.key(pv, 1, loc=(px - 0.55, 0, pz), rot=(0, R(T0), 0))
    S.key(pv, 14, loc=(px, 0, pz), rot=(0, R(T0), 0))
    S.cue("slide_down", 3, vol=-12); S.cue("clunk", 14, vol=-8)
    dust(S, px - 1.0, 0.05, 12, n=3, spread=0.3, size=0.06, y=-0.4, rise=0.1)
    pose(S, a, 12, lean=34, thigh=(-30, 10), knee=(40, 16), arm=(-78, -78), elbow=(-30, -30))
    S.key(a.root, 1, loc=(xa, 0, 0), rot=(0, 0, R(75))); S.key(a.root, 14, loc=(xa + 0.55, 0, 0), rot=(0, 0, R(75)))
    pose(S, a, 20, lean=0, arm=(-8, -8), elbow=(-25, -25))
    S.key(a.head, 14, rot=(R(-10), 0, 0)); S.key(a.head, 20, rot=(0, 0, 0))
    # mira la palanca, se frota la barbilla: idea
    a.face(-30, 22, turn=5); a.blink(26)
    a.look(0.03, 0.04, 24)
    pose(S, a, 30, lean=0, arm=(-50, 0), elbow=(-110, -20))
    S.key(a.head, 28, rot=(R(5), 0, R(-8)))
    pose(S, a, 36, lean=0, arm=(-3, -3), elbow=(-25, -25)); S.cue("pop", 32, vol=-8)
    S.f = 38
    a.face(-75, S.f, turn=3)
    xs = px - 0.70 - 0.85
    a.mocap("correr", travel_to=xs - 0.0, root=True) if False else None
    n = a.mocap("caminar", travel_to=xs)
    for k in range(5, n, 12): S.cue("step", 38 + k, vol=-8)
    a.face(75, S.f, turn=3); S.wait(3)
    # salta sobre el extremo alto del tablón
    xe = px - 0.68
    ze = pz + math.sin(R(T0)) * 0.68 + 0.05
    a.hop_to(xe, z=ze, h=0.5, dur=12, sound=None); S.cue("boing", S.f - 12, vol=-6)
    fl = S.f - 3                                                         # aterriza
    # la palanca baja por su lado: la roca sube, se tambalea y rueda lentamente
    ang = -17
    for k, (ff, an) in enumerate(((fl, T0), (fl + 5, ang), (fl + 9, ang + 2), (fl + 13, ang))):
        S.key(pv, ff, loc=(px, 0, pz), rot=(0, R(an), 0), interp="BEZIER")
    zend = pz - math.sin(R(-ang)) * 0.68 + 0.09
    S.key(a.root, fl, loc=(xe, 0, ze), rot=(0, 0, R(75)))
    S.key(a.root, fl + 5, loc=(xe + 0.06, 0, zend)); S.key(a.root, fl + 9, loc=(xe + 0.06, 0, zend + 0.07)); S.key(a.root, fl + 13, loc=(xe + 0.06, 0, zend))
    pose(S, a, fl + 5, lean=14, thigh=(-30, -30), knee=(60, 60), arm=(60, 60), elbow=(-20, -20))
    pose(S, a, fl + 10, lean=0, thigh=(-6, -6), knee=(10, 10), arm=(-30, -30), elbow=(-20, -20))
    S.cue("clunk", fl + 4, vol=-6); S.cue("creak", fl + 6, vol=-8)
    # roca: levanta un poco, se inclina y rueda ~1,1 m con paradas
    x0 = BX
    S.key(rk, fl, loc=(x0, 0, RZ), rot=(0, 0, 0))
    S.key(rk, fl + 6, loc=(x0 + 0.04, 0, RZ + 0.30), rot=(0, R(8), 0))
    S.key(rk, fl + 14, loc=(x0 + 0.20, 0, RZ + 0.38), rot=(0, R(24), 0))
    S.key(rk, fl + 22, loc=(x0 + 0.32, 0, RZ + 0.05), rot=(0, R(50), 0))
    S.key(rk, fl + 28, loc=(x0 + 0.38, 0, RZ), rot=(0, R(62), 0), interp="BACK")
    S.key(rk, fl + 38, loc=(x0 + 0.50, 0, RZ), rot=(0, R(82), 0))
    S.key(rk, fl + 50, loc=(x0 + 0.56, 0, RZ), rot=(0, R(92), 0))
    for g, dx in ((fl + 22, 0.32), (fl + 29, 0.38), (fl + 40, 0.5)):
        dust(S, BX + dx, 0.05, g, n=5, spread=0.55, size=0.12, y=-0.5, seed=g)
    S.cue("clunk", fl + 22, vol=-6); S.cue("clunk", fl + 29, vol=-9); S.cue("whoosh", fl + 14, vol=-12)
    a.blink(fl + 16); a.look(0.03, 0.02, fl + 14)
    # salta de alegría
    S.f = fl + 30
    a.cheer(times=1)
    S.key(rk, S.f, loc=(x0 + 0.56, 0, RZ), rot=(0, R(92), 0))
    S.f += 8
    return a


# ------------------------------------------------------------------ nivel 5200
def l5(S):
    """5200: mira alrededor, se acerca, toca la roca con un dedo: es de espuma. La levanta con un dedo, la deja a un lado y saluda."""
    rk, stone, foam, rockx = build_set(S); rock_base(S, rk)
    xa = BX - 2.75
    a = S.actor(x=xa); S.key(a.root, 1, loc=(xa, 0, 0), rot=(0, 0, R(-30)))
    # mira alrededor (captura "mirar"); la roca tiembla un pelo (siembra la espuma)
    n = a.mocap("mirar", frames=28, root=False, start=1.0, strength=0.75)
    S.f = 1
    wobble(S, rk, 10, amp=0.9, n=2); wobble(S, rk, 21, amp=1.1, n=2)
    for f in (10, 30): a.blink(f)
    S.f = 30
    a.face(75, S.f, turn=3)
    xp = BX - rockx(1.1, -1) - 0.62
    f0 = S.f
    n = a.mocap("caminar", travel_to=xp)
    for k in range(5, n, 12): S.cue("step", f0 + k, vol=-8)
    fp = S.f
    # se para, ladea la cabeza y extiende un dedo
    a.look(0.03, 0.03, fp); a.blink(fp + 4)
    S.key(a.head, fp + 3, rot=(R(5), 0, R(-8)))
    pose(S, a, fp, lean=0, arm=(-8, -8), elbow=(-20, -20))
    pose(S, a, fp + 5, lean=4, arm=(-8, -45), elbow=(-20, -50), interp="BEZIER")
    pose(S, a, fp + 11, lean=8, arm=(-8, -88), elbow=(-20, -8), interp="BEZIER")
    S.key(a.root, fp, loc=(xp, 0, 0), rot=(0, 0, R(75)))
    # toque 1: la roca se tambalea
    S.key(a.pivot, fp + 12, rot=(R(8), 0, 0))
    S.cue("pop", fp + 12, vol=-10)
    wobble(S, rk, fp + 12, amp=3.2, n=4)
    pose(S, a, fp + 16, lean=-2, arm=(-8, -80), elbow=(-20, -10))
    S.key(a.head, fp + 14, rot=(R(-6), 0, R(-6)))
    a.blink(fp + 18)
    # toque 2: la roca cede, se hunde el dedo... es de espuma (cambia el material)
    S.key(a.pivot, fp + 26, rot=(R(2), 0, 0)); pose(S, a, fp + 26, lean=2, arm=(-8, -85), elbow=(-20, -10))
    pose(S, a, fp + 30, lean=8, arm=(-8, -92), elbow=(-20, -6))
    fs_ = fp + 30
    S.key(stone, fs_ - 1, scale=RSC); S.key(stone, fs_, scale=(0.001,) * 3)
    S.key(foam, fs_ - 1, scale=(0.001,) * 3); S.key(foam, fs_, scale=RSC)
    S.key(rk, fs_ - 1, loc=(BX, 0, RZ), rot=(0, 0, 0), scale=(1, 1, 1))
    S.key(rk, fs_ + 3, loc=(BX + 0.05, 0, RZ), rot=(0, R(7), 0), scale=(0.93, 1, 1.0))
    S.key(rk, fs_ + 8, loc=(BX, 0, RZ), rot=(0, R(-3), 0), scale=(1.04, 1, 1.0))
    S.key(rk, fs_ + 12, loc=(BX, 0, RZ), rot=(0, 0, 0), scale=(1, 1, 1))
    S.cue("boing", fs_, vol=-5)
    dust(S, BX - 0.6, 1.0, fs_, n=7, spread=0.5, size=0.07, y=-0.6, rise=0.25)
    for i in range(6):   # migajitas de espuma
        c = S.obj("uv_sphere", "migaja", "foam", (BX - 0.65, -0.6, 1.0), (0.001,) * 3, segments=6, ring_count=4); rr = random.Random(i)
        S.key(c, fs_ - 1, scale=(0.001,) * 3); S.key(c, fs_ + 1, loc=(BX - 0.65, -0.6, 1.0), scale=(0.035,) * 3)
        S.key(c, fs_ + 14, loc=(BX - 0.65 + rr.uniform(-0.5, 0.2), -0.6 + rr.uniform(-0.2, 0.1), 0.06), scale=(0.03,) * 3); S.key(c, fs_ + 16, scale=(0.001,) * 3)
    # cara de sorpresa a cámara; sonríe
    a.face(-30, fs_ + 6, turn=5); a.look(0.0, 0.0, fs_ + 8); a.blink(fs_ + 14)
    S.key(a.head, fs_ + 10, rot=(R(-4), 0, R(8)))
    pose(S, a, fs_ + 8, lean=-3, arm=(-8, -50), elbow=(-20, -30))
    pose(S, a, fs_ + 14, lean=0, arm=(-8, -8), elbow=(-20, -20))
    S.f = fs_ + 16
    # levanta la roca con un dedo: el brazo sube, la roca flota sobre la yema
    fl = S.f
    for i, (sh, el) in enumerate(zip(a.arms, a.elbows)): pass
    ya = -150
    pose(S, a, fl, lean=0, arm=(-8, -8), elbow=(-20, -20))
    pose(S, a, fl + 6, lean=2, arm=(-8, -75), elbow=(-20, -10), spread=(0, -20), interp="BEZIER")
    pose(S, a, fl + 16, lean=-4, arm=(-8, ya), elbow=(-20, -6), spread=(0, -6), interp="BACK")
    S.key(a.root, fl, loc=(xp, 0, 0), rot=(0, 0, R(-30)))
    S.cue("whoosh", fl + 4, vol=-8)
    # la roca sigue a la yema (posición calculada fotograma a fotograma)
    s_x = xp; hr = (RSC[2]) * 0.78
    S.f = fl + 16

    def hand_key(f, blend, extra=(0, 0, 0), spin=0.0):
        hp = hand_pos(S, a, 1, f)
        tgt = Vector((hp.x, hp.y, hp.z + hr + 0.02)) + Vector(extra)
        start = Vector((BX, 0, RZ))
        p = start.lerp(tgt, blend)
        S.key(rk, f, loc=tuple(p), rot=(0, 0, R(spin)), scale=(1, 1, 1), interp="LINEAR")
    for f in range(fl, fl + 17):
        hand_key(f, ss((f - fl - 4) / 12.0), spin=(f - fl) * 2.5)
    S.cue("pop", fl + 8, vol=-8)
    # la lleva a un lado (paso a paso, con la roca girando suave sobre el dedo) y la deja detrás del camino
    S.f = fl + 17
    f2 = S.f; xt = xp + 1.5
    a.face(75, f2, turn=4)
    a.look(0.0, 0.0, f2)
    n = a.mocap("caminar", travel_to=xt)
    for k in range(5, n, 12): S.cue("step", f2 + k, vol=-8)
    # el brazo derecho se mantiene arriba y la mano (con el cuerpo) mueve la roca
    for f in range(f2, f2 + n):
        S.key(a.arms[1], f, rot=(R(-150 + 4 * math.sin((f - f2) * 0.5)), R(-6), 0)); S.key(a.elbows[1], f, rot=(R(-6), 0, 0))
        hp = hand_pos(S, a, 1, f)
        t = ss((f - f2 - (n - 14)) / 14.0)                               # al final la deja caer detrás del camino
        tgt = Vector((hp.x + 0.35 * t, hp.y + 1.25 * t, hp.z + hr + 0.02 - (hp.z + hr + 0.02 - RZ) * t))
        S.key(rk, f, loc=tuple(tgt), rot=(0, 0, R(60 + (f - f2) * 2.0)), scale=(1, 1, 1), interp="LINEAR")
    S.cue("clunk", f2 + n - 2, vol=-8)
    fe = S.f
    dust(S, xt + 0.4, 0.03, fe, n=6, spread=0.5, size=0.1, y=1.2, rise=0.3)
    # baja el brazo, se gira a cámara y saluda
    a.face(-30, fe, turn=5)
    pose(S, a, fe, lean=0, arm=(-8, -150), elbow=(-20, -6))
    pose(S, a, fe + 8, lean=0, arm=(-8, -8), elbow=(-20, -20))
    S.key(a.root, fe, loc=(xt, 0, 0), rot=(0, 0, R(75))); S.key(a.root, fe + 5, loc=(xt, 0, 0), rot=(0, 0, R(-30)))
    S.f = fe + 8; a.blink(fe + 6)
    n = a.mocap("saludar", frames=34, root=False, start=0.6, strength=0.9)
    S.cue("pop", fe + 16, vol=-10)
    a.blink(fe + 30)
    S.f = fe + 8 + n + 4
    return a


LEVELS = [(-500, l1), (-80, l2), (130, l3), (900, l4), (5200, l5)]
