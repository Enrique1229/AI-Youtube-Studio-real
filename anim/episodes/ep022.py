"""ep021 — Every IQ Level Carries the Cake Through the Door (story-024, idea b20261124-2-i08). Reutiliza de ep020 (se importa, NO se modifica): fachada de
geometria, portal, hall, suelo de adoquin, hombre fijo (rayas naranjas/vaqueros/zapatillas rojas) y utilidades. Cambia: UNA hoja azul con BISAGRA a la derecha
que abre hacia DENTRO y se cierra de golpe por la corriente; tarta de nata grande (primitivas); mesa con mantel y vasos, silla, farolillos que el viento
inclina hacia la puerta (se ve desde el f1); ventana grande de planta baja a la derecha (x 2,65..3,95), FUERA de plano hasta el nivel 5.

  -400 F1 el hombre llega con la tarta; portazo (f7-8) y la tarta se estampa contra la hoja: nata en la cara y en la puerta; se vuelve a camara.
  -65  Dentro del hall sujeta la hoja con la cadera; cada racha la empuja (moreton de nata en la cadera) y la tarta se inclina; mira a camara.
  135  Sujeta la hoja con el pie (Kicking), pasa; la hoja le pilla el talon: ay; la tarta se tambalea.
  1300 Deja la tarta en el suelo, corre a la silla, arrastra el mantel con ella (vasos por el suelo), la calza en la puerta, recoge la tarta y pasa.
  9001 Portazo; duda (Looking Around); la camara GIRA a la derecha: ventana enorme con cortinas ondeando; deja la tarta en la mesa, corre y cierra la
       ventana de un golpe; CORTE a la puerta: sin viento, entra con la tarta intacta (ding).
UN SOLO actor visible por nivel; la camara nunca atraviesa al personaje; ninguna cara en primer plano. Convenio: mira hacia (sin yaw, -cos yaw). 24 fps."""
import math, os, random, importlib.util
import bpy
from mathutils import Vector, Matrix
import env_real

_spec = importlib.util.spec_from_file_location("ep020_base", os.path.join(os.path.dirname(os.path.abspath(__file__)), "ep020.py"))
E0 = importlib.util.module_from_spec(_spec); _spec.loader.exec_module(E0)
mmat, O, box, seg, faces, pin_feet, bone_w, hand_offset = E0.mmat, E0.O, E0.box, E0.seg, E0.faces, E0.pin_feet, E0.bone_w, E0.hand_offset
R, sstep, lerp, seg01, key_path = E0.R, E0.sstep, E0.lerp, E0.seg01, E0.key_path
WY, LW = E0.WY, E0.LW

TITLE = "Every IQ Level Carries the Cake Through the Door"
ONSCREEN = "Every IQ level carries the cake"
SPEED = 1.0
ENV = "mesa"
CUSTOM_CAMERA = True
LABEL_STYLE = "big"

N = 72
PSI = 186.0                                   # mira a la puerta (+y), un pelo a la izquierda
CAM = (0.30, -2.6, 3.3); TGT = (0.30, 1.2, 0.8); LENS = 38.0
CK = 0.78                                     # escala base de la tarta (bandeja radio 0,575)
RF = 0.5 * CK
FWD = RF + 0.03                               # centro de la tarta delante del punto medio de las manos (la bandeja queda delante del cuerpo, sin atravesarlo)
TAB = Vector((0.98, 1.12)); CHAIR0 = Vector((0.58, 0.80))
WX0, WX1, WZ0, WZ1 = 2.65, 3.95, 0.85, 2.15   # ventana grande
A_OPEN = 84.0


def floor_z(y): return 0.05 * sstep((y - 1.38) / 0.30) + 0.05 * sstep((y - 1.68) / 0.30)


def path(pts, f):
    for (fa, *va), (fb, *vb) in zip(pts, pts[1:]):
        if fa <= f <= fb:
            t = sstep((f - fa) / float(max(1, fb - fa))); return [lerp(x, y, t) for x, y in zip(va, vb)]
    return list(pts[-1][1:]) if f > pts[-1][0] else list(pts[0][1:])


# ------------------------------------------------------------------ puerta (una hoja, bisagra a la derecha, abre hacia dentro)
def build_door(S):
    blue = mmat(S, "puerta_azul", (0.03, 0.16, 0.72), 0.42); blue2 = mmat(S, "puerta_panel", (0.05, 0.24, 0.85), 0.40)
    brass = mmat(S, "laton", (0.95, 0.68, 0.22), 0.22, 1.0, ((1.0, 0.7, 0.2), 0.5))
    h = S.empty("hoja", (LW, WY - 0.03, 0.05))
    box(S, "hoja_losa", blue, 0, -2 * LW, -0.03, 0.03, 0.0, 2.05, h)
    for (a0, a1) in ((0.12, 0.70), (0.86, 1.44)):
        for (z0, z1) in ((0.14, 0.95), (1.07, 1.97)): box(S, "panel", blue2, -a0, -a1, -0.045, -0.03, z0, z1, h)
    box(S, "zocalo_laton", brass, -0.02, -2 * LW + 0.02, -0.05, -0.03, 0.02, 0.12, h)
    for zz in (0.30, 1.00, 1.75): O(S, "cylinder", "bisagra", brass, (0, -0.035, zz), (0.026, 0.026, 0.06), parent=h)
    box(S, "placa", brass, -1.30, -1.46, -0.055, -0.03, 0.80, 1.20, h)                      # manilla grande
    box(S, "manilla", brass, -1.34, -1.00, -0.095, -0.075, 0.99, 1.04, h); O(S, "uv_sphere", "pomo", brass, (-1.36, -0.085, 1.015), (0.04,) * 3, parent=h)
    O(S, "cylinder", "manilla_pie", brass, (-1.36, -0.065, 1.015), (0.02, 0.02, 0.02), (R(90), 0, 0), h)
    return h


def leaf_key(S, h, f, ang): S.key(h, f, rot=(0, 0, R(-ang)), interp="LINEAR")


def slam(f, f0, f1, a_open=A_OPEN, rest=0.0):
    """Abierta -> cierra de golpe entre f0 y f1 (acelera) y rebota amortiguada."""
    if f < f0: return a_open + 1.2 * math.sin(f * 2.3)
    if f <= f1: u = (f - f0) / float(f1 - f0); return lerp(a_open, rest, u * u)
    t = f - f1; return rest + 7.0 * math.exp(-0.33 * t) * abs(math.cos(0.85 * t))


# ------------------------------------------------------------------ tarta
def build_cake(S):
    white = mmat(S, "nata", (0.97, 0.96, 0.92), 0.35); steel = mmat(S, "bandeja", (0.72, 0.74, 0.78), 0.25, 0.9)
    red = mmat(S, "fresa", (0.85, 0.03, 0.06), 0.25, 0.0, ((0.9, 0.05, 0.05), 0.25)); grn = mmat(S, "fresa_hoja", (0.10, 0.45, 0.10), 0.6)
    g = S.empty("tarta", (0, 0, 0)); g.scale = (CK,) * 3
    O(S, "cylinder", "bandeja", steel, (0, 0, 0.015), (0.50, 0.50, 0.015), parent=g, vertices=40)
    O(S, "cylinder", "piso1", white, (0, 0, 0.115), (0.42, 0.42, 0.085), parent=g, vertices=40)
    O(S, "cylinder", "piso2", white, (0, 0, 0.27), (0.31, 0.31, 0.07), parent=g, vertices=40)
    for i in range(14):
        a = i * 2 * math.pi / 14; O(S, "uv_sphere", "rosa1", white, (0.41 * math.cos(a), 0.41 * math.sin(a), 0.21), (0.05, 0.05, 0.045), parent=g, segments=10, ring_count=6)
    for i in range(10):
        a = i * 2 * math.pi / 10; O(S, "uv_sphere", "rosa2", white, (0.30 * math.cos(a), 0.30 * math.sin(a), 0.345), (0.045, 0.045, 0.04), parent=g, segments=10, ring_count=6)
    def straw(x, y, z, s=1.0):
        O(S, "uv_sphere", "fresa", red, (x, y, z), (0.062 * s, 0.062 * s, 0.075 * s), parent=g, segments=12, ring_count=8)
        O(S, "uv_sphere", "fresa_h", grn, (x, y, z + 0.07 * s), (0.04 * s, 0.04 * s, 0.014 * s), parent=g, segments=8, ring_count=4)
    for i in range(8): a = i * 2 * math.pi / 8 + 0.2; straw(0.21 * math.cos(a), 0.21 * math.sin(a), 0.43)
    for i in range(7): a = i * 2 * math.pi / 7 + 0.45; straw(0.36 * math.cos(a), 0.36 * math.sin(a), 0.275, 0.8)
    straw(0.0, 0.0, 0.45, 1.25)
    return g


def cake_key(S, g, f, loc, yaw, sc=(1, 1, 1), tilt=(0, 0)):
    S.key(g, f, loc=tuple(loc), rot=(R(tilt[0]), R(tilt[1]), yaw), scale=(CK * sc[0], CK * sc[1], CK * sc[2]), interp="LINEAR")


def hands_mid(S, a, f):
    S.sc.frame_set(f); bpy.context.view_layer.update()
    mid = (bone_w(a, "LeftHand", 0.6) + bone_w(a, "RightHand", 0.6)) * 0.5
    return mid, a.root.matrix_world.to_euler().z


def track(S, a, obj, spec, f0, f1, fwd=FWD, dz=-0.08, setter=None):
    """spec(f) -> dict. modo 'hand' (sigue las manos; 'from'/'u' funden desde una posicion; 'ay','az' fijan y/z del centro) o 'pos'."""
    setter = setter or cake_key
    for f in range(f0, f1 + 1):
        d = spec(f)
        if d.get("mode", "hand") == "hand":
            mid, yaw = hands_mid(S, a, f); fw = Vector((math.sin(yaw), -math.cos(yaw), 0))
            loc = mid + fw * d.get("fwd", fwd) + Vector((0, 0, d.get("dz", dz)))
            if "from" in d: loc = Vector(d["from"]).lerp(loc, d["u"])
            if "ay" in d: loc.y = d["ay"]
            if "az" in d: loc.z = d["az"]
            if "dx" in d: loc.x += d["dx"]
            if "minf" in d:                                   # la tarta nunca queda a menos de `minf` m de la raiz (las manos suben/bajan y el cuerpo se inclina)
                rp = a.root.matrix_world.translation; gap = d["minf"] - (loc - rp).dot(fw)
                if gap > 0: loc = loc + fw * gap
            setter(S, obj, f, loc, yaw, d.get("sc", (1, 1, 1)), d.get("tilt", (0, 0)))
        else:
            setter(S, obj, f, d["loc"], d.get("yaw", 0.0), d.get("sc", (1, 1, 1)), d.get("tilt", (0, 0)))
    S.sc.frame_set(1)


# ------------------------------------------------------------------ escenario
def build_party(S):
    """Mesa con mantel y vasos, silla, postes con farolillos, confeti, ventana grande con cortinas. Devuelve los objetos animables."""
    wood = mmat(S, "madera_clara", (0.62, 0.40, 0.20), 0.6); wood_d = mmat(S, "madera_oscura", (0.34, 0.20, 0.10), 0.7)
    cloth_m = mmat(S, "mantel", (0.97, 0.80, 0.12), 0.8); iron = mmat(S, "hierro", (0.03, 0.03, 0.035), 0.5, 0.7)
    out = {}
    # mesa
    tb = S.empty("mesa", (TAB.x, TAB.y, 0)); O(S, "cylinder", "mesa_pata", iron, (0, 0, 0.36), (0.035, 0.035, 0.36), parent=tb)
    O(S, "cylinder", "mesa_base", iron, (0, 0, 0.02), (0.20, 0.20, 0.02), parent=tb); O(S, "cylinder", "mesa_tablero", wood, (0, 0, 0.73), (0.31, 0.31, 0.02), parent=tb, vertices=32)
    cl = S.empty("mantel", (TAB.x, TAB.y, 0))
    O(S, "cylinder", "mantel_top", cloth_m, (0, 0, 0.765), (0.335, 0.335, 0.012), parent=cl, vertices=32)
    O(S, "cone", "mantel_falda", cloth_m, (0, 0, 0.63), (0.40, 0.40, 0.135), parent=cl, vertices=32, radius1=1.0, radius2=0.84, depth=2.0)
    cols = [(0.95, 0.80, 0.10), (0.15, 0.40, 0.90), (0.15, 0.70, 0.25), (0.95, 0.35, 0.65), (0.98, 0.50, 0.10), (0.55, 0.25, 0.85)]
    cups = []
    for i, c in enumerate(cols):
        a = i * 2 * math.pi / 6 + 0.3; r = 0.17 if i < 5 else 0.0
        o = O(S, "cylinder", "vaso", mmat(S, "vaso%d" % i, c, 0.3), (TAB.x + r * math.cos(a), TAB.y + r * math.sin(a), 0.82), (0.038, 0.038, 0.05), vertices=14)
        cups.append((o, (r * math.cos(a), r * math.sin(a))))
    out.update(table=tb, cloth=cl, cups=cups)
    # silla
    ch = S.empty("silla", (CHAIR0.x, CHAIR0.y, 0))
    box(S, "asiento", wood, -0.20, 0.20, -0.20, 0.20, 0.42, 0.46, ch); box(S, "respaldo", wood, -0.20, 0.20, 0.17, 0.21, 0.46, 0.92, ch)
    for sx in (-1, 1):
        for sy in (-1, 1): box(S, "pata", wood_d, sx * 0.17, sx * 0.20, sy * 0.17, sy * 0.20, 0.0, 0.42, ch)
    box(S, "travesano", wood_d, -0.20, 0.20, 0.17, 0.21, 0.62, 0.66, ch)
    out["chair"] = ch
    # postes y farolillos (el viento los inclina hacia la puerta: se ve desde el f1)
    for px in (-1.45, 1.95):
        O(S, "cylinder", "poste", iron, (px, WY - 0.55, 1.25), (0.025, 0.025, 1.25)); O(S, "cylinder", "poste_base", iron, (px, WY - 0.55, 0.03), (0.10, 0.10, 0.03))
    O(S, "cylinder", "cuerda", mmat(S, "cuerda", (0.05, 0.05, 0.05), 0.8), (0.25, WY - 0.55, 2.46), (0.006, 0.006, 1.72), (0, R(90), 0))
    lan = []
    lc = [((1.0, 0.25, 0.10), 1.6), ((1.0, 0.75, 0.10), 1.6), ((0.15, 0.55, 1.0), 1.4), ((0.95, 0.2, 0.55), 1.6), ((0.30, 0.85, 0.30), 1.4), ((1.0, 0.45, 0.10), 1.6)]
    for i, (c, e) in enumerate(lc):
        g = S.empty("farolillo", ([-1.40, -1.12, -0.92, 0.92, 1.20, 1.48][i], WY - 0.55, 2.45))
        O(S, "cylinder", "hilo", iron, (0, 0, -0.10), (0.004, 0.004, 0.10), parent=g)
        O(S, "uv_sphere", "farol", mmat(S, "farol%d" % i, c, 0.5, 0.0, (c, e)), (0, 0, -0.30), (0.13, 0.13, 0.17), parent=g, segments=14, ring_count=8)
        O(S, "cylinder", "farol_tapa", iron, (0, 0, -0.14), (0.04, 0.04, 0.015), parent=g)
        lan.append(g)
    out["lanterns"] = lan
    # confeti en el suelo
    rnd = random.Random(7)
    for i in range(16):
        c = [(0.95, 0.2, 0.3), (0.2, 0.5, 0.95), (0.98, 0.8, 0.1), (0.2, 0.8, 0.4), (0.95, 0.5, 0.1)][i % 5]
        x, y = rnd.uniform(-1.3, 1.5), rnd.uniform(0.45, 1.7)
        o = box(S, "confeti", mmat(S, "confeti%d" % (i % 5), c, 0.5), -0.025, 0.025, -0.012, 0.012, 0.0, 0.004)
        o.location = (x, y, 0.01 + floor_z(y)); o.rotation_euler = (0, 0, rnd.uniform(0, 6.28))
    # ventana grande de planta baja (derecha): marco, hueco calido, hoja con bisagra a la derecha, cortinas
    white = mmat(S, "marco_blanco", (0.90, 0.87, 0.78), 0.6); warm = mmat(S, "interior_luz", (0.55, 0.30, 0.12), 0.9, 0.0, ((1.0, 0.55, 0.2), 0.55))
    glass = mmat(S, "cristal", (0.10, 0.16, 0.22), 0.05, 0.0, ((0.3, 0.45, 0.6), 0.25)); stone = mmat(S, "piedra", (0.62, 0.58, 0.50), 0.85)
    box(S, "v_hueco", warm, WX0, WX1, WY - 0.025, WY - 0.012, WZ0, WZ1)
    box(S, "v_m_i", white, WX0 - 0.10, WX0, WY - 0.09, WY, WZ0 - 0.05, WZ1 + 0.10); box(S, "v_m_d", white, WX1, WX1 + 0.10, WY - 0.09, WY, WZ0 - 0.05, WZ1 + 0.10)
    box(S, "v_m_s", white, WX0 - 0.10, WX1 + 0.10, WY - 0.09, WY, WZ1, WZ1 + 0.10); box(S, "v_m_b", white, WX0 - 0.10, WX1 + 0.10, WY - 0.09, WY, WZ0 - 0.05, WZ0)
    box(S, "v_alfeizar", stone, WX0 - 0.20, WX1 + 0.20, WY - 0.30, WY, WZ0 - 0.12, WZ0 - 0.05)
    sh = S.empty("hoja_ventana", (WX1, WY - 0.06, 0.0))
    W = WX1 - WX0
    box(S, "h_pane", glass, -W + 0.06, -0.06, -0.012, 0.012, WZ0 + 0.04, WZ1 - 0.04, sh)
    box(S, "h_f1", white, -W, 0, -0.03, 0.03, WZ0, WZ0 + 0.07, sh); box(S, "h_f2", white, -W, 0, -0.03, 0.03, WZ1 - 0.07, WZ1, sh)
    box(S, "h_f3", white, -W, -W + 0.07, -0.03, 0.03, WZ0, WZ1, sh); box(S, "h_f4", white, -0.07, 0, -0.03, 0.03, WZ0, WZ1, sh)
    box(S, "h_pil", white, -W / 2 - 0.025, -W / 2 + 0.025, -0.03, 0.03, WZ0, WZ1, sh)
    out["sash"] = sh
    cur = []
    rod = O(S, "cylinder", "barra_cortina", iron, ((WX0 + WX1) / 2, WY - 0.10, WZ1 + 0.02), (0.012, 0.012, W / 2 + 0.1), (0, R(90), 0))
    for i, (x0, c) in enumerate(((WX0 + 0.05, (0.97, 0.88, 0.70)), (WX0 + W / 2 + 0.05, (0.95, 0.55, 0.45)))):
        g = S.empty("cortina", (x0, WY - 0.12, WZ1))
        box(S, "cortina_tela", mmat(S, "cortina%d" % i, c, 0.85), 0.0, W / 2 - 0.10, -0.012, 0.012, -1.20, 0.0, g)
        cur.append(g)
    out["curtains"] = cur
    return out


def build_props(S):
    cache = {}
    def put(name, res, x, y, h, rot, z=0.0):
        if name not in cache: cache[name] = env_real._model(name, res)
        bpy.context.view_layer.update(); return env_real._place_fit(S, cache[name], (x, y, z), h, R(rot))[0]
    put("potted_plant_02", "1k", -1.12, WY - 0.50, 0.85, 20); put("potted_plant_02", "1k", 1.52, WY - 0.50, 0.85, 200)
    put("power_box_01", "1k", -1.05, WY - 0.05, 0.5, 0, z=1.95); put("potted_plant_04", "1k", 0.52, WY - 0.20, 0.20, 0, z=0.10)
    put("street_lamp_01", "2k", -2.4, WY - 0.6, 4.6, 0); put("fire_hydrant", "1k", 3.75, 0.45, 0.8, 25)
    put("metal_trash_can", "2k", -2.1, 1.0, 1.0, 20); put("trashbag", "1k", -1.75, 0.75, 0.5, 60)
    put("painted_wooden_bench", "1k", -3.6, 1.2, 0.9, 0); put("wooden_crate_01", "1k", 4.5, 0.95, 0.5, -15)
    put("plastic_crate_01", "1k", -1.6, 0.35, 0.34, 20); put("planter_box_01", "2k", 5.1, 1.5, 0.75, 0)


def wind_fx(S, P, wind, n):
    """Farolillos inclinados hacia la puerta (+y) y cortinas hinchadas hacia fuera; wind(f) 0..1."""
    for f in range(1, n + 1):
        w = wind(f)
        for i, g in enumerate(P["lanterns"]):
            S.key(g, f, rot=(R(w * 6 * math.sin(f * 0.7 + i)), R(w * (36 + 10 * math.sin(f * 0.9 + i * 1.3))), 0), interp="LINEAR")
        for i, g in enumerate(P["curtains"]):
            S.key(g, f, rot=(R(-w * (38 + 14 * math.sin(f * 0.8 + i * 2.0))), 0, R(w * 6 * math.sin(f * 0.6 + i))), interp="LINEAR")


HD = 4.8                                       # profundidad del hall (en ep020 eran 3,0: la tarta grande chocaba con el fondo)


def deepen_hall(S):
    """El hall de ep020 mide 3 m; con la tarta y el hombre la tarta atravesaba el fondo y el cuadro. Se reconstruye mas profundo (misma estetica)."""
    for nm in ("hall_suelo", "hall_pared_i", "hall_pared_d", "hall_techo", "hall_fondo", "hall_luz", "cuadro_marco", "cuadro", "cuadro_sol", "alfombra"):
        bpy.data.objects.remove(bpy.data.objects[nm], do_unlink=True)
    M = lambda n: S.mats["m_" + n]
    dark = M("interior"); HX = LW
    box(S, "hall_suelo", dark, -HX, HX, WY, WY + HD, 0.0, 0.10); box(S, "hall_pared_i", dark, -HX - 0.05, -HX, WY, WY + HD, 0.0, 2.35)
    box(S, "hall_pared_d", dark, HX, HX + 0.05, WY, WY + HD, 0.0, 2.35); box(S, "hall_techo", dark, -HX, HX, WY, WY + HD, 2.35, 2.40)
    box(S, "hall_fondo", dark, -HX, HX, WY + HD, WY + HD + 0.05, 0.0, 2.35); box(S, "hall_luz", M("interior_luz"), -HX + 0.25, HX - 0.25, WY + HD - 0.02, WY + HD, 0.5, 2.0)
    box(S, "alfombra", M("alfombra"), -0.55, 0.55, WY + 0.4, WY + HD - 0.2, 0.10, 0.115)
    box(S, "cuadro_marco", M("marco_blanco"), -0.30, 0.30, WY + HD - 0.06, WY + HD - 0.02, 1.05, 1.75)
    box(S, "cuadro", M("cuadro_lienzo"), -0.25, 0.25, WY + HD - 0.07, WY + HD - 0.06, 1.10, 1.70)
    box(S, "cuadro_sol", M("cuadro_sol"), -0.10, 0.10, WY + HD - 0.075, WY + HD - 0.07, 1.35, 1.55)


def setup(S):
    E0.stage(S)
    for nm, mt, z0, z1, y0, y1 in (("zocalo", "piedra_osc", 0, 0.55, WY - 0.07, WY + 0.02), ("zocalo_borde", "piedra", 0.50, 0.58, WY - 0.09, WY - 0.02)):
        bpy.data.objects.remove(bpy.data.objects[nm], do_unlink=True)          # el zocalo de ep020 cruzaba el hueco de la puerta: se parte en dos
        box(S, nm, S.mats["m_" + mt], -9, -LW, y0, y1, z0, z1); box(S, nm, S.mats["m_" + mt], LW, 9, y0, y1, z0, z1)
    deepen_hall(S)
    S.cam.location = CAM; S.cam.data.lens = LENS; S.tgt.location = TGT
    bpy.ops.object.light_add(type="POINT", location=(0.0, WY + 1.7, 2.1)); Lg = bpy.context.object; Lg.data.energy = 520; Lg.data.color = (1.0, 0.82, 0.62); Lg.data.shadow_soft_size = 0.7
    build_props(S); P = build_party(S); P["door"] = build_door(S); P["cake"] = build_cake(S)
    return P


def cam_keys(S, shake=None, focus=None, n=N + 10, tx=None, cam=CAM, tgt=TGT, ty=None):
    bpy.context.preferences.edit.keyframe_new_interpolation_type = "LINEAR"
    for f in range(1, n + 1):
        sh = shake(f) if shake else (0.0, 0.0)
        S.cam.location = (cam[0] + sh[0], cam[1], cam[2] + sh[1]); S.cam.keyframe_insert("location", frame=f)
        S.tgt.location = (tx(f) if tx else tgt[0], ty(f) if ty else tgt[1], tgt[2]); S.tgt.keyframe_insert("location", frame=f)
        S.cam.data.lens = LENS; S.cam.data.keyframe_insert("lens", frame=f)
        S.cam.data.dof.focus_distance = focus(f) if focus else 3.0; S.cam.data.dof.keyframe_insert("focus_distance", frame=f)


def new_man(S, uses, x, y, yaw): return E0.new_man(S, uses, x, y, yaw)


def front_dist(hl): return -hl.y + FWD + RF          # distancia de la raiz al frente de la bandeja


def cream_blob(S, name, col=(0.97, 0.96, 0.92), rgb_name="nata"):
    return O(S, "uv_sphere", name, mmat(S, rgb_name, col, 0.35), (0, 0, -5), (0, 0, 0), segments=12, ring_count=8)


def head_pos(S, a, f):
    S.sc.frame_set(f); bpy.context.view_layer.update()
    return bone_w(a, "Head", 0.75), a.root.matrix_world.to_euler().z


def face_mask(S, a, f0, f1, f_on, parts=None):
    """Nata en la cara: mancha sobre la boca/nariz, a los lados y una fresa en el pelo. Escala 0 antes de f_on."""
    white = [cream_blob(S, "nata_cara") for _ in range(4)]; berry = O(S, "uv_sphere", "fresa_pelo", mmat(S, "fresa", (0.85, 0.03, 0.06), 0.25), (0, 0, -5), (0, 0, 0), segments=10, ring_count=6)
    for f in range(f0, f1 + 1):
        hp, yaw = head_pos(S, a, f); fw = Vector((math.sin(yaw), -math.cos(yaw), 0)); rt = Vector((math.cos(yaw), math.sin(yaw), 0))
        k = seg01(f, f_on, f_on + 2)
        pos = [hp + fw * 0.11 + Vector((0, 0, -0.05)), hp + rt * 0.12 + fw * 0.02, hp - rt * 0.12 + fw * 0.02, hp + fw * 0.07 + Vector((0, 0, 0.13))]
        sc = [(0.13, 0.10, 0.09), (0.08, 0.08, 0.08), (0.08, 0.08, 0.08), (0.10, 0.09, 0.05)]
        for o, p, s in zip(white, pos, sc): S.key(o, f, loc=tuple(p), scale=tuple(v * k for v in s), interp="LINEAR")
        S.key(berry, f, loc=tuple(hp + fw * 0.02 + Vector((0.02, 0, 0.19))), scale=(0.05 * k, 0.05 * k, 0.06 * k), interp="LINEAR")


def burst(S, f0, p0, n=14, seed=3, vmin=1.2, vmax=3.2, up=1.6, bias=(0, -1.0), berries=3, life=22):
    rnd = random.Random(seed); white = mmat(S, "nata", (0.97, 0.96, 0.92), 0.35); red = mmat(S, "fresa", (0.85, 0.03, 0.06), 0.25)
    for i in range(n):
        ang = rnd.uniform(0, 2 * math.pi); sp = rnd.uniform(vmin, vmax); r = rnd.uniform(0.045, 0.085) * (1.4 if i < berries else 1.0)
        v = Vector((math.cos(ang) * sp * 0.8 + bias[0] * 1.4, math.sin(ang) * sp * 0.5 + bias[1] * 1.8, rnd.uniform(0.6, up) + 0.6))
        o = O(S, "uv_sphere", "salpica", red if i < berries else white, tuple(p0), (0, 0, 0), segments=10, ring_count=6)
        for k in range(0, life + 1):
            t = k / 24.0; p = Vector(p0) + v * t + Vector((0, 0, -4.9 * t * t)); p.z = max(p.z, 0.04)
            sc = r * (min(1.0, k / 2.0)) * (1.0 - seg01(k, life - 4, life))
            S.key(o, f0 + k, loc=tuple(p), scale=(sc, sc, sc), interp="LINEAR")


def berry_drop(S, a, f_on, f0, f1):
    """Una fresa se suelta de lo alto de la tarta (que se inclina) y cae al suelo delante."""
    red = mmat(S, "fresa", (0.85, 0.03, 0.06), 0.25); bs = O(S, "uv_sphere", "fresa_cae", red, (0, 0, -5), (0, 0, 0), segments=10, ring_count=6)
    for f in range(1, N + 12):
        mid, yaw = hands_mid(S, a, f); fw = Vector((math.sin(yaw), -math.cos(yaw), 0)); u = seg01(f, f0, f1)
        pos = mid + fw * FWD + Vector((0.15, 0, 0.55)); drop = pos + Vector((0.25 * u, -0.30 * u, -0.9 * u * u)); drop.z = max(drop.z, 0.16)
        S.key(bs, f, loc=tuple(drop), scale=(0.075, 0.075, 0.085) if f >= f_on else (0, 0, 0), interp="LINEAR")
    S.sc.frame_set(1)


def finish(S, a, faces_ev, first_blink=12, every=38):
    S.f = N; a.verify(S.f); faces(a, faces_ev, N, first_blink=first_blink, every=every)


# ================================================================== NIVEL -400
def l1(S):
    """-400: llega con la tarta; portazo f7-8; la tarta se estampa contra la hoja (f9): nata en cara y puerta; se vuelve a camara."""
    P = setup(S); door, cake = P["door"], P["cake"]
    f_sl, f_hit, f_rel, f_turn, f_ang = 7, 9, 26, 30, 50
    X0 = 0.02
    a = new_man(S, ["Pushing", "Surprised", "Angry"], X0, 0, PSI)
    seg(S, a, "Pushing", 1, f_hit + 2, start=18, speed=1.3, blend=0)
    seg(S, a, "Surprised", f_hit, f_ang + 2, start=0, speed=1.0, blend=3)
    seg(S, a, "Angry", f_ang, None, start=0, speed=1.0, blend=5)
    key_path(S, a, [(1, X0, 0, PSI)], 1, N + 11)
    hl = hand_offset(S, a, (4, 8)); YC = WY - 0.06 - front_dist(hl)
    pts = [(1, X0, YC - 0.62, PSI), (f_hit, X0, YC, PSI), (f_hit + 3, X0, YC + 0.14, PSI), (f_hit + 9, X0, YC - 0.12, PSI), (f_turn, X0, YC - 0.12, PSI),
           (f_turn + 11, X0 + 0.15, YC - 0.20, 342.0), (N + 11, X0 + 0.15, YC - 0.20, 342.0)]
    key_path(S, a, pts, 1, N + 11); pin_feet(S, a, 1, N + 11, lambda f: floor_z(path(pts, f)[1]))
    for f in range(1, N + 12): leaf_key(S, door, f, slam(f, f_sl - 3, f_sl + 1, A_OPEN, 0.0) if f < f_hit + 14 else 0.0)
    CX, CY = X0 - 1.12, 0.62                                 # la tarta cae a un lado (izquierda), lejos del hombre, sobre el adoquin llano
    XS = 1.35                                                 # ancho de la tarta aplastada contra la hoja (cabe en el hueco: 0,64 < 0,78)
    def spec(f):
        if f < f_hit: return dict(mode="hand")
        u = seg01(f, f_hit, f_hit + 3)
        sy = lerp(1.0, 0.32, u); sc = (lerp(1.0, XS, u), sy, lerp(1.0, 1.1, u))
        ay = WY - 0.13 - RF * sy                              # por delante de la manilla (sobresale hasta WY-0,125)
        if f < f_rel:
            return dict(mode="hand", sc=sc, ay=ay, dz=-0.08 - 0.30 * seg01(f, f_hit + 6, f_rel))
        t = seg01(f, f_rel, f_rel + 8)
        z0 = 0.95 - 0.30 - 0.08 + 0.05
        return dict(mode="pos", loc=(lerp(X0, CX, t), lerp(ay, CY, sstep(t * 1.6)), lerp(z0, 0.01, t * t)), yaw=math.radians(PSI) + R(35) * t,
                    sc=(lerp(XS, 1.25, t), lerp(0.32, 1.25, t), lerp(1.1, 0.30, t * t)))
    track(S, a, cake, spec, 1, N + 11)
    # mancha en la puerta + gotas + fresas pegadas
    white = mmat(S, "nata", (0.97, 0.96, 0.92), 0.35); red = mmat(S, "fresa", (0.85, 0.03, 0.06), 0.25)
    sm = O(S, "cylinder", "mancha", white, (X0, WY - 0.075, 1.02), (0, 0, 0.012), (R(90), 0, 0), vertices=24)
    for f in range(1, N + 12):
        u = seg01(f, f_hit, f_hit + 2); S.key(sm, f, loc=(X0, WY - 0.075, 1.02), scale=(0.46 * u, 0.46 * u * 0.9, 0.012), interp="LINEAR")
    for i, dx in enumerate((-0.30, -0.05, 0.22, 0.36)):
        d = O(S, "cube", "gota", white, (X0 + dx, WY - 0.08, 1.12), (0.025, 0.012, 0.001))
        for f in range(1, N + 12):
            u = seg01(f, f_hit + 6 + 3 * i, f_hit + 34 + 4 * i); L = 0.001 + (0.05 + 0.24 * u) * seg01(f, f_hit + 6 + 3 * i, f_hit + 8 + 3 * i)
            S.key(d, f, loc=(X0 + dx, WY - 0.08, 1.12 - 0.26 * u - L), scale=(0.025, 0.012, L), interp="LINEAR")
    for dx, dz in ((-0.18, 0.18), (0.20, 0.05)):
        b = O(S, "uv_sphere", "fresa_puerta", red, (X0 + dx, WY - 0.09, 1.02 + dz), (0, 0, 0), segments=10, ring_count=6)
        for f in range(1, N + 12): k = seg01(f, f_hit + 1, f_hit + 3); S.key(b, f, loc=(X0 + dx, WY - 0.09, 1.02 + dz - 0.12 * seg01(f, f_hit + 8, f_rel)), scale=(0.07 * k, 0.07 * k, 0.07 * k), interp="LINEAR")
    burst(S, f_hit, (X0, WY - 0.30, 1.05), n=16, seed=3, bias=(0, -1.0))
    face_mask(S, a, 1, N + 11, f_hit + 2)
    wind_fx(S, P, lambda f: 1.0, N + 11)
    S.cue("huh", 3, vol=-8); S.cue("creak", f_sl - 3, vol=-6); S.cue("hit", f_sl + 1, vol=-1); S.cue("clunk", f_sl + 1, vol=-3); S.cue("splash", f_hit + 1, vol=-1)
    S.cue("oof", f_hit + 2, vol=-4); S.cue("slide_down", f_hit + 8, vol=-7); S.cue("splash", f_rel + 5, vol=-4); S.cue("wahwah", f_ang + 2, vol=-8)
    finish(S, a, [(1, "neutra", 1.0), (f_sl - 2, "sorpresa", 0.6), (f_hit, "sorpresa", 1.0), (f_turn + 6, "sorpresa", 0.7), (f_ang, "enfado", 0.9)], first_blink=14)
    def shake(f):
        t = f - f_hit; k = max(0.0, 1 - t / 8.0) if t >= 0 else 0.0
        return (0.05 * math.sin(f * 2.3) * k, 0.05 * math.cos(f * 1.9) * k)
    cam_keys(S, shake)
    return a


# ================================================================== NIVEL -65
def l2(S):
    """-65: dentro del hall sujeta la hoja con la cadera; cada racha la empuja; moreton de nata en la cadera; la tarta se inclina; mira a camara."""
    P = setup(S); door, cake = P["door"], P["cake"]
    f_c, f_cr, f_t, f_ang = 5, 30, 40, 52
    gusts = (13, 24, 36)
    X0 = 0.05; LEAF = 1.57                       # la punta de la hoja (1,56 m) toca la cadera derecha: el hombre esta a esa distancia de la bisagra
    a = new_man(S, ["Pushing", "Angry"], X0, 0, PSI)
    seg(S, a, "Pushing", 1, None, start=10, speed=1.0, blend=0)            # sigue sujetando la tarta con las manos todo el nivel (el enfado va en la cara)
    key_path(S, a, [(1, X0, 0, PSI)], 1, N + 11)
    def xman(f):
        x = X0
        for g in gusts: x -= 0.05 * sstep((f - g) / 3.0)
        return x
    HIPD = 0.30                                    # la cadera derecha sobresale del eje del hombre
    def ym(f):
        dx = LW - (xman(f) + HIPD); yh = WY + math.sqrt(LEAF ** 2 - dx ** 2)
        return yh - 0.04 - 0.55 * (1 - seg01(f, 1, f_c - 1))
    pts = []
    for f in range(1, N + 12):
        yw = PSI + 4.0 * sum(math.exp(-((f - g) / 3.0) ** 2) for g in gusts)
        pts.append((f, xman(f), ym(f), yw))
    key_path(S, a, pts, 1, N + 11); pin_feet(S, a, 1, N + 11, lambda f: 0.10)
    def ang(f):
        if f < f_c - 3: return A_OPEN
        dx = LW - (xman(f) + HIPD); rest = math.degrees(math.atan2(math.sqrt(LEAF ** 2 - dx ** 2), dx)) + 0.5
        if f < f_c: return lerp(A_OPEN, rest, ((f - (f_c - 3)) / 3.0) ** 2)
        return rest
    for f in range(1, N + 12): leaf_key(S, door, f, ang(f))
    def spec(f):
        tilt = (0.0, 0.0)
        side = 12.0 * sstep((f - gusts[0]) / 6.0) + 8.0 * sstep((f - gusts[2]) / 8.0) + 5 * sum(math.exp(-((f - g) / 2.0) ** 2) for g in gusts)
        fwd = 3.0 * sstep((f - gusts[1]) / 8.0)
        return dict(mode="hand", tilt=(-fwd, -side) if False else (0.0, side), dz=-0.08 + 0.02 * math.sin(f * 1.7) * (1 if f > gusts[0] else 0))
    track(S, a, cake, spec, 1, N + 11)
    # nata que resbala de la bandeja y cae en la cadera (lado derecho = +x); mancha que crece
    white = mmat(S, "nata", (0.97, 0.96, 0.92), 0.35)
    dz = cream_blob(S, "dollop"); sp = cream_blob(S, "moreton"); sp2 = cream_blob(S, "moreton2")
    for f in range(1, N + 12):
        hp, yaw = hands_mid(S, a, f); hip = bone_w(a, "Hips", 0.0)
        S.sc.frame_set(f); bpy.context.view_layer.update(); hip = bone_w(a, "Hips", 0.0)
        tdrop = f - (gusts[0] + 6); u = seg01(f, gusts[0] + 6, gusts[0] + 12)
        start = Vector((hip.x + 0.25, hip.y - 0.05, hip.z + 0.55)); end = Vector((hip.x + 0.17, hip.y - 0.10, hip.z - 0.05))
        p = start.lerp(end, u * u); k = 1.0 if 0 <= tdrop < 6 else 0.0
        S.key(dz, f, loc=tuple(p), scale=(0.07 * k,) * 3 if k else (0, 0, 0), interp="LINEAR")
        g = seg01(f, gusts[0] + 12, gusts[0] + 15) + 0.5 * seg01(f, gusts[1] + 2, gusts[1] + 6)
        S.key(sp, f, loc=(hip.x + 0.17, hip.y - 0.11, hip.z - 0.06), scale=(0.10 * g, 0.045 * g, 0.12 * g), interp="LINEAR")
        g2 = seg01(f, gusts[2] + 2, gusts[2] + 6)
        S.key(sp2, f, loc=(hip.x + 0.15, hip.y - 0.10, hip.z - 0.20), scale=(0.07 * g2, 0.04 * g2, 0.09 * g2), interp="LINEAR")
    S.sc.frame_set(1)
    berry_drop(S, a, f_t + 4, f_t + 6, f_t + 17)
    wind_fx(S, P, lambda f: 1.0, N + 11)
    S.cue("huh", 2, vol=-8); S.cue("whoosh", f_c - 3, vol=-5); S.cue("hit", f_c, vol=-2); S.cue("clunk", f_c, vol=-4)
    for g in gusts: S.cue("creak", g - 1, vol=-5); S.cue("clunk", g + 1, vol=-5)
    S.cue("splash", gusts[0] + 12, vol=-4); S.cue("splash", gusts[2] + 3, vol=-6); S.cue("oof", gusts[1] + 1, vol=-5); S.cue("hmm", f_t + 4, vol=-6); S.cue("wahwah", f_ang + 8, vol=-8)
    finish(S, a, [(1, "neutra", 1.0), (f_c, "enfado", 0.6), (gusts[1], "enfado", 1.0), (f_t, "enfado", 1.0), (f_ang + 6, "sorpresa", 0.6)], first_blink=16)
    def shake(f): return tuple(0.02 * sum(math.exp(-((f - g) / 2.0) ** 2) for g in gusts) * v for v in (math.sin(f * 2.2), math.cos(f * 1.8)))
    cam_keys(S, shake, focus=lambda f: 4.6, cam=(0.0, -0.4, 2.0), tgt=(0.0, 3.7, 1.0))
    return a


# ================================================================== NIVEL 135
def l3(S):
    """135: dentro del hall sujeta la hoja con el pie (Kicking) y pasa; la hoja le pilla el talon: ay; la tarta se tambalea; mira a camara."""
    P = setup(S); door, cake = P["door"], P["cake"]
    f_in, f_k, f_pin, f_ay, f_turn = 12, 14, 20, 23, 52
    X0 = -0.05; LEAF = 1.57
    def yh(cx): return WY + math.sqrt(LEAF ** 2 - (LW - cx) ** 2)          # y a la que la PUNTA de la hoja (1,57 m) toca un punto de x=cx
    CXF, CXH = X0 + 0.44, X0 + 0.46                                         # pie derecho que sujeta la hoja / talon que pilla
    Y1, Y2 = yh(CXF), yh(CXH) + 0.12
    a = new_man(S, ["Pushing", "Kicking", "Surprised"], X0, 0, PSI)
    seg(S, a, "Pushing", 1, f_k + 1, start=14, speed=1.3, blend=0)
    seg(S, a, "Kicking", f_k, f_ay + 3, start=8, speed=1.3, blend=3)
    seg(S, a, "Surprised", f_ay + 1, None, start=0, speed=1.0, blend=3)
    key_path(S, a, [(1, X0, 0, PSI)], 1, N + 11)
    pts = [(1, X0, Y1 - 1.0, PSI), (f_in, X0, Y1, PSI), (f_pin, X0, Y1 + 0.01, PSI), (f_pin + 6, X0, Y2, PSI), (f_ay + 8, X0, Y2 + 0.01, PSI + 6),
           (f_turn, X0, Y2 + 0.01, PSI + 6), (N + 11, X0, Y2 + 0.01, PSI + 6)]
    key_path(S, a, pts, 1, N + 11); pin_feet(S, a, 1, N + 11, lambda f: floor_z(path(pts, f)[1]))
    def ang(f):
        a_hold = math.degrees(math.atan2(yh(CXF) - WY, LW - CXF)); a_pin = math.degrees(math.atan2(yh(CXH) - WY, LW - CXH))
        if f < f_k - 5: return A_OPEN + 1.5 * math.sin(f * 2.1)
        if f < f_k: return lerp(A_OPEN, a_hold, ((f - (f_k - 5)) / 5.0) ** 2)                 # la racha la cierra hasta el pie
        if f < f_pin: return a_hold
        if f < f_ay: return lerp(a_hold, a_pin, seg01(f, f_pin, f_ay))                       # el talon queda atras y la hoja avanza
        return a_pin
    for f in range(1, N + 12): leaf_key(S, door, f, ang(f))
    def spec(f):
        wob = 11.0 * math.exp(-0.14 * (f - f_ay)) * math.sin(0.9 * (f - f_ay)) if f >= f_ay else 0.0
        fw = 4.0 * math.exp(-0.12 * (f - f_ay)) * math.cos(0.8 * (f - f_ay)) if f >= f_ay else 0.0
        return dict(mode="hand", tilt=(fw, wob), dz=-0.08, minf=1.12)
    track(S, a, cake, spec, 1, N + 11)
    berry_drop(S, a, f_turn - 2, f_turn, f_turn + 12)
    wind_fx(S, P, lambda f: 1.0, N + 11)
    S.cue("huh", 3, vol=-8); S.cue("whoosh", f_k - 4, vol=-5); S.cue("clunk", f_k, vol=-2); S.cue("creak", f_k + 3, vol=-6); S.cue("hit", f_pin, vol=-3)
    S.cue("oof", f_ay, vol=-1); S.cue("boing", f_ay + 3, vol=-5); S.cue("clunk", f_ay + 8, vol=-5); S.cue("hmm", f_turn + 6, vol=-6); S.cue("wahwah", f_turn + 18, vol=-8)
    finish(S, a, [(1, "neutra", 1.0), (f_k, "enfado", 0.7), (f_pin, "sorpresa", 0.6), (f_ay, "sorpresa", 1.0), (f_turn + 8, "enfado", 0.7)], first_blink=15)
    def shake(f):
        t = f - f_ay; k = max(0.0, 1 - t / 8.0) if t >= 0 else 0.0
        return (0.03 * math.sin(f * 2.2) * k, 0.03 * math.cos(f * 1.7) * k)
    cam_keys(S, shake, focus=lambda f: 4.6, cam=(-0.1, -0.4, 2.0), tgt=(-0.1, 3.7, 1.0))
    return a


# ================================================================== NIVEL 1300
def l4(S):
    """1300: portazo; deja la tarta en el suelo; corre a la silla y tira del mantel con ella (vasos por el suelo); la calza en la puerta; recoge la tarta, pasa."""
    P = setup(S); door, cake, chair, cloth = P["door"], P["cake"], P["chair"], P["cloth"]
    f_sl, f_dn, f_g, f_y0, f_d0, f_wd, f_up, f_in = 4, 8, 15, 16, 20, 28, 35, 42
    X0 = -0.05
    a = new_man(S, ["Pushing", "Surprised", "Picking Up", "Running"], X0, 0, PSI)
    seg(S, a, "Pushing", 1, f_dn + 1, start=18, speed=1.3, blend=0)
    seg(S, a, "Picking Up", f_dn - 1, f_g - 2, start=30, speed=1.7, blend=3)
    seg(S, a, "Running", f_g - 3, f_wd, start=0, speed=1.15, blend=3, repeat=3)
    seg(S, a, "Pushing", f_wd, f_wd + 6, start=18, speed=1.3, blend=3)
    seg(S, a, "Picking Up", f_wd + 6, f_in - 1, start=30, speed=1.9, blend=3)
    seg(S, a, "Pushing", f_in - 2, None, start=18, speed=1.0, blend=4)
    key_path(S, a, [(1, X0, 0, PSI)], 1, N + 11)
    hl = hand_offset(S, a, (4, 8)); YC = WY - 0.06 - front_dist(hl)
    CF = Vector((X0, YC + 0.62))                                      # donde queda la tarta en el suelo
    GRAB = Vector((CHAIR0.x - hl.x, CHAIR0.y - 0.22 + hl.y))          # raiz al agarrar la silla
    WEDGE = Vector((0.50, WY + 0.55)); YDOOR = WY - 0.10
    pts = [(1, X0, YC - 0.15, PSI), (f_sl, X0, YC, PSI), (f_dn + 5, X0, YC, PSI), (f_g - 3, X0 + 0.05, YC, 120.0), (f_g + 1, GRAB.x, GRAB.y, 180.0), (f_d0 - 1, GRAB.x, GRAB.y, 180.0),
           (f_wd - 2, X0 + 0.55, YDOOR - 0.20, PSI), (f_wd + 4, X0 + 0.55, YDOOR, PSI), (f_wd + 6, X0 + 0.55, YDOOR, PSI), (f_up - 2, X0 + 0.15, YC + 0.30, PSI), (f_up + 1, CF.x - hl.x, CF.y + hl.y, PSI),
           (f_in, X0, CF.y - 0.1, PSI), (N + 11, X0, WY + 0.95, PSI)]
    # tramo final: camina hacia dentro (de f_in en adelante)
    pts = pts[:-2] + [(f_in - 1, X0, CF.y - 0.12 + 0.0, PSI), (f_in + 15, X0 - 0.30, WY + 1.0, PSI), (f_in + 18, X0 - 0.30, WY + 1.05, PSI), (f_in + 30, X0 - 0.30, WY + 1.05, PSI), (N + 11, X0 - 0.30, WY + 1.05, PSI)]
    key_path(S, a, pts, 1, N + 11); pin_feet(S, a, 1, N + 11, lambda f: floor_z(path(pts, f)[1]))
    def ang(f):
        if f < f_sl - 3: return A_OPEN + 1.2 * math.sin(f * 2.3)
        if f <= f_sl: return lerp(A_OPEN, 0.0, ((f - (f_sl - 3)) / 3.0) ** 2)
        if f < f_wd + 1: return 7.0 * math.exp(-0.33 * (f - f_sl)) * abs(math.cos(0.85 * (f - f_sl)))
        return lerp(0.0, 70.0, seg01(f, f_wd + 1, f_wd + 6)) if f < f_wd + 8 else 70.0 + 0.8 * math.sin(f * 1.7) * math.exp(-0.2 * (f - f_wd - 8))
    for f in range(1, N + 12): leaf_key(S, door, f, ang(f))
    # tarta: manos -> suelo (f_dn..f_dn+5) ; suelo ; manos (f_up..)
    def spec(f):
        if f < f_dn: return dict(mode="hand")
        if f < f_dn + 5:
            u = seg01(f, f_dn, f_dn + 5); mid, yaw = hands_mid(S, a, f)
            return dict(mode="hand", from_=None) if False else dict(mode="hand", ay=lerp(0, 0, 0) or None) if False else dict(mode="hand", dz=lerp(-0.08, -0.62, u))
        if f < f_up: return dict(mode="pos", loc=(CF.x, CF.y, 0.05), yaw=math.radians(PSI))
        u = seg01(f, f_up, f_up + 4)
        return dict(mode="hand", **{"from": (CF.x, CF.y, 0.05), "u": u})
    track(S, a, cake, spec, 1, N + 11)
    # silla: en su sitio -> manos (f_g..) -> tope en la puerta
    def cset(S_, o, f, loc, yaw, sc=(1, 1, 1), tilt=(0, 0)):
        S_.key(o, f, loc=tuple(loc), rot=(0, 0, yaw), interp="LINEAR")
    def cspec(f):
        if f < f_g + 1: return dict(mode="pos", loc=(CHAIR0.x, CHAIR0.y, 0.0), yaw=R(180))
        if f < f_wd + 2: return dict(mode="hand", dz=-0.62, fwd=0.22, **{"from": (CHAIR0.x, CHAIR0.y, 0.0), "u": seg01(f, f_g + 1, f_g + 3)})
        if f < f_wd + 7:
            mid, yaw = hands_mid(S, a, f); fw = Vector((math.sin(yaw), -math.cos(yaw), 0))
            return dict(mode="hand", dz=-0.62, fwd=0.22, **{"from": (WEDGE.x, WEDGE.y, floor_z(WEDGE.y)), "u": seg01(f, f_wd + 2, f_wd + 6) * 0.0}) if False else dict(mode="pos", loc=(lerp(mid.x + fw.x * 0.22, WEDGE.x, seg01(f, f_wd + 2, f_wd + 7)), lerp(mid.y + fw.y * 0.22, WEDGE.y, seg01(f, f_wd + 2, f_wd + 7)), floor_z(WEDGE.y) + 0.0), yaw=R(90))
        return dict(mode="pos", loc=(WEDGE.x, WEDGE.y, floor_z(WEDGE.y)), yaw=R(90))
    track(S, a, chair, cspec, 1, N + 11, setter=cset)
    # mantel + vasos: el pie de la silla engancha el mantel y lo arrastra; los vasos salen volando
    base_cl = Vector((TAB.x, TAB.y, 0.0))
    for f in range(1, N + 12):
        u = seg01(f, f_y0 + 1, f_y0 + 9)
        cp = Vector((chair.matrix_world.translation.x if False else 0, 0, 0))
        chp = path_chair(S, a, f, f_g, f_wd, hl, WEDGE)
        tgt = Vector((chp.x + 0.12, chp.y + 0.10, 0.03))
        pos = base_cl.lerp(tgt, u * 0.92 if f < f_wd + 3 else 0.92)
        k = seg01(f, f_y0 + 3, f_y0 + 9)
        S.key(cloth, f, loc=tuple(pos), rot=(0, 0, R(40) * k), scale=(1 + 0.2 * k, 1 + 0.2 * k, 1 - 0.78 * k), interp="LINEAR")
    for i, (o, (ox, oy)) in enumerate(P["cups"]):
        fs = f_y0 + 3 + i; rnd = random.Random(40 + i); v = Vector((-0.8 + rnd.uniform(-0.5, 0.4), -0.4 + rnd.uniform(-0.5, 0.5), 0.0))
        for f in range(1, N + 12):
            if f < f_y0 + 1: p = Vector((TAB.x + ox, TAB.y + oy, 0.80)); rot = (0, 0, 0)
            elif f < fs:
                u = seg01(f, f_y0 + 1, f_y0 + 9); tgt = path_chair(S, a, f, f_g, f_wd, hl, WEDGE); b = Vector((TAB.x + ox, TAB.y + oy, 0.80))
                p = b + (Vector((tgt.x + 0.12, tgt.y + 0.10, 0.80)) - Vector((TAB.x, TAB.y, 0.80))) * (u * 0.92); rot = (0, 0, 0)
            else:
                t = (f - fs) / 24.0; p0 = Vector((TAB.x + ox, TAB.y + oy, 0.80)) + (Vector((-0.2, 0.0, 0.0)) * 0.0)
                p = p0 + v * t * 1.2 + Vector((-0.05 * (i % 3), 0.0, 0.0)); p.z = max(0.045, 0.80 - 4.9 * t * t)
                if p.z <= 0.045: rot = (R(90), 0, R(30 * i)); p.z = 0.045 + 0.02
                else: rot = (R(400 * t), R(250 * t), 0)
            S.key(o, f, loc=tuple(p), rot=rot, scale=(0.038, 0.038, 0.05), interp="LINEAR")
    wind_fx(S, P, lambda f: 1.0, N + 11)
    S.cue("creak", 2, vol=-6); S.cue("hit", f_sl, vol=-1); S.cue("clunk", f_sl, vol=-3); S.cue("hmm", f_dn + 2, vol=-7); S.cue("clunk", f_dn + 5, vol=-4)
    S.cue("whoosh", f_g - 2, vol=-6); S.cue("slide_down", f_y0 + 2, vol=-3)
    for i in range(5): S.cue("clunk", f_y0 + 7 + 2 * i, vol=-5 - i)
    S.cue("clunk", f_wd + 6, vol=-2); S.cue("pop", f_up + 1, vol=-6); S.cue("whoosh", f_in, vol=-7); S.cue("bell", f_in + 20, vol=-4)
    finish(S, a, [(1, "neutra", 1.0), (f_sl, "sorpresa", 0.9), (f_g, "enfado", 0.8), (f_y0 + 4, "sorpresa", 0.9), (f_wd + 4, "enfado", 0.7), (f_in + 18, "feliz", 0.6)], first_blink=13)
    def shake(f):
        t = f - f_sl; k = max(0.0, 1 - t / 6.0) if t >= 0 else 0.0
        return (0.03 * math.sin(f * 2.3) * k, 0.03 * math.cos(f * 1.9) * k)
    cam_keys(S, shake, focus=lambda f: 4.4, cam=(0.30, -2.2, 3.2), tgt=(0.30, 1.6, 0.9), ty=lambda f: lerp(1.6, 2.4, seg01(f, 40, 62)))
    return a


def path_chair(S, a, f, f_g, f_wd, hl, WEDGE):
    """Posicion aproximada de la silla en el fotograma f (solo para el mantel)."""
    if f <= f_g: return Vector((CHAIR0.x, CHAIR0.y, 0.0))
    t = seg01(f, f_g + 1, f_wd)
    return Vector((lerp(CHAIR0.x, WEDGE.x - 0.1, t), lerp(CHAIR0.y, WY - 0.45, t), 0.0))


# ================================================================== NIVEL 9001
def l5(S):
    """9001: portazo (f3); duda (Looking Around); la camara GIRA a la derecha: ventana enorme con cortinas; deja la tarta en la mesa, corre y cierra la ventana
    de un golpe; CORTE a la puerta: sin viento, entra con la tarta intacta (ding)."""
    P = setup(S); door, cake, sash = P["door"], P["cake"], P["sash"]
    f_sl, f_look, f_run0, f_put, f_run1, f_push, f_close, f_cut, f_ding, f_vic = 3, 5, 15, 24, 28, 40, 43, 50, 59, 64
    X0 = 0.02
    a = new_man(S, ["Pushing", "Looking Around", "Running"], X0, 0, PSI)
    seg(S, a, "Pushing", 1, f_look + 1, start=18, speed=1.3, blend=0)
    seg(S, a, "Looking Around", f_look, f_run0 + 1, start=0, speed=1.15, blend=4)
    seg(S, a, "Running", f_run0, f_push, start=0, speed=1.1, blend=3, repeat=3)
    seg(S, a, "Pushing", f_push - 1, None, start=18, speed=1.1, blend=3)
    key_path(S, a, [(1, X0, 0, PSI)], 1, N + 11)
    hl = hand_offset(S, a, (4, 8)); YC = WY - 0.06 - front_dist(hl)
    TBL = Vector((0.95, 0.50)); WS = Vector((2.72, 0.66)); YIN = WY + 1.0
    pts = [(1, X0, YC - 0.05, PSI), (f_sl + 2, X0, YC, PSI), (f_run0 - 1, X0, YC, PSI), (f_run0 + 2, X0 + 0.05, YC - 0.05, 120.0), (f_put + 3, TBL.x, TBL.y, 110.0),
           (f_run1 + 11, WS.x, WS.y, 92.0), (f_push + 4, WS.x + 0.05, WS.y, 92.0), (f_cut - 1, WS.x + 0.05, WS.y, 92.0),
           (f_cut, X0, WY - 0.55, PSI), (f_ding + 4, X0, YIN, PSI), (f_vic + 2, X0, YIN + 0.05, PSI), (f_vic + 10, X0, YIN + 0.05, PSI), (N + 11, X0, YIN + 0.05, PSI)]
    key_path(S, a, pts, 1, N + 11); pin_feet(S, a, 1, N + 11, lambda f: floor_z(path(pts, f)[1]))
    for f in range(1, N + 12):
        ang = slam(f, f_sl - 3, f_sl + 1, A_OPEN, 0.0) if f < f_close + 4 else lerp(0.0, A_OPEN - 4, seg01(f, f_close + 4, f_cut - 1))
        leaf_key(S, door, f, ang if f < f_cut else A_OPEN - 4 + 0.3 * math.sin(f * 0.5) * math.exp(-0.1 * (f - f_cut)))
    for f in range(1, N + 12):                                         # hoja de la ventana: abierta 62 grados hasta que el hombre la golpea
        u = seg01(f, f_push + 1, f_close); a_w = 62.0 * (1 - u * u) if f < f_close else 5.0 * math.exp(-0.4 * (f - f_close)) * abs(math.cos(1.0 * (f - f_close)))
        a_w += 2.0 * math.sin(f * 1.6) * (1 if f < f_push else 0)
        S.key(sash, f, rot=(0, 0, R(a_w)), interp="LINEAR")
    def spec(f):
        if f < f_put: return dict(mode="hand")
        if f < f_put + 4: return dict(mode="hand", **{"from": None}) if False else dict(mode="hand", dz=-0.08 - 0.05 * seg01(f, f_put, f_put + 3), ay=None) if False else dict(mode="hand")
        return dict(mode="pos", loc=(TAB.x, TAB.y, 0.77), yaw=R(0))
    def spec2(f):
        if f < f_put + 1: return dict(mode="hand")
        u = seg01(f, f_put + 1, f_put + 5)
        if f < f_cut:
            mid, yaw = hands_mid(S, a, min(f, f_put + 1)); fw = Vector((math.sin(yaw), -math.cos(yaw), 0)); h0 = mid + fw * FWD + Vector((0, 0, -0.08))
            p = h0.lerp(Vector((TAB.x, TAB.y, 0.77)), u); p.z += 0.18 * math.sin(math.pi * u)
            return dict(mode="pos", loc=p, yaw=yaw)
        return dict(mode="hand")
    track(S, a, cake, spec2, 1, N + 11)
    def wind(f): return 1.0 if f <= f_close else max(0.0, 1.0 - (f - f_close) / 8.0)
    wind_fx(S, P, wind, N + 11)
    S.cue("huh", 2, vol=-8); S.cue("hit", f_sl + 1, vol=-1); S.cue("clunk", f_sl + 1, vol=-3); S.cue("hmm", f_look + 4, vol=-7); S.cue("whoosh", f_run0 + 2, vol=-6)
    S.cue("clunk", f_put + 4, vol=-6); S.cue("whoosh", f_run1, vol=-6); S.cue("hit", f_close, vol=-1); S.cue("clunk", f_close, vol=-2); S.cue("pop", f_close + 1, vol=-5)
    S.cue("wahwah", f_close - 40, vol=-30) if False else None
    S.cue("whoosh", f_cut + 2, vol=-9); S.cue("bell", f_ding, vol=-2); S.cue("tada", f_ding + 1, vol=-3); S.cue("yay", f_vic + 4, vol=-6)
    finish(S, a, [(1, "neutra", 1.0), (f_sl + 1, "sorpresa", 0.6), (f_look + 3, "neutra", 1.0), (f_run0, "enfado", 0.7), (f_close, "enfado", 1.0), (f_cut + 2, "neutra", 1.0), (f_ding, "feliz", 1.0)], first_blink=18, every=40)
    def tx(f):
        if f >= f_cut: return TGT[0]
        a1 = seg01(f, f_run0, f_run0 + 8); a2 = seg01(f, f_run1 - 2, f_run1 + 9)
        return TGT[0] + 0.55 * a1 + 1.75 * a2
    def focus(f): return lerp(3.2, 4.2, seg01(f, f_run1, f_run1 + 10)) if f < f_cut else 3.4
    def shake(f):
        t = f - f_close; k = max(0.0, 1 - t / 6.0) if t >= 0 and f < f_cut else 0.0
        return (0.03 * math.sin(f * 2.3) * k, 0.03 * math.cos(f * 1.9) * k)
    cam_keys(S, shake, focus, tx=tx, ty=lambda f: lerp(TGT[1], 2.2, seg01(f, f_cut + 4, f_cut + 16)) if f >= f_cut else TGT[1])
    return a


LEVELS = [(-400, l1), (-65, l2), (135, l3), (1300, l4), (9001, l5)]
