"""ep019 — Every IQ Level Catches the Drone (story-022, idea b20261123-4-i01). Azotea urbana (env_real.build_rooftop, muy producida), humano de Mixamo
con el protagonista de klunk_toon. Un dron naranja y blanco (primitivas, ~70 cm, 4 hélices girando, luces de posición parpadeando) zumba a ~2,8 m.

EL MANDO (clave del remate): caja ROJA de 30 x 18 cm con dos palancas amarillas, antena, pantalla y luz que parpadea, colgada del cuello con un
cordón en V. Se ve en el pecho desde el fotograma 1 de CADA nivel y rebota (muelle amortiguado sobre la aceleración del pecho; se calcula por
fotograma a partir de los huesos), así que el espectador lo ve antes que el personaje.

  -450 Ya saltando bajo el dron con el mando rebotando; salta más fuerte, cae de espaldas (Falling Back Death); el dron sube y zumba más rápido.
  -80  Lanza un zapato (Throw) al dron; falla, rebota en el depósito de agua (clunk hueco) y le da en la cabeza; el dron esquiva girando; se enfada.
  120  Trepa por la escalera del depósito (Climbing Up Wall); el mando golpea un peldaño (clunk, la palanca se mueve): el dron pica en picado,
       casi lo roza y sube; se queda agarrado temblando.
  900  Salta, agarra el patín del dron (Climbing A Rope), el dron lo arrastra por la azotea hacia las sábanas (que se agitan); lo suelta y se ríe.
  5469 Mira alrededor, mira abajo (Thinking), levanta el mando (Button Pushing), empuja la palanca: el dron baja y aterriza en sus manos
       (Victory, primer plano, tada); el dron vuelve a subir al final (bucle).
Convenio: yaw 0 = mira a cámara (-y); mira hacia (sin yaw, -cos yaw). 24 fps."""
import math
import bpy
from mathutils import Vector, Matrix, Euler
from mixamo import MixamoActor
from klunk_toon import apply as klunk, expression, blink
import env_real

TITLE = "Every IQ Level Catches the Drone"
ONSCREEN = "Every IQ level catches the drone"
ENV = "mesa"                       # base mínima del kit; build_rooftop la vacía y monta la azotea
CUSTOM_CAMERA = True
LABEL_STYLE = "big"

TANK = (3.0, 1.8)                  # centro del depósito de agua (radio 1,0; cara -x en x = 1,94)
HOVER = Vector((0.15, 0.2, 2.8))   # el dron zumba aquí (centro del cuerpo)
CW, CD, CH = 0.36, 0.07, 0.22      # mando: ancho, fondo, alto (m): exagerado (pedido ~25 x 15) para leerse en plano medio en vertical
CAM_Y, CAM_Z, TGT_Z = -7.0, 3.1, 1.75     # plano medio: personaje ~34 % del alto, pies al ~17 %, cabeza al ~50 %


def R(d): return math.radians(d)
def D(r): return math.degrees(r)
def Rz(d): return Matrix.Rotation(R(d), 4, "Z")
def Ry(d): return Matrix.Rotation(R(d), 4, "Y")
def Rx(d): return Matrix.Rotation(R(d), 4, "X")
def Tm(v): return Matrix.Translation(Vector(v))
def sstep(t): t = max(0.0, min(1.0, t)); return t * t * (3 - 2 * t)
def lerp(a, b, t): return a + (b - a) * t
def Mw(pos, yaw=0.0): return Tm(pos) @ Rz(yaw)


# ------------------------------------------------------------------ materiales y objetos
def mmat(S, name, rgb, rough=0.5, metal=0.0, emit=None, alpha=None):
    k = "m_" + name
    if k in S.mats: return S.mats[k]
    m = bpy.data.materials.new(k); m.use_nodes = True
    b = m.node_tree.nodes["Principled BSDF"]
    b.inputs["Base Color"].default_value = (*rgb, 1); b.inputs["Roughness"].default_value = rough; b.inputs["Metallic"].default_value = metal
    if emit:
        b.inputs["Emission Color"].default_value = (*emit[:3], 1); b.inputs["Emission Strength"].default_value = emit[3]
    if alpha is not None:
        b.inputs["Alpha"].default_value = alpha
        try: m.blend_method = "BLEND"
        except Exception: pass
    S.mats[k] = m
    return m


def O(S, prim, name, mat, loc=(0, 0, 0), scale=(1, 1, 1), rot=(0, 0, 0), parent=None, **kw):
    sm = kw.pop("smooth", True)
    o = S.obj(prim, name, "white", loc, scale, rot, parent, sm, **kw); o.data.materials[0] = mat; return o


def seg(S, a, clip, f0, f1=None, start=0, speed=1.0, blend=4, repeat=None):
    """Reproduce el clip desde f0 hasta f1 (o hasta el final); lo repite las veces que haga falta."""
    S.f = f0
    cl = a.clips[clip]; per = max(1, int((cl.frame_range[1] - cl.frame_range[0] - start) / speed))
    if f1 is None: a.play(clip, frames=None, speed=speed, blend=blend, start=start, repeat=repeat or 1)
    else:
        n = f1 - f0 + blend
        a.play(clip, frames=n, speed=speed, blend=blend, start=start, repeat=repeat or (n // per + 2))


def faces(a, ev, n_end, first_blink=16, every=56):
    f = first_blink
    while f < n_end - 6:
        blink(a, f); f += every
    for f, name, v in ev: expression(a, name, f, v, ramp=3)


PREV = {}


def key_M(S, a, f, M):
    e = M.to_euler("XYZ", PREV.get(id(a), Euler((0, 0, 0)))); PREV[id(a)] = e
    S.key(a.root, f, loc=tuple(M.to_translation()), rot=(e.x, e.y, e.z), interp="LINEAR")


def bone_w(a, bone, frac=0.0):
    pb = a.arm.pose.bones[a.pfx + bone]
    return a.arm.matrix_world @ (pb.head + (pb.tail - pb.head) * frac)


FINGERS = ("Thumb", "Index", "Middle", "Ring", "Pinky")


def pin_feet(S, a, f0, f1, floor, off=0.02, allbones=False):
    """Punto más bajo (pies; o todo el cuerpo si allbones) a floor(f)+off en cada fotograma."""
    for f in range(f0, f1 + 1):
        S.sc.frame_set(f); bpy.context.view_layer.update()
        if allbones:
            zs = [(a.arm.matrix_world @ (pb.head + (pb.tail - pb.head) * fr)).z for pb in a.arm.pose.bones if not any(k in pb.name for k in FINGERS) for fr in (0.0, 1.0)]
        else:
            zs = [(a.arm.matrix_world @ a.arm.pose.bones[a.pfx + b].tail).z for b in ("LeftToeBase", "RightToeBase", "LeftFoot", "RightFoot")]
        d = floor(f) + off - min(zs)
        loc = a.root.location.copy(); rot = a.root.rotation_euler.copy()
        S.key(a.root, f, loc=(loc.x, loc.y, loc.z + d), rot=(rot.x, rot.y, rot.z), interp="LINEAR")


def hand_local(S, a, f):
    """Punto de agarre (media de las dos palmas) en el marco de la raíz."""
    S.sc.frame_set(f); bpy.context.view_layer.update()
    p = (bone_w(a, "LeftHand", 0.6) + bone_w(a, "RightHand", 0.6)) * 0.5
    return a.root.matrix_world.inverted() @ p


def sample(S, a, n):
    """Posiciones (mundo) de los huesos clave por fotograma; se evalúan una vez con la raíz ya animada."""
    out = {}
    for f in range(1, n + 1):
        S.sc.frame_set(f); bpy.context.view_layer.update()
        out[f] = {k: bone_w(a, b, fr) for k, (b, fr) in (("neck", ("Neck", 0.0)), ("hips", ("Hips", 0.0)), ("lsh", ("LeftArm", 0.0)), ("rsh", ("RightArm", 0.0)),
                                                         ("rh", ("RightHand", 0.5)), ("lh", ("LeftHand", 0.5)), ("head", ("Head", 0.5)))}
    return out


def audit_floor(S, a, tag, f0, f1, step=2):
    lo = 9.0
    for f in range(f0, f1 + 1, step):
        S.sc.frame_set(f); bpy.context.view_layer.update()
        for pb in a.arm.pose.bones:
            if any(k in pb.name for k in FINGERS): continue
            for fr in (0.0, 1.0): lo = min(lo, (a.arm.matrix_world @ (pb.head + (pb.tail - pb.head) * fr)).z)
    print(f"AUDITORIA hueso mas bajo {tag}: z {lo:+.3f} m")


# ------------------------------------------------------------------ escenario
def stage(S, N, gust=None, rot_deg=0):
    """Azotea + sábanas ondeando (gust(f) -> 0..1 las agita) + zumbido continuo del dron."""
    E = env_real.build_rooftop(S, rot_deg=rot_deg, tank=TANK, focus=7.1)
    for f in range(1, N + 14, 2):
        g = gust(f) if gust else 0.0
        for i, hg in enumerate(E["sheets"]):
            S.key(hg, f, rot=(R(2.5 * math.sin(0.21 * f + i) + g * 26 * math.sin(0.75 * f + 2 * i) + g * 10), 0, R(g * 6 * math.sin(0.5 * f + i))), interp="LINEAR")
    for f in range(1, N, 9): S.cue("whoosh", f, vol=-20)                 # zumbido de las hélices (cue repetido; ver ISSUES)
    return E


# ------------------------------------------------------------------ dron
def build_drone(S):
    """Dron de primitivas (~70 cm): cuerpo blanco con cúpula naranja, 4 brazos, 4 hélices con disco difuminado, cámara, patines y luces."""
    wh = mmat(S, "dron_blanco", (0.95, 0.95, 0.93), 0.35); org = mmat(S, "dron_naranja", (1.0, 0.38, 0.02), 0.35); drk = mmat(S, "dron_gris", (0.07, 0.07, 0.08), 0.4, 0.3)
    disc = mmat(S, "dron_disco", (0.55, 0.58, 0.62), 0.6, alpha=0.22)
    D_ = S.empty("dron", tuple(HOVER))
    O(S, "cylinder", "d_cuerpo", wh, (0, 0, 0), (0.17, 0.17, 0.045), parent=D_, vertices=32)
    O(S, "uv_sphere", "d_cupula", org, (0, 0, 0.035), (0.15, 0.15, 0.075), parent=D_, segments=24, ring_count=12)
    O(S, "cylinder", "d_cinta", org, (0, 0, -0.012), (0.176, 0.176, 0.014), parent=D_, vertices=32)
    O(S, "uv_sphere", "d_camara", drk, (0, -0.12, -0.075), (0.055, 0.055, 0.055), parent=D_, segments=14, ring_count=10)
    O(S, "cylinder", "d_lente", mmat(S, "dron_lente", (0.05, 0.12, 0.25), 0.1, 0.6), (0, -0.172, -0.075), (0.028, 0.028, 0.012), (R(90), 0, 0), D_, vertices=16)
    props, leds = [], []
    for i, (sx, sy) in enumerate(((-1, -1), (1, -1), (-1, 1), (1, 1))):
        ang = D(math.atan2(sy, sx))
        O(S, "cube", "d_brazo", wh, (sx * 0.115, sy * 0.115, 0.0), (0.17, 0.024, 0.014), (0, 0, R(ang)), D_)
        mx, my = sx * 0.2, sy * 0.2
        O(S, "cylinder", "d_motor", org, (mx, my, 0.015), (0.04, 0.04, 0.03), parent=D_, vertices=16)
        pe = S.empty("d_helice", (mx, my, 0.05), D_); props.append(pe)
        O(S, "cylinder", "d_disco", disc, (0, 0, 0), (0.155, 0.155, 0.002), parent=pe, vertices=32)
        for k in range(2): O(S, "cube", "d_pala", drk, (0, 0, 0.004), (0.15, 0.016, 0.003), (0, 0, R(90 * k)), pe)
        O(S, "uv_sphere", "d_buje", org, (0, 0, 0.008), (0.018, 0.018, 0.014), parent=pe, segments=8, ring_count=6)
    for sx in (-1, 1):                                                  # patines de aterrizaje: dos postes y un tubo largo (el dron se agarra de él)
        for sy in (-1, 1): O(S, "cylinder", "d_pata", drk, (sx * 0.12, sy * 0.1, -0.095), (0.012, 0.012, 0.055), parent=D_, vertices=8)
        O(S, "cylinder", "d_patin", wh, (sx * 0.12, 0, -0.15), (0.017, 0.017, 0.17), (R(90), 0, 0), D_, vertices=12)
    red_on = mmat(S, "led_rojo", (1.0, 0.05, 0.03), 0.3, emit=(1.0, 0.04, 0.02, 14.0)); red_off = mmat(S, "led_rojo_off", (0.15, 0.02, 0.02), 0.5)
    grn_on = mmat(S, "led_verde", (0.05, 1.0, 0.15), 0.3, emit=(0.05, 1.0, 0.12, 14.0)); grn_off = mmat(S, "led_verde_off", (0.02, 0.15, 0.04), 0.5)
    for (px, py, on, off) in ((-0.2, -0.2, red_on, red_off), (0.2, -0.2, red_on, red_off), (-0.2, 0.2, grn_on, grn_off), (0.2, 0.2, grn_on, grn_off)):
        a_ = O(S, "uv_sphere", "d_luz", on, (px, py, -0.03), (0.026, 0.026, 0.026), parent=D_, segments=10, ring_count=6)
        b_ = O(S, "uv_sphere", "d_luz_off", off, (px, py, -0.03), (0.026, 0.026, 0.026), parent=D_, segments=10, ring_count=6); b_.scale = (0, 0, 0)
        leds.append((a_, b_, 0.026, py < 0))
    return D_, props, leds


def drone_keys(S, D_, props, leds, n, pos, tilt=None, yaw=None, spin=1.0):
    """pos(f) -> Vector (centro del dron). Flota con un vaivén y un balanceo suaves; las hélices giran (spin(f) rapidez) y las luces parpadean."""
    for f in range(1, n + 1):
        p = pos(f); t = tilt(f) if tilt else (0.0, 0.0); y = yaw(f) if yaw else 0.0
        bob = Vector((0.018 * math.sin(0.23 * f), 0.012 * math.sin(0.31 * f + 1), 0.035 * math.sin(0.37 * f)))
        S.key(D_, f, loc=tuple(p + bob), rot=(R(t[0] + 3.0 * math.sin(0.29 * f)), R(t[1] + 3.5 * math.sin(0.23 * f + 2)), R(y + 8.0 * math.sin(0.04 * f))), interp="LINEAR")
    ang = 0.0
    for f in range(1, n + 1):
        sp = spin(f) if callable(spin) else spin
        ang += 62.0 * sp
        for i, pe in enumerate(props): S.key(pe, f, rot=(0, 0, R(ang * (1 if i % 2 else -1))), interp="LINEAR")
    for f in range(1, n + 1, 5):
        ph = (f // 5) % 2 == 0
        for a_, b_, s_, front in leds:
            on = ph if front else (not ph)
            S.key(a_, f, scale=(s_,) * 3 if on else (0, 0, 0), interp="CONSTANT"); S.key(b_, f, scale=(0, 0, 0) if on else (s_,) * 3, interp="CONSTANT")


# ------------------------------------------------------------------ mando colgado del cuello
def build_ctrl(S):
    """Mando rojo con pantalla negra, dos palancas amarillas (bisagras animables), antena, luz que parpadea y cordón en V (dos cilindros)."""
    red = mmat(S, "mando_rojo", (0.92, 0.04, 0.03), 0.3); blk = mmat(S, "mando_negro", (0.02, 0.02, 0.025), 0.35); yel = mmat(S, "mando_amarillo", (1.0, 0.82, 0.0), 0.3)
    scr = mmat(S, "mando_pantalla", (0.05, 0.35, 0.40), 0.2, emit=(0.1, 0.9, 1.0, 1.5)); cord = mmat(S, "mando_cordon", (0.02, 0.02, 0.02), 0.7)
    C = S.empty("mando", (0, 0, 2))
    O(S, "cube", "m_caja", red, (0, 0, 0), (CW / 2, CD / 2, CH / 2), parent=C, smooth=False)
    O(S, "cube", "m_pantalla", scr, (-CW * 0.2, CD / 2 + 0.002, CH * 0.14), (CW * 0.2, 0.002, CH * 0.2), parent=C, smooth=False)
    O(S, "cube", "m_franja", blk, (0, CD / 2 + 0.002, -CH * 0.37), (CW * 0.45, 0.002, CH * 0.06), parent=C, smooth=False)
    hinges = []
    for sx in (-1, 1):
        hg = S.empty("m_palanca", (sx * CW * 0.23, CD / 2, -CH * 0.12), C); hinges.append(hg)
        O(S, "cylinder", "m_base", blk, (0, 0.004, 0), (0.030, 0.030, 0.008), (R(90), 0, 0), hg, vertices=14)
        O(S, "cylinder", "m_vara", blk, (0, 0.06, 0), (0.011, 0.011, 0.06), (R(90), 0, 0), hg, vertices=10)
        O(S, "uv_sphere", "m_bola", yel, (0, 0.125, 0), (0.030, 0.030, 0.030), parent=hg, segments=12, ring_count=8)
    O(S, "cylinder", "m_antena", blk, (CW * 0.38, -0.01, CH / 2 + 0.06), (0.007, 0.007, 0.06), (R(-8), 0, 0), C, vertices=8)
    O(S, "uv_sphere", "m_antena_punta", yel, (CW * 0.38, -0.017, CH / 2 + 0.125), (0.015, 0.015, 0.015), parent=C, segments=10, ring_count=6)
    on = mmat(S, "mando_led_on", (1.0, 0.9, 0.1), 0.3, emit=(1.0, 0.85, 0.05, 18.0)); off = mmat(S, "mando_led_off", (0.2, 0.15, 0.02), 0.5)
    l_on = O(S, "uv_sphere", "m_led", on, (CW * 0.36, CD / 2 + 0.005, CH * 0.3), (0.022, 0.022, 0.016), parent=C, segments=10, ring_count=6)
    l_off = O(S, "uv_sphere", "m_led_off", off, (CW * 0.36, CD / 2 + 0.005, CH * 0.3), (0.022, 0.022, 0.016), parent=C, segments=10, ring_count=6); l_off.scale = (0, 0, 0)
    cords = [O(S, "cylinder", "m_cordon", cord, (0, 0, 0), (1, 1, 1), vertices=6, radius=0.007, depth=0.2) for _ in range(2)]
    return C, hinges, (l_on, l_off), cords


def basis(sm):
    """Marco del torso (columnas X lateral, Y adelante, Z arriba) a partir de la cadera, el cuello y los hombros."""
    up = (sm["neck"] - sm["hips"]).normalized()
    fwd = (sm["lsh"] - sm["rsh"]).cross(up); fwd.z *= 0.6; fwd.normalize()
    Z = (up - fwd * up.dot(fwd)).normalized(); X = fwd.cross(Z).normalized()
    return Matrix((X, fwd, Z)).transposed()          # 3x3: columnas = ejes


def attach_ctrl(S, a, sm, n, parts, over=None, lever=None, impulses=(), v0=Vector((0, 0, 0))):
    """Mando sobre el pecho, colgando del cuello: muelle amortiguado con la aceleración del pecho (rebota al saltar y al caer).
    over(f, Mchest) -> M o None (llevar el mando a las manos); lever(f) -> (angulo_izq, angulo_der) en grados sobre la posición de reposo (25)."""
    C, hinges, (l_on, l_off), cords = parts
    chest, B = {}, {}
    for f in range(1, n + 1):
        B[f] = basis(sm[f]); chest[f] = sm[f]["neck"] - B[f].col[2] * 0.27 + B[f].col[1] * 0.145
    d = Vector((0, 0, 0)); v = v0.copy(); w, z = 0.62, 0.10
    for f in range(1, n + 1):
        acc = (chest[min(n, f + 1)] - 2 * chest[f] + chest[max(1, f - 1)])
        v += -(w * w) * d - 2 * z * w * v - acc * 1.2
        for fi, imp in impulses:
            if fi == f: v += imp
        d += v
        if d.length > 0.16: d *= 0.16 / d.length
        Bf = B[f]; tilt = 3.2 * d.dot(Bf.col[2]) + 2.2 * d.dot(Bf.col[1])
        M = Tm(chest[f] + d) @ Bf.to_4x4() @ Rx(D(tilt))
        if over:
            Mo = over(f, M)
            if Mo is not None: M = Mo
        e = M.to_euler("XYZ", PREV.get(id(C), Euler((0, 0, 0)))); PREV[id(C)] = e
        S.key(C, f, loc=tuple(M.to_translation()), rot=(e.x, e.y, e.z), interp="LINEAR")
        lv = lever(f) if lever else (0.0, 0.0)
        for hg, ex in zip(hinges, lv): S.key(hg, f, rot=(R(25.0 + ex), 0, 0), interp="LINEAR")
        for k, sx in enumerate((-1, 1)):                                   # cordón en V: del cuello (a cada lado) a las esquinas superiores del mando
            A = sm[f]["neck"] + Bf.col[0] * (sx * 0.075) + Bf.col[1] * 0.03 + Bf.col[2] * 0.01
            Bp = M @ Vector((sx * CW * 0.42, 0, CH / 2 - 0.004))
            dv = Bp - A; mid = (A + Bp) * 0.5
            q = dv.to_track_quat("Z", "Y").to_euler()
            S.key(cords[k], f, loc=tuple(mid), rot=(q.x, q.y, q.z), scale=(1, 1, dv.length / 0.2), interp="LINEAR")
    for f in range(1, n + 1, 7):
        on = (f // 7) % 2 == 0
        S.key(l_on, f, scale=(0.022, 0.022, 0.016) if on else (0, 0, 0), interp="CONSTANT"); S.key(l_off, f, scale=(0, 0, 0) if on else (0.022, 0.022, 0.016), interp="CONSTANT")


def lever_tip(side=1):
    """Punta de la palanca (marco del mando) con la palanca en reposo (25 grados hacia arriba)."""
    return Vector((side * CW * 0.23, CD / 2 + 0.125 * math.cos(R(25)), -CH * 0.12 + 0.125 * math.sin(R(25))))


# ------------------------------------------------------------------ cámara
def K(keys, f):
    if f <= keys[0][0]: return keys[0][1]
    for (f0, v0), (f1, v1) in zip(keys, keys[1:]):
        if f <= f1: return v0 + (v1 - v0) * ((f - f0) / float(f1 - f0))
    return keys[-1][1]


def cam_follow(S, sm, n, py=None, pz=None, lens=None, tz=None, xoff=None, xw=1.0, zw=0.0, dx_lean=0.0):
    """Cámara: x sigue la cabeza (suavizada +-6 fotogramas); y, z, focal y altura de mirada por claves lineales; zw = peso de la altura de la cabeza.
    Mantiene el foco en la cabeza (profundidad de campo)."""
    py = py or [(1, CAM_Y)]; pz = pz or [(1, CAM_Z)]; lens = lens or [(1, 50.0)]; tz = tz or [(1, TGT_Z)]; xoff = xoff or [(1, 0.0)]
    bpy.context.preferences.edit.keyframe_new_interpolation_type = "LINEAR"
    for f in list(range(1, n + 1, 2)) + [n]:
        ws = [sm[g]["head"] for g in range(max(1, f - 6), min(n, f + 6) + 1)]
        h = sum(ws, Vector((0, 0, 0))) / len(ws)
        cx = h.x * xw + K(xoff, f); tzz = K(tz, f) + zw * (h.z - 1.6)
        S.cam.location = (cx, K(py, f), K(pz, f) + zw * (h.z - 1.6) * 0.7); S.cam.data.lens = K(lens, f); S.tgt.location = (cx, 0.0, tzz)
        S.cam.data.dof.focus_distance = max(2.0, (S.cam.location - sm[f]["head"]).length)
        for o, p in ((S.cam, "location"), (S.tgt, "location")): o.keyframe_insert(p, frame=f)
        S.cam.data.keyframe_insert("lens", frame=f); S.cam.data.dof.keyframe_insert("focus_distance", frame=f)
    S.cam.data.dof.use_dof = True; S.cam.data.dof.aperture_fstop = 2.8


def new_actor(S, uses, x, y, yaw):
    a = MixamoActor(S, x=x, yaw=yaw, use=uses); klunk(a)
    S.key(a.root, 1, loc=(x, y, 0.0), rot=(0, 0, R(yaw)), interp="LINEAR")
    PREV.pop(id(a), None)
    return a


# ------------------------------------------------------------------ nivel -450
def l1(S):
    """-450: ya saltando bajo el dron (fotograma 1, en el aire) con el mando rebotando; pausa dudando; salta mucho más fuerte y cae de espaldas
    (Falling Back Death); el dron sube y zumba más rápido."""
    N = 150; x0, y0, yaw = -0.1, 0.0, -8.0
    f_tA, f_LA = -4, 17; f_c = 44; f_tB, f_LB = f_c + 11, f_c + 32; f_fall = f_LB + 2
    E = stage(S, N)
    a = new_actor(S, ["Jumping", "Falling Back Death"], x0, y0, yaw)
    seg(S, a, "Jumping", 1, 46, start=30, speed=1.0, blend=0)
    seg(S, a, "Jumping", f_c, f_fall + 2, start=14, speed=1.0, blend=4)
    seg(S, a, "Falling Back Death", f_fall, None, start=0, speed=1.0, blend=5)
    def arc(f):
        for (t0, t1, h) in ((f_tA, f_LA, 0.55), (f_tB, f_LB, 0.95)):
            if t0 < f < t1: u = (f - t0) / float(t1 - t0); return h * 4 * u * (1 - u)
        return 0.0
    for f in range(1, N + 12): S.key(a.root, f, loc=(x0, y0, 0.0), rot=(0, 0, R(yaw)), interp="LINEAR")
    pin_feet(S, a, 1, f_fall - 2, arc)
    pin_feet(S, a, f_fall - 1, N + 11, lambda f: 0.0, allbones=True)
    S.cue("boing", 1, vol=-8); S.cue("hit", f_LA, vol=-6); S.cue("huh", f_c - 4, vol=-8); S.cue("boing", f_tB, vol=-5); S.cue("hit", f_LB, vol=-5)
    S.cue("oof", f_fall + 6, vol=-4); S.cue("hit", f_fall + 14, vol=-2); S.cue("wahwah", f_fall + 34, vol=-8)
    S.f = N; a.verify(S.f)
    faces(a, [(1, "enfado", 0.6), (f_LA + 4, "neutra", 1.0), (f_c - 12, "enfado", 1.0), (f_fall, "sorpresa", 1.0), (f_fall + 30, "enfado", 0.6)], N, first_blink=14, every=40)
    sm = sample(S, a, N + 10)
    audit_floor(S, a, "nivel -450", f_fall, N)
    D_, props, leds = build_drone(S)
    def dpos(f):
        p = HOVER.copy(); p.x += 0.35 * math.sin(0.02 * f)
        if f > f_fall + 14: p.z += 0.75 * sstep((f - f_fall - 14) / 30.0)
        return p
    drone_keys(S, D_, props, leds, N + 10, dpos, spin=lambda f: 1.0 if f < f_fall + 14 else 1.6)
    attach_ctrl(S, a, sm, N + 10, build_ctrl(S), impulses=[(1, Vector((0, 0, -0.03)))])
    cam_follow(S, sm, N + 10, zw=0.0)
    return a


# ------------------------------------------------------------------ nivel -80
def l2(S):
    """-80: lanza un zapato (Throw) al dron; el dron esquiva girando y sube; el zapato falla, rebota en el depósito de agua (clunk hueco) y le da
    en la cabeza; se enfada (Angry)."""
    N = 140; x0, y0, yaw = -0.2, 0.0, 28.0
    E = stage(S, N, gust=None)
    a = new_actor(S, ["Throw", "Angry"], x0, y0, yaw)
    seg(S, a, "Throw", 1, 60, start=0, speed=0.85, blend=0, repeat=1)
    for f in range(1, N + 12): S.key(a.root, f, loc=(x0, y0, 0.0), rot=(0, 0, R(yaw)), interp="LINEAR")
    pin_feet(S, a, 1, 60, lambda f: 0.0)
    sm0 = sample(S, a, 60)
    best, f_rel = 0.0, 24                                              # suelta el zapato cuando la mano va más rápida
    for f in range(8, 56):
        v = (sm0[f + 1]["rh"] - sm0[f - 1]["rh"]).length
        if v > best: best, f_rel = v, f
    print(f"L2 suelta el zapato en f{f_rel} (velocidad de mano {best:.3f} m/f)")
    f_wall = f_rel + 11; f_head = f_wall + 12; f_ang = f_head + 2
    # el Throw ya empezó en f1 (hay que verlo dudar antes: se arranca más tarde si hace falta)
    seg(S, a, "Angry", f_ang, None, start=0, speed=1.0, blend=6)
    pin_feet(S, a, 1, N + 11, lambda f: 0.0)
    sm = sample(S, a, N + 10)
    tx, ty, TR, z0, z1 = E["tank"]
    T = Vector((E["tank_x_face"] + 0.02, ty - 0.1, 2.15))              # punto de la pared del depósito donde pega el zapato
    shoe = S.empty("zapato", (0, 0, 1.0))
    sole = mmat(S, "zapato_suela", (0.95, 0.95, 0.92), 0.6); upp = mmat(S, "zapato_rojo", (0.85, 0.12, 0.08), 0.5); lac = mmat(S, "zapato_cordon", (1.0, 1.0, 0.95), 0.6)
    O(S, "cube", "z_suela", sole, (0, 0, -0.035), (0.15, 0.06, 0.02), parent=shoe); O(S, "cube", "z_cuerpo", upp, (-0.02, 0, 0.0), (0.12, 0.052, 0.035), parent=shoe)
    O(S, "uv_sphere", "z_punta", upp, (0.10, 0, -0.005), (0.07, 0.052, 0.045), parent=shoe, segments=12, ring_count=8)
    O(S, "cube", "z_lengua", lac, (0.01, 0, 0.038), (0.05, 0.03, 0.006), parent=shoe)
    O(S, "cube", "z_caña", upp, (-0.12, 0, 0.035), (0.04, 0.05, 0.05), parent=shoe)
    p_rel = sm[f_rel]["rh"] + Vector((0, 0, 0.03)); p_head = sm[f_head]["head"] + Vector((0, 0, 0.12))
    def bez(p0, p1, t, h):
        return p0.lerp(p1, t) + Vector((0, 0, h * 4 * t * (1 - t)))
    spin_a = 0.0
    for f in range(1, N + 11):
        if f < f_rel: p = sm[f]["rh"] + Vector((0.0, 0.0, 0.03)); rot = (0, 0, R(60))
        elif f < f_wall: t = (f - f_rel) / float(f_wall - f_rel); p = bez(p_rel, T, t, 0.25); rot = (R(500 * t), 0, R(60))
        elif f < f_head: t = (f - f_wall) / float(f_head - f_wall); p = bez(T, p_head, t, 0.45); rot = (R(500 + 700 * t), 0, R(60))
        else:
            t = min(1.0, (f - f_head) / 9.0); gnd = Vector((p_head.x + 0.35, p_head.y - 0.35, 0.05)); p = bez(p_head, gnd, t, 0.35); rot = (R(1200 + 200 * t), 0, R(60 + 40 * t))
        S.key(shoe, f, loc=tuple(p), rot=rot, interp="LINEAR")
    S.cue("huh", f_rel - 8, vol=-8); S.cue("whoosh", f_rel, vol=-5); S.cue("clunk", f_wall, vol=-1); S.cue("hit", f_wall, vol=-5); S.cue("whoosh", f_wall + 2, vol=-9)
    S.cue("hit", f_head, vol=-3); S.cue("oof", f_head + 1, vol=-4); S.cue("hmm", f_head + 20, vol=-7); S.cue("wahwah", f_head + 34, vol=-8)
    S.f = N; a.verify(S.f)
    faces(a, [(1, "neutra", 1.0), (f_rel - 10, "enfado", 0.5), (f_rel + 2, "sorpresa", 0.7), (f_head, "sorpresa", 1.0), (f_head + 12, "enfado", 1.0)], N, first_blink=12, every=36)
    D_, props, leds = build_drone(S)
    d0 = HOVER + Vector((0.55, 0.0, 0.0))
    def dpos(f):
        p = d0.copy()
        t = (f - (f_rel + 2)) / 14.0                                    # esquiva: un giro lateral y sube
        if t > 0: p += Vector((-0.5 * math.sin(math.pi * min(1.0, t)) * 1.0, 0, 0.55 * sstep(t)))
        return p
    def dtilt(f):
        t = (f - (f_rel + 2)) / 14.0
        return (0.0, 0.0 + 70.0 * math.sin(math.pi * max(0.0, min(1.0, t))))
    def dyaw(f):
        t = (f - (f_rel + 2)) / 14.0
        return 0.0 + 360.0 * sstep(t) if t > 0 else 0.0
    drone_keys(S, D_, props, leds, N + 10, dpos, tilt=dtilt, yaw=dyaw, spin=lambda f: 1.0 if f < f_rel else 1.4)
    attach_ctrl(S, a, sm, N + 10, build_ctrl(S), impulses=[(f_head + 1, Vector((0, 0.0, 0.05)))], v0=Vector((0, 0, -0.02)))
    cam_follow(S, sm, N + 10, xoff=[(1, 1.1)], tz=[(1, TGT_Z)], zw=0.0)
    return a


# ------------------------------------------------------------------ nivel 120
def l3(S):
    """120: trepa por la escalera del depósito (Climbing Up Wall); el mando golpea un peldaño (clunk, la palanca salta): el dron pica, casi lo roza y
    vuelve a subir; se queda agarrado temblando."""
    N = 135; yaw = 62.0
    E = stage(S, N)
    xf = E["tank_x_face"]; ty = E["tank"][1]
    x0, y0 = xf - 0.28, ty
    f_h = 72                                                            # el mando golpea un peldaño (el clip sube la cadera 1,2 m por sí solo)
    a = new_actor(S, ["Climbing Up Wall"], x0, y0, yaw)
    seg(S, a, "Climbing Up Wall", 1, f_h + 6, start=0, speed=0.5, blend=0, repeat=1)
    seg(S, a, "Climbing Up Wall", f_h + 4, None, start=36, speed=0.04, blend=6)
    for f in range(1, N + 12):
        tt = f - f_h
        sh = 0.0 if tt < 0 else math.sin(tt * 2.3) * 0.012 * (1 - 0.4 * min(1.0, tt / 50.0))
        key_M(S, a, f, Tm((x0 + sh, y0, 0.0)) @ Rz(yaw + (0 if tt < 0 else 3.0 * math.sin(tt * 1.9))))
    sm = sample(S, a, N + 10)
    S.cue("huh", 4, vol=-10); S.cue("clunk", f_h, vol=-1); S.cue("hit", f_h, vol=-6); S.cue("huh", f_h + 4, vol=-5); S.cue("whoosh", f_h + 4, vol=-5); S.cue("whoosh", f_h + 18, vol=-6)
    S.cue("creak", f_h + 28, vol=-9); S.cue("hmm", f_h + 44, vol=-7); S.cue("wahwah", f_h + 56, vol=-9)
    S.f = N; a.verify(S.f)
    faces(a, [(1, "neutra", 1.0), (20, "enfado", 0.6), (f_h - 4, "enfado", 1.0), (f_h + 2, "sorpresa", 1.0)], N, first_blink=12, every=30)
    D_, props, leds = build_drone(S)
    d0 = Vector((xf - 1.0, y0 - 0.3, 3.7))
    def dpos(f):
        p = d0.copy(); p.x += 0.25 * math.sin(0.03 * f)
        t = (f - (f_h + 2)) / 20.0                                      # pica hasta casi rozarle la cabeza (apenas a un lado) y sube
        if t > 0 and t < 2.4:
            h = sm[f_h + 14]["head"]
            dive = math.sin(math.pi * min(1.0, t / 1.2)) if t < 1.2 else 0.0
            tgt = Vector((h.x - 0.2, h.y - 0.45, h.z + 0.30))
            p = p.lerp(tgt, dive if t < 1.2 else 0.0)
            if t >= 1.2: p.z += 0.35 * sstep((t - 1.2) / 1.2)
        elif t >= 2.4: p.z += 0.35
        return p
    def dtilt(f):
        t = (f - (f_h + 2)) / 20.0
        return (35.0 * math.sin(math.pi * max(0.0, min(1.0, t / 1.2))) if t > 0 else 0.0, 0.0)
    drone_keys(S, D_, props, leds, N + 10, dpos, tilt=dtilt, spin=lambda f: 1.0 if f < f_h else 1.7)
    # el mando choca con el peldaño: empujón contra el pecho y palanca hacia arriba
    def lever(f):
        t = f - f_h
        return (0.0, 0.0) if t < 0 else (40.0 * math.sin(math.pi * min(1.0, t / 9.0)), 30.0 * math.sin(math.pi * min(1.0, t / 9.0)))
    B = basis(sm[f_h])
    attach_ctrl(S, a, sm, N + 10, build_ctrl(S), lever=lever, impulses=[(f_h, B.col[1] * -0.07 + B.col[2] * 0.05)])
    cam_follow(S, sm, N + 10, xoff=[(1, 0.3)], py=[(1, -6.2)], tz=[(1, 1.75)], pz=[(1, 2.9)], zw=0.65)
    return a


# ------------------------------------------------------------------ nivel 900
def l4(S):
    """900: salta (Jumping), agarra el patín del dron (Climbing A Rope) y el dron lo arrastra por la azotea hacia las sábanas, que se agitan;
    lo suelta y se ríe (Laughing)."""
    N = 150; x0, y0 = 0.55, 0.1
    f_c = 1; f_t = f_c + 11; f_g = f_t + 10; f_b = f_g + 6; f_dr = f_g + 14; f_r = 100; x_end, y_end = -1.75, 1.7
    gust = lambda f: sstep((f - f_dr) / 8.0) * (1 - sstep((f - f_r - 4) / 10.0))
    E = stage(S, N, gust=gust)
    a = new_actor(S, ["Jumping", "Climbing A Rope", "Laughing"], x0, y0, -10.0)
    seg(S, a, "Jumping", f_c, f_b + 4, start=14, speed=1.0, blend=0)
    seg(S, a, "Climbing A Rope", f_g - 2, f_r + 2, start=0, speed=0.12, blend=5)
    seg(S, a, "Laughing", f_r, None, start=30, speed=1.0, blend=6)
    for f in range(1, N + 12): S.key(a.root, f, loc=(x0, y0, 0.0), rot=(0, 0, R(-10)), interp="LINEAR")
    hl = hand_local(S, a, f_g + 18)                                     # agarre (media de las palmas) en el marco de la raíz
    def Gp(f):
        """Punto de agarre en el mundo (centro del patín)."""
        k = sstep((f - f_dr) / float(f_r - f_dr)); k = min(1.0, max(0.0, k))
        x = lerp(x0, x_end, k) + (0.0); y = lerp(y0, y_end, k)
        zlow = hl.z + 0.045
        z = HOVER.z - 0.14 if f <= f_g - 3 else lerp(HOVER.z - 0.14, zlow, sstep((f - (f_g - 3)) / float(f_dr - f_g + 3)))
        if f > f_dr: z += 0.025 * math.sin(0.9 * (f - f_dr)) * (1 - sstep((f - f_r + 8) / 8.0))
        return Vector((x, y, z))
    def hang_M(f):
        env = sstep((f - f_dr) / 12.0) * (1 - sstep((f - f_r + 10) / 10.0))
        th = -12.0 * env * (0.6 + 0.4 * math.sin(0.35 * (f - f_dr)))
        yaw = -10.0 + 12.0 * math.sin(0.22 * (f - f_dr)) * env
        return Tm(Gp(f)) @ Ry(th) @ Rz(yaw) @ Tm(-hl)
    def arc_h(f): return 0.62 * math.sin(0.5 * math.pi * max(0.0, min(1.0, (f + 6) / float(f_g + 6))))        # ya en el aire en el fotograma 1
    for f in range(1, f_g - 2): key_M(S, a, f, Tm((x0, y0, arc_h(f))) @ Rz(-10.0))
    pin_feet(S, a, 1, f_g - 3, arc_h)
    A_ = Tm(a.root.location.copy()) @ Rz(-10.0)
    for f in range(f_g - 2, N + 12):
        if f <= f_b:
            t = sstep((f - (f_g - 3)) / float(f_b - f_g + 3)); B_ = hang_M(f)
            q = A_.to_quaternion().slerp(B_.to_quaternion(), t)
            key_M(S, a, f, Tm(A_.to_translation().lerp(B_.to_translation(), t)) @ q.to_matrix().to_4x4())
        elif f <= f_r: key_M(S, a, f, hang_M(f))
        else:
            Mh = hang_M(f_r); pos = Mh.to_translation(); pos.z = 0.0
            key_M(S, a, f, Tm(pos) @ Rz(D(Mh.to_euler("XYZ").z)))
    pin_feet(S, a, f_dr, N + 11, lambda f: 0.0)                         # arrastra los pies por el suelo (el clip sube la cadera) y luego de pie
    sm = sample(S, a, N + 10)
    S.cue("huh", f_t - 4, vol=-8); S.cue("boing", f_t, vol=-8); S.cue("pop", f_g, vol=-6); S.cue("whoosh", f_g + 2, vol=-6); S.cue("slide_down", f_dr, vol=-9)
    for f in (f_dr + 10, f_dr + 24, f_dr + 38): S.cue("creak", f, vol=-12)
    S.cue("whoosh", f_dr + 30, vol=-5); S.cue("whoosh", f_dr + 44, vol=-5)
    S.cue("pop", f_r, vol=-6); S.cue("laugh", f_r + 8, vol=-6); S.cue("whoosh", f_r + 3, vol=-3)
    S.f = N; a.verify(S.f)
    faces(a, [(1, "enfado", 0.6), (f_t, "feliz", 0.8), (f_g, "sorpresa", 0.7), (f_dr + 8, "sorpresa", 1.0), (f_r - 6, "neutra", 0.6), (f_r + 4, "feliz", 1.0)], N, first_blink=14, every=40)
    D_, props, leds = build_drone(S)
    def dpos(f):
        g = Gp(f); p = g + Vector((-0.12, 0, 0.14))
        if f > f_r: p.z += 0.9 * sstep((f - f_r) / 22.0) + 0.0; p.x += -0.5 * sstep((f - f_r) / 22.0)
        return p
    def dtilt(f):
        env = sstep((f - f_dr) / 12.0) * (1 - sstep((f - f_r + 10) / 10.0))
        return (6.0 * math.sin(0.3 * f) * env, -14.0 * env - (20.0 * sstep((f - f_r) / 12.0) if f > f_r else 0.0))
    drone_keys(S, D_, props, leds, N + 10, dpos, tilt=dtilt, spin=lambda f: 1.0 if f < f_g else 1.8)
    attach_ctrl(S, a, sm, N + 10, build_ctrl(S), impulses=[(f_t, Vector((0, 0, -0.02))), (f_g + 1, Vector((0, 0, 0.05)))])
    cam_follow(S, sm, N + 10, zw=0.5, pz=[(1, CAM_Z)], tz=[(1, TGT_Z)], xw=1.0)
    return a


# ------------------------------------------------------------------ nivel 5469
def l5(S):
    """5469: se queda quieto mirando alrededor (Looking Around), baja la vista (Thinking), descubre el mando en el pecho y lo levanta (Button Pushing);
    empuja la palanca con un dedo: el dron baja suave y aterriza en sus manos mientras levanta los brazos (Victory), en primer plano. Al final el
    dron vuelve a subir (bucle)."""
    N = 190; x0, y0 = 0.0, 0.0
    f_th = 42; f_bp = 78
    E = stage(S, N)
    a = new_actor(S, ["Looking Around", "Thinking", "Button Pushing", "Victory"], x0, y0, 0.0)
    seg(S, a, "Looking Around", 1, f_th + 4, start=30, speed=1.0, blend=0)
    seg(S, a, "Thinking", f_th, f_bp + 4, start=10, speed=1.0, blend=6)
    seg(S, a, "Button Pushing", f_bp, f_bp + 40, start=0, speed=0.9, blend=6)
    for f in range(1, N + 12): S.key(a.root, f, loc=(x0, y0, 0.0), rot=(0, 0, 0), interp="LINEAR")
    pin_feet(S, a, 1, f_bp + 40, lambda f: 0.0)
    sm0 = sample(S, a, f_bp + 40)
    best, f_press = -9.0, f_bp + 14                                     # el momento de más alcance de la mano derecha hacia delante
    for f in range(f_bp + 6, f_bp + 36):
        Bf = basis(sm0[f]); reach = (sm0[f]["rh"] - sm0[f]["neck"]).dot(Bf.col[1])
        if reach > best: best, f_press = reach, f
    print(f"L5 pulsa en f{f_press} (alcance de la mano {best:.2f} m)")
    f_v = f_press + 6; f_land = f_press + 34; f_up = N - 24
    seg(S, a, "Victory", f_v, None, start=0, speed=1.0, blend=8)
    for f in range(f_bp + 41, N + 12): S.key(a.root, f, loc=(x0, y0, 0.0), rot=(0, 0, 0), interp="LINEAR")
    pin_feet(S, a, 1, N + 11, lambda f: 0.0)
    sm = sample(S, a, N + 10)
    Bp = basis(sm[f_press]); tip = lever_tip(1)
    # mando levantado: posición tal que la punta de la palanca derecha toca la mano en f_press (marco del torso en ese instante)
    Rh = Bp.to_4x4() @ Rx(-12.0)
    held = Tm(sm[f_press]["rh"] - (Rh.to_3x3() @ (tip + Vector((0, 0.02, 0.0))))) @ Rh
    f_l0, f_l1, f_dn = f_th + 26, f_press - 4, f_press + 8
    def over(f, Mc):
        if f < f_l0 or f > f_dn + 10: return None
        if f <= f_l1: t = sstep((f - f_l0) / float(f_l1 - f_l0)); return blend_M(Mc, held, t)
        if f <= f_dn: return held
        return blend_M(held, Mc, sstep((f - f_dn) / 10.0))
    def lever(f):
        t = f - f_press
        if t < 0: return (0.0, 0.0)
        return (0.0, 38.0 * math.sin(math.pi * min(1.0, t / 10.0)) if t < 12 else 0.0)
    S.cue("hmm", f_th + 6, vol=-7); S.cue("huh", f_th + 22, vol=-6); S.cue("clunk", f_press, vol=-3); S.cue("riser", f_press - 2, vol=-6)
    S.cue("bell", f_land, vol=-4); S.cue("tada", f_land + 1, vol=-3); S.cue("yay", f_land + 4, vol=-4); S.cue("whoosh", f_up, vol=-9)
    S.f = N; a.verify(S.f)
    faces(a, [(1, "neutra", 1.0), (24, "sorpresa", 0.4), (f_th + 8, "neutra", 1.0), (f_th + 24, "sorpresa", 1.0), (f_press - 6, "neutra", 0.7), (f_press + 10, "feliz", 1.0)], N,
          first_blink=18, every=48)
    D_, props, leds = build_drone(S)
    hov = HOVER.copy(); hov.x = 0.1
    def hands(f): return (sm[f]["rh"] + sm[f]["lh"]) * 0.5 + Vector((0, 0, 0.17))
    def dpos(f):
        p = hov.copy(); p.x += 0.3 * math.sin(0.025 * f)
        if f_press <= f < f_up:
            t = sstep((f - f_press) / float(f_land - f_press)); p = p.lerp(hands(f), min(1.0, t))
        elif f >= f_up:
            tt = sstep((f - f_up) / 22.0); p = hands(f_up).lerp(hov, tt)
        return p
    def spin(f):
        if f_land <= f < f_up: return 0.25
        return 1.0 if f < f_press else 1.0 - 0.3 * min(1.0, (f - f_press) / 20.0)
    drone_keys(S, D_, props, leds, N + 10, dpos, spin=spin)
    attach_ctrl(S, a, sm, N + 10, build_ctrl(S), over=over, lever=lever)
    # plano medio y empuje a primer plano: la cara del remate al ~60 % del alto
    f_z0, f_z1, f_z2 = f_th + 28, f_press - 2, f_land - 2
    cam_follow(S, sm, N + 10, py=[(1, CAM_Y), (f_z0, CAM_Y), (f_z1, -5.3), (f_z2, -4.9)], pz=[(1, CAM_Z), (f_z0, CAM_Z), (f_z1, 2.2), (f_z2, 1.9)],
               lens=[(1, 50.0), (f_z0, 50.0), (f_z1, 55.0), (f_z2, 55.0)], tz=[(1, TGT_Z), (f_z0, TGT_Z), (f_z1, 1.5), (f_z2, 1.35)], xw=0.0)
    return a


def blend_M(M0, M1, t):
    q = M0.to_quaternion().slerp(M1.to_quaternion(), t)
    return Tm(M0.to_translation().lerp(M1.to_translation(), t)) @ q.to_matrix().to_4x4()


LEVELS = [(-450, l1), (-80, l2), (120, l3), (900, l4), (5469, l5)]
