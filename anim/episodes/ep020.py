"""ep020 — Every IQ Level Moves the Sofa Through the Door (story-023, idea b20261124-2-i02). Portal de un edificio de pisos en dia de mudanza, FACHADA DE
GEOMETRIA (ocre/crema, piedra, buzones, timbres, escalones, farol, ventanas con macetero) + atrezo de Poly Haven; HDRI german_town_street solo para luz.
Plano cercano (el grupo hombre+sofa ocupa ~55 % del alto), camara fija a 2,8 m del hombre, nada importante en el 15 % inferior.

PUERTA DOBLE: hoja izquierda FIJA (cerrada, sin tirador, con una maceta grande delante que esconde la barra de cerrojo de laton) y hoja derecha abierta
(120 grados hacia fuera). Solo la ranura de la hoja derecha (0,7 m) esta libre; el sofa rojo (sofa_02 recoloreado, ~1,6 m, fondo 0,74 m) entra de punta
y se atasca contra las jambas. Otra maceta enorme a la derecha, fuera de la ranura (simetria visual). Lo oculto se descubre solo en el nivel 5.

  -300 F1: sofa encajado y hombre empujando. A ~0,4 s el sofa rebota como un muelle (squash), le da y lo estampa contra la pantalla (fump); se desliza.
  -60  Empuja con el hombro; el marco cruje y asoma una astilla; el sofa avanza un dedo y se atasca; se enfada mirando a camara.
  150  Lo tumba de lado (rodando sobre el respaldo); pasa rozando el marco con chirrido; casi se le cae encima; alivio.
  1200 Corre a la hoja abierta, la saca de las bisagras y la apoya contra la pared; el sofa pasa, la puerta queda sin poder cerrarse; mira el hueco.
  7000 Duda, mira la maceta, la patea: aparece la barra de laton; tira de ella: las dos hojas se abren de par en par, el sofa pasa sin rozar. DING.
Convenio: yaw 0 = mira a camara (-y). 24 fps. Cada nivel 72 fotogramas + 10 de cola (3,4 s); total ~17 s a velocidad 1,0."""
import math, random
import bpy
from mathutils import Vector, Matrix, Euler
from mixamo import MixamoActor
from klunk_toon import apply as klunk, expression, blink
import klunk_toon
import env_real

TITLE = "Every IQ Level Moves the Sofa Through the Door"
ONSCREEN = "Every IQ level moves the sofa through the door"
SPEED = 1.0
ENV = "mesa"
CUSTOM_CAMERA = True
LABEL_STYLE = "big"

N = 72
WY = 2.0                                   # plano de la fachada (cara exterior)
TH = -75.0                                 # giro del sofa (largo casi a lo largo de y; frente hacia -x/camara)
U = Vector((math.cos(math.radians(TH)), math.sin(math.radians(TH)), 0.0))     # de la punta (dentro) a la trasera (fuera)
SX, SY, SZ = 1.0, 1.0, 1.3                 # escala del sofa: 1,8 x 0,82 x 0,92 m
HL, HD, HZ = 0.9 * SX, 0.41 * SY, 0.355 * SZ
TIP = Vector((0.38, WY + 0.55, 0.0))       # punta del sofa encajado (s = 0)
LW = 0.78                                  # ancho de cada hoja (portal de -0,7 a 0,7)
ANG_R = 120.0                              # hoja derecha abierta hacia fuera
CAM = (0.50, -2.7, 1.65); TGT = (0.50, WY - 0.2, 1.04); LENS = 34.0
POT_L, POT_R = Vector((-0.80, WY - 0.50)), Vector((1.62, WY - 0.50))


def R(d): return math.radians(d)
def D(r): return math.degrees(r)
def Rz(d): return Matrix.Rotation(R(d), 4, "Z")
def Tm(v): return Matrix.Translation(Vector(v))
def sstep(t): t = max(0.0, min(1.0, t)); return t * t * (3 - 2 * t)
def lerp(a, b, t): return a + (b - a) * t
def seg01(f, a, b): return sstep((f - a) / float(b - a))


# ------------------------------------------------------------------ materiales y utilidades
def mmat(S, name, rgb, rough=0.5, metal=0.0, emit=None):
    k = "m_" + name
    if k in S.mats: return S.mats[k]
    m = bpy.data.materials.new(k); m.use_nodes = True
    b = m.node_tree.nodes["Principled BSDF"]
    b.inputs["Base Color"].default_value = (*rgb, 1); b.inputs["Roughness"].default_value = rough; b.inputs["Metallic"].default_value = metal
    if emit:
        b.inputs["Emission Color"].default_value = (*emit[0], 1); b.inputs["Emission Strength"].default_value = emit[1]
    S.mats[k] = m
    return m


def O(S, prim, name, mat, loc=(0, 0, 0), scale=(1, 1, 1), rot=(0, 0, 0), parent=None, **kw):
    o = S.obj(prim, name, "white", loc, scale, rot, parent, True, **kw); o.data.materials[0] = mat; return o


def box(S, name, mat, x0, x1, y0, y1, z0, z1, parent=None):
    xa, xb = sorted((x0, x1)); ya, yb = sorted((y0, y1)); za, zb = sorted((z0, z1))
    o = O(S, "cube", name, mat, ((xa + xb) / 2, (ya + yb) / 2, (za + zb) / 2), ((xb - xa) / 2, (yb - ya) / 2, (zb - za) / 2), parent=parent)
    for p in o.data.polygons: p.use_smooth = False
    return o


def wall_mat(S, name, tint):
    k = "wall_" + name
    if k in S.mats: return S.mats[k]
    d = env_real.PH / "beige_wall_001"; m = bpy.data.materials.new(k); m.use_nodes = True; Nn = m.node_tree.nodes; L = m.node_tree.links
    b = Nn["Principled BSDF"]; geo = Nn.new("ShaderNodeNewGeometry"); mp = Nn.new("ShaderNodeMapping"); mp.inputs["Scale"].default_value = (0.5, 0.5, 0.5)
    L.new(geo.outputs["Position"], mp.inputs["Vector"])
    def tex(suffix, cs="sRGB"):
        t = Nn.new("ShaderNodeTexImage"); t.image = bpy.data.images.load(str(next(iter(sorted(d.glob(f"*_{suffix}_2k.*")))))); t.image.colorspace_settings.name = cs
        t.projection = "BOX"; t.projection_blend = 0.2; L.new(mp.outputs["Vector"], t.inputs["Vector"]); return t
    c = tex("diff"); r = tex("rough", "Non-Color"); n = tex("nor_gl", "Non-Color")
    tn = Nn.new("ShaderNodeMix"); tn.data_type = "RGBA"; tn.blend_type = "MULTIPLY"; tn.inputs[0].default_value = 1.0; tn.inputs[7].default_value = (*tint, 1)
    L.new(c.outputs["Color"], tn.inputs[6]); L.new(tn.outputs[2], b.inputs["Base Color"]); L.new(r.outputs["Color"], b.inputs["Roughness"])
    nm = Nn.new("ShaderNodeNormalMap"); L.new(n.outputs["Color"], nm.inputs["Color"]); L.new(nm.outputs["Normal"], b.inputs["Normal"])
    S.mats[k] = m; return m


FINGERS = ("Thumb", "Index", "Middle", "Ring", "Pinky")


def seg(S, a, clip, f0, f1=None, start=0, speed=1.0, blend=4, repeat=None):
    S.f = f0
    cl = a.clips[clip]; per = max(1, int((cl.frame_range[1] - cl.frame_range[0] - start) / speed))
    if f1 is None: a.play(clip, frames=None, speed=speed, blend=blend, start=start, repeat=repeat or 1)
    else:
        n = f1 - f0 + blend
        a.play(clip, frames=n, speed=speed, blend=blend, start=start, repeat=repeat or (n // per + 2))


def faces(a, ev, n_end, first_blink=16, every=44):
    f = first_blink
    while f < n_end - 6:
        blink(a, f); f += every
    for f, name, v in ev: expression(a, name, f, v, ramp=3)


def pin_feet(S, a, f0, f1, floor, off=0.02):
    for f in range(f0, f1 + 1):
        S.sc.frame_set(f); bpy.context.view_layer.update()
        zs = [(a.arm.matrix_world @ a.arm.pose.bones[a.pfx + b].tail).z for b in ("LeftToeBase", "RightToeBase", "LeftFoot", "RightFoot")]
        d = floor(f) + off - min(zs)
        loc = a.root.location.copy(); rot = a.root.rotation_euler.copy()
        S.key(a.root, f, loc=(loc.x, loc.y, loc.z + d), rot=(rot.x, rot.y, rot.z), interp="LINEAR")


def bone_w(a, bone, frac=0.0):
    pb = a.arm.pose.bones[a.pfx + bone]
    return a.arm.matrix_world @ (pb.head + (pb.tail - pb.head) * frac)


def hand_offset(S, a, frames):
    """Media de las dos palmas en el marco de la raiz (solo x, y) sobre varios fotogramas."""
    acc = Vector((0, 0, 0))
    for f in frames:
        S.sc.frame_set(f); bpy.context.view_layer.update()
        p = (bone_w(a, "LeftHand", 0.6) + bone_w(a, "RightHand", 0.6)) * 0.5
        acc += a.root.matrix_world.inverted() @ p
    return acc / len(frames)


def key_path(S, a, pts, f0, f1, scale=None):
    """pts: lista (f, x, y, yaw[, z]) con interpolacion suave; se keya la raiz del hombre en cada fotograma."""
    for f in range(f0, f1 + 1):
        for (fa, *va), (fb, *vb) in zip(pts, pts[1:]):
            if fa <= f <= fb:
                t = sstep((f - fa) / float(max(1, fb - fa))); v = [lerp(x, y, t) for x, y in zip(va, vb)]; break
        else:
            v = pts[-1][1:] if f > pts[-1][0] else pts[0][1:]
        z = v[3] if len(v) > 3 else 0.0
        S.key(a.root, f, loc=(v[0], v[1], z), rot=(0, 0, R(v[2])), interp="LINEAR")
        if scale: S.key(a.root, f, scale=scale(f), interp="LINEAR")


# ------------------------------------------------------------------ escenario
def stage(S):
    for o in list(S.sc.objects):
        if o.name.startswith("sun") or o is S.cam or o is S.tgt: continue
        bpy.data.objects.remove(o, do_unlink=True)
    env_real._hdri(S, name="german_town_street", strength=0.9, rot_deg=200)
    sun = bpy.data.objects["sun"]; sun.data.energy = 4.2; sun.data.color = (1.0, 0.92, 0.78); sun.data.angle = R(2.0)
    sun.rotation_euler = (R(52), 0, R(-28))
    S.sc.view_settings.view_transform = "AgX"
    try: S.sc.view_settings.look = "AgX - Punchy"; S.sc.view_settings.exposure = 0.05
    except Exception: pass
    S.water = None
    S.cam.location = CAM; S.cam.data.lens = LENS; S.tgt.location = TGT
    S.cam.data.dof.use_dof = True; S.cam.data.dof.aperture_fstop = 3.5; S.cam.data.dof.focus_distance = 3.1
    # suelo: adoquin PBR en metros
    cob = env_real._pbr(S, "cobblestone_floor_01", scale=1.0)
    bpy.ops.mesh.primitive_plane_add(size=1, location=(0, 10, 0)); g = bpy.context.object; g.name = "suelo"; g.scale = (60, 60, 1); g.data.materials.append(cob)
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    me = g.data; me.uv_layers.active.data.foreach_set("uv", [c for l in me.loops for c in (me.vertices[l.vertex_index].co.x / 1.5, me.vertices[l.vertex_index].co.y / 1.5)])
    ocre = wall_mat(S, "ocre", (1.0, 0.80, 0.50)); crema = wall_mat(S, "crema", (1.0, 0.93, 0.78))
    stone = mmat(S, "piedra", (0.62, 0.58, 0.50), 0.85); stone_d = mmat(S, "piedra_osc", (0.30, 0.28, 0.25), 0.9)
    white = mmat(S, "marco_blanco", (0.90, 0.87, 0.78), 0.6); iron = mmat(S, "hierro", (0.03, 0.03, 0.035), 0.5, 0.7)
    dark = mmat(S, "interior", (0.10, 0.065, 0.045), 0.9); warm = mmat(S, "interior_luz", (0.55, 0.30, 0.12), 0.9, 0.0, ((1.0, 0.55, 0.2), 0.55))
    glass = mmat(S, "cristal", (0.10, 0.16, 0.22), 0.05, 0.0, ((0.3, 0.45, 0.6), 0.25)); brass = mmat(S, "laton", (0.95, 0.68, 0.22), 0.22, 1.0, ((1.0, 0.7, 0.2), 0.5))
    # muro con hueco de portal (z 0-2,35) + hall con pared del fondo; espesor 0,5
    T = 0.5; HX = LW + 0.0; ZD = 2.35
    box(S, "muro_izq", ocre, -9, -HX, WY, WY + T, 0, 2.30); box(S, "muro_der", ocre, HX, 9, WY, WY + T, 0, 2.30)
    box(S, "muro_sup_p", ocre, -HX, HX, WY, WY + T, ZD, 2.30) if ZD < 2.30 else None
    box(S, "muro_alto", crema, -9, 9, WY, WY + T, 2.30, 8.0)
    box(S, "muro_dintel", ocre, -HX, HX, WY, WY + T, ZD - 0.0, 2.30) if False else None
    # zocalo, cornisa y pilastras
    box(S, "zocalo", stone_d, -9, 9, WY - 0.07, WY + 0.02, 0, 0.55); box(S, "zocalo_borde", stone, -9, 9, WY - 0.09, WY - 0.02, 0.50, 0.58)
    box(S, "cornisa", white, -9, 9, WY - 0.12, WY + 0.05, 2.30, 2.42); box(S, "cornisa2", stone, -9, 9, WY - 0.16, WY + 0.05, 5.0, 5.14)
    for sx in (-1, 1):
        px0, px1 = (sx * HX, sx * (HX + 0.25)); box(S, "pilastra", white, px0, px1, WY - 0.10, WY + 0.05, 0.0, 2.30)
        box(S, "pil_base", stone, px0 - sx * 0.03, px1 + sx * 0.03, WY - 0.13, WY + 0.05, 0.0, 0.34); box(S, "pil_cap", stone, px0 - sx * 0.03, px1 + sx * 0.03, WY - 0.13, WY + 0.05, 2.12, 2.30)
    box(S, "dintel", stone, -HX - 0.3, HX + 0.3, WY - 0.16, WY + 0.05, 2.10, 2.30)
    box(S, "marco_sup", white, -HX, HX, WY - 0.05, WY + 0.2, 2.05, 2.12)
    # luz de montante sobre la puerta (dos paneles de cristal con parteluz)
    box(S, "montante_m", white, -HX, HX, WY - 0.04, WY + 0.1, 2.12, 2.30)
    box(S, "montante_c", glass, -HX + 0.05, HX - 0.05, WY + 0.04, WY + 0.08, 2.14, 2.28); box(S, "montante_p", white, -0.015, 0.015, WY - 0.05, WY + 0.1, 2.12, 2.30)
    # escalones de piedra delante del portal
    box(S, "escalon1", stone, -1.25, 1.95, WY - 0.32, WY, 0, 0.10); box(S, "escalon2", stone, -1.05, 1.75, WY - 0.62, WY - 0.32, 0, 0.05)
    box(S, "escalon1_borde", stone_d, -1.25, 1.95, WY - 0.33, WY - 0.30, 0.0, 0.10)
    # hall interior: suelo, paredes, techo, fondo luminoso
    HD_ = 3.0
    box(S, "hall_suelo", dark, -HX, HX, WY, WY + HD_, 0.0, 0.10); box(S, "hall_pared_i", dark, -HX - 0.05, -HX, WY, WY + HD_, 0.0, 2.35)
    box(S, "hall_pared_d", dark, HX, HX + 0.05, WY, WY + HD_, 0.0, 2.35); box(S, "hall_techo", dark, -HX, HX, WY, WY + HD_, 2.35, 2.40)
    box(S, "hall_fondo", dark, -HX, HX, WY + HD_, WY + HD_ + 0.05, 0.0, 2.35); box(S, "hall_luz", warm, -HX + 0.25, HX - 0.25, WY + HD_ - 0.02, WY + HD_, 0.5, 2.0)
    rug = mmat(S, "alfombra", (0.45, 0.05, 0.06), 0.9); box(S, "alfombra", rug, -0.55, 0.55, WY + 0.4, WY + 2.8, 0.10, 0.115)
    box(S, "cuadro_marco", white, -0.30, 0.30, WY + HD_ - 0.06, WY + HD_ - 0.02, 1.05, 1.75); box(S, "cuadro", mmat(S, "cuadro_lienzo", (0.12, 0.35, 0.55), 0.7), -0.25, 0.25, WY + HD_ - 0.07, WY + HD_ - 0.06, 1.10, 1.70)
    box(S, "cuadro_sol", mmat(S, "cuadro_sol", (0.95, 0.75, 0.15), 0.7), -0.10, 0.10, WY + HD_ - 0.075, WY + HD_ - 0.07, 1.35, 1.55)
    bpy.ops.object.light_add(type="POINT", location=(0.0, WY + 1.2, 1.9)); Lg = bpy.context.object; Lg.data.energy = 220; Lg.data.color = (1.0, 0.65, 0.35); Lg.data.shadow_soft_size = 0.5
    # buzones (3 x 2), placa de timbres, farol, numero de casa, ventanas con maceteros
    mb = [mmat(S, "buzon%d" % i, c, 0.35, 0.6) for i, c in enumerate(((0.55, 0.57, 0.60), (0.75, 0.62, 0.15), (0.50, 0.12, 0.10)))]
    for r in range(2):
        for c in range(3):
            x0 = 1.18 + c * 0.24; z0 = 1.72 + r * 0.30
            box(S, "buzon", mb[(r + c) % 3], x0, x0 + 0.21, WY - 0.09, WY, z0, z0 + 0.26); box(S, "buzon_ranura", iron, x0 + 0.03, x0 + 0.18, WY - 0.095, WY - 0.09, z0 + 0.17, z0 + 0.19)
    box(S, "timbres", brass, -HX - 0.20, -HX - 0.04, WY - 0.115, WY - 0.09, 1.28, 1.58)
    for i in range(4): O(S, "cylinder", "timbre", mmat(S, "timbre_boton", (0.95, 0.93, 0.88), 0.3), (-HX - 0.12, WY - 0.12, 1.33 + i * 0.07), (0.018, 0.018, 0.012), (R(90), 0, 0))
    box(S, "placa_num", brass, 0.80, 1.05, WY - 0.06, WY - 0.02, 2.58, 2.76)
    for i in range(2): box(S, "num_cifra", iron, 0.85 + i * 0.10, 0.92 + i * 0.10, WY - 0.065, WY - 0.06, 2.62, 2.73)
    O(S, "cylinder", "brazo_farol", iron, (-0.3, WY - 0.2, 2.95), (0.015, 0.015, 0.2), (R(90), 0, 0)); O(S, "cylinder", "farol", warm, (-0.3, WY - 0.42, 2.88), (0.07, 0.07, 0.13))
    O(S, "cone", "farol_tejado", iron, (-0.3, WY - 0.42, 3.05), (0.09, 0.09, 0.05), vertices=12, radius1=1.0, radius2=0.1, depth=2.0)
    shut = mmat(S, "contraventana", (0.12, 0.30, 0.45), 0.55); terra = mmat(S, "terracota", (0.62, 0.30, 0.16), 0.8); leaf = mmat(S, "hoja_v", (0.10, 0.34, 0.08), 0.7)
    red = mmat(S, "geranio", (0.88, 0.07, 0.10), 0.6)
    for wx in (-0.55, 1.35):
        box(S, "ventana_marco", white, wx - 0.45, wx + 0.45, WY - 0.06, WY + 0.15, 3.05, 4.30); box(S, "ventana_cristal", glass, wx - 0.38, wx + 0.38, WY + 0.05, WY + 0.09, 3.12, 4.23)
        box(S, "ventana_trav", white, wx - 0.38, wx + 0.38, WY - 0.03, WY + 0.1, 3.64, 3.70); box(S, "ventana_pil", white, wx - 0.02, wx + 0.02, WY - 0.03, WY + 0.1, 3.12, 4.23)
        box(S, "alfeizar", stone, wx - 0.55, wx + 0.55, WY - 0.30, WY + 0.15, 2.95, 3.05)
        box(S, "maceta_v", terra, wx - 0.40, wx + 0.40, WY - 0.30, WY - 0.08, 3.05, 3.28)
        for i in range(6):
            O(S, "uv_sphere", "mata", leaf, (wx - 0.32 + i * 0.13, WY - 0.19, 3.33), (0.10, 0.09, 0.08), segments=10, ring_count=6)
            O(S, "uv_sphere", "flor", red, (wx - 0.32 + i * 0.13, WY - 0.22, 3.42 + 0.02 * (i % 2)), (0.045,) * 3, segments=8, ring_count=6)
        for sg in (-1, 1):
            box(S, "contra_u", shut, wx + sg * 0.46, wx + sg * 0.88, WY - 0.07, WY - 0.04, 3.05, 4.30)
            for k in range(8): box(S, "lama", mmat(S, "contra_osc", (0.07, 0.19, 0.30), 0.6), wx + sg * 0.50, wx + sg * 0.84, WY - 0.085, WY - 0.07, 3.10 + k * 0.15, 3.15 + k * 0.15)
    pipe = mmat(S, "bajante", (0.18, 0.19, 0.20), 0.5, 0.6)
    O(S, "cylinder", "bajante", pipe, (2.15, WY - 0.07, 2.5), (0.045, 0.045, 2.5))
    for zz in (0.8, 2.0, 3.4, 4.6): O(S, "cylinder", "abrazadera", pipe, (2.15, WY - 0.07, zz), (0.06, 0.06, 0.03))
    return dict(brass=brass, white=white, iron=iron)


def build_props(S):
    """Atrezo de Poly Haven (CC0) repartido en primer plano (cajas), plano medio (macetas, cajas de luz) y fondo (farola, banco, camion)."""
    cols = {}
    def put(name, res, x, y, h, rot, z=0.0):
        if (name, res) not in cols: cols[(name, res)] = env_real._model(name, res)
        bpy.context.view_layer.update(); return env_real._place_fit(S, cols[(name, res)], (x, y, z), h, R(rot))[0]
    pot_l = put("potted_plant_02", "1k", POT_L.x, POT_L.y, 1.55, 20)
    pot_r = put("potted_plant_02", "1k", POT_R.x, POT_R.y, 1.55, 200)
    lf = [mmat(S, "arbusto%d" % i, c, 0.65) for i, c in enumerate(((0.06, 0.26, 0.05), (0.14, 0.40, 0.08), (0.04, 0.20, 0.06)))]
    grp = {}
    for nm, P_, inst in (("l", POT_L, pot_l), ("r", POT_R, pot_r)):                 # arbusto denso sobre la maceta (esconde lo que hay detras); el grupo se mueve junto
        g = S.empty("maceta_" + nm, (0, 0, 0)); inst.parent = g; grp[nm] = g
        rnd = random.Random(5 if nm == "l" else 9); sx_ = 1 if nm == "l" else -1
        for i in range(26):                                                           # hojas grandes y aplastadas, orientadas al azar
            while True:
                u, v, w = rnd.uniform(-1, 1), rnd.uniform(-1, 1), rnd.uniform(-1, 1)
                if u * u + v * v + w * w < 1: break
            rr = rnd.uniform(0.15, 0.24)
            O(S, "uv_sphere", "arbusto", lf[i % 3], (P_.x + (0.20 + 0.46 * u) * sx_, P_.y + 0.34 * v, 1.08 + 0.58 * w), (rr * 1.3, rr * 0.55, rr * 0.9),
              (rnd.uniform(-0.6, 0.6), rnd.uniform(-0.6, 0.6), rnd.uniform(0, 6.28)), parent=g, segments=10, ring_count=6)
    put("power_box_01", "1k", -1.05, WY - 0.05, 0.5, 0, z=1.95)            # contador electrico sobre la maceta izquierda
    put("utility_box_01", "1k", 2.55, WY - 0.2, 1.3, 0)
    put("cardboard_box_01", "1k", -1.15, 0.20, 0.40, 28); put("cardboard_box_01", "1k", -1.13, 0.21, 0.40, -12, z=0.40)       # pila de cajas (primer plano izq.)
    put("cardboard_box_01", "1k", 1.42, 0.70, 0.36, 70)
    put("potted_plant_04", "1k", -0.28, WY - 0.22, 0.20, 0, z=0.10)         # suculenta sobre el escalon
    put("street_lamp_01", "2k", -2.4, WY - 0.6, 4.6, 0)
    put("fire_hydrant", "1k", 2.9, 0.4, 0.8, 25); put("metal_trash_can", "2k", -3.3, 1.2, 1.0, 20); put("trashbag", "1k", -2.8, 0.8, 0.5, 60)
    put("painted_wooden_bench", "1k", 3.6, 1.2, 0.9, 0)
    put("plastic_crate_01", "1k", -1.5, 0.9, 0.34, 20); put("wooden_crate_01", "1k", 1.9, 0.9, 0.5, -15)
    # camion de mudanzas (primitivas) a un lado, al fondo de la calle
    wh = mmat(S, "camion_blanco", (0.92, 0.92, 0.90), 0.45); bl = mmat(S, "camion_azul", (0.10, 0.30, 0.62), 0.45); blk = mmat(S, "camion_negro", (0.03, 0.03, 0.035), 0.6)
    T0 = Vector((4.3, 1.4, 0.0))
    box(S, "camion_caja", wh, T0.x, T0.x + 2.4, T0.y - 0.5, T0.y + 4.5, 0.55, 3.0); box(S, "camion_franja", bl, T0.x - 0.002, T0.x + 2.402, T0.y - 0.52, T0.y + 4.52, 1.6, 2.0)
    box(S, "camion_cabina", bl, T0.x, T0.x + 2.4, T0.y + 4.55, T0.y + 6.1, 0.55, 2.4); box(S, "camion_chasis", blk, T0.x + 0.1, T0.x + 2.3, T0.y - 0.4, T0.y + 6.0, 0.3, 0.55)
    for yy in (T0.y + 0.6, T0.y + 4.9):
        for xx in (T0.x - 0.01, T0.x + 2.41): O(S, "cylinder", "rueda", blk, (xx, yy, 0.45), (0.45, 0.45, 0.14), (0, R(90), 0))
    box(S, "camion_puerta", mmat(S, "camion_gris", (0.75, 0.76, 0.78), 0.4, 0.4), T0.x + 0.1, T0.x + 2.3, T0.y - 0.52, T0.y - 0.50, 0.8, 2.8)
    return dict(pot_l=pot_l, pot_r=pot_r, grp_l=grp['l'], grp_r=grp['r'])


# ------------------------------------------------------------------ puerta doble y barra de cerrojo
def build_door(S, E):
    blue = mmat(S, "puerta_azul", (0.03, 0.16, 0.72), 0.42); blue2 = mmat(S, "puerta_panel", (0.05, 0.24, 0.85), 0.40); brass = E["brass"]
    iron = E["iron"]; shine = mmat(S, "laton_vivo", (1.0, 0.55, 0.08), 0.18, 1.0, ((1.0, 0.5, 0.1), 0.35))
    leaves = {}
    for name, sg, hx in (("izq", 1, -LW), ("der", -1, LW)):
        h = S.empty("hoja_" + name, (hx, WY - 0.03, 0.05))
        box(S, "hoja_losa", blue, 0, sg * LW, -0.03, 0.03, 0.0, 2.05, h)
        for (a0, a1, z0, z1) in ((0.08, 0.33, 0.14, 0.95), (0.37, 0.62, 0.14, 0.95), (0.08, 0.33, 1.07, 1.97), (0.37, 0.62, 1.07, 1.97)):
            box(S, "panel", blue2, sg * a0, sg * a1, -0.045, -0.03, z0, z1, h)
        box(S, "zocalo_laton", brass, sg * 0.02, sg * (LW - 0.02), -0.05, -0.03, 0.02, 0.12, h)
        for zz in (0.30, 1.00, 1.75): O(S, "cylinder", "bisagra", brass, (0, -0.035, zz), (0.022, 0.022, 0.05), parent=h)
        if name == "der":
            box(S, "placa_tirador", brass, sg * (LW - 0.12), sg * (LW - 0.04), -0.05, -0.03, 0.85, 1.12, h); O(S, "uv_sphere", "tirador", brass, (sg * (LW - 0.08), -0.08, 1.0), (0.032,) * 3, parent=h)
        leaves[name] = h
    # barra de cerrojo (hoja izquierda fija): soportes fijos + barra deslizante de laton 1 m + empunadura grande
    hL = leaves["izq"]
    bar_root = S.empty("barra_raiz", (0.30, -0.075, 0.0), hL)
    for zz in (0.60, 1.10, 1.60): O(S, "cylinder", "soporte_barra", brass, (0, 0, zz), (0.045, 0.045, 0.04), (R(90), 0, 0), bar_root)
    box(S, "enchufe_suelo", iron, -0.04, 0.04, -0.035, 0.0, 0.0, 0.12, bar_root)
    slide = S.empty("barra_desliza", (0, 0, 0), bar_root)
    O(S, "cylinder", "barra", shine, (0, 0, 1.1), (0.042, 0.042, 0.52), parent=slide, vertices=20)
    O(S, "cylinder", "barra_punta", shine, (0, 0, 0.55), (0.030, 0.030, 0.06), parent=slide, vertices=12)
    O(S, "cylinder", "agarre", shine, (0.0, -0.075, 0.78), (0.02, 0.02, 0.11), (0, R(90), 0), slide, vertices=12)
    O(S, "uv_sphere", "agarre_bola_i", shine, (-0.11, -0.075, 0.78), (0.045,) * 3, parent=slide); O(S, "uv_sphere", "agarre_bola_d", shine, (0.11, -0.075, 0.78), (0.045,) * 3, parent=slide)
    box(S, "agarre_pata", shine, -0.012, 0.012, -0.075, -0.02, 0.76, 0.80, slide)
    # destello de revelacion (dos barritas cruzadas, invisibles hasta la animacion)
    gl = mmat(S, "destello", (1, 1, 0.9), 0.1, 0.0, ((1, 0.95, 0.7), 8.0)); glint = S.empty("destello", (0.0, -0.20, 1.45), hL); glint.scale = (0, 0, 0)
    for r in (0, 45, 90, 135): O(S, "cube", "rayo", gl, (0, 0, 0), (0.18, 0.006, 0.006), (0, R(r), 0), glint)
    return dict(leaves=leaves, slide=slide, glint=glint, bar_root=bar_root)


def leaf_keys(S, D, f, ang_l, ang_r):
    S.key(D["leaves"]["izq"], f, rot=(0, 0, R(-ang_l)), interp="LINEAR"); S.key(D["leaves"]["der"], f, rot=(0, 0, R(ang_r)), interp="LINEAR")


# ------------------------------------------------------------------ sofa rojo (sofa_02 recoloreado)
def build_sofa(S):
    col = env_real._model("sofa_02", "1k")
    red = (0.90, 0.0, 0.012)
    for o in col.objects:
        if o.type != "MESH": continue
        for sl in o.material_slots:
            m = sl.material
            if not m or not m.use_nodes: continue
            b = m.node_tree.nodes.get("Principled BSDF")
            for l in list(b.inputs["Base Color"].links): m.node_tree.links.remove(l)
            b.inputs["Base Color"].default_value = (*red, 1); b.inputs["Roughness"].default_value = 0.42
            for k in ("Coat Weight", "Sheen Weight"):
                if k in b.inputs: b.inputs[k].default_value = 0.0
    root = S.empty("sofa", (0, 0, 0)); root.scale = (SX, SY, SZ)
    inst = env_real._place(S, col, (0, -0.07, -0.355), 0.0, 1.0); inst.parent = root
    return root


def sofa_key(S, root, f, s=0.0, roll=0.0, dyaw=0.0, sq=(1, 1, 1), dz=0.0, side=0.0):
    C = TIP + U * HL - U * s + Vector((-U.y, U.x, 0)) * side
    zc = 0.05 + HZ * sq[2] * abs(math.cos(R(roll))) + HD * sq[1] * abs(math.sin(R(roll))) + dz
    S.key(root, f, loc=(C.x, C.y, zc), rot=(R(roll), 0, R(TH + dyaw)), scale=(SX * sq[0], SY * sq[1], SZ * sq[2]), interp="LINEAR")
    return C


def trailing(s, extra=0.0):
    return TIP + U * (2 * HL + extra) - U * s


def damp(t, k=0.20, w=0.9): return math.exp(-k * t) * math.cos(w * t) if t >= 0 else 0.0


# ------------------------------------------------------------------ hombre
def new_man(S, uses, x, y, yaw):
    a = MixamoActor(S, x=x, yaw=yaw, use=uses); klunk(a, seed=23)
    for o in a.meshes:
        n = o.name.split(".")[0]
        if n == "Ch01_Shirt": klunk_toon._flat(o, klunk_toon._mat("toon_camisa", (0.04, 0.42, 0.22), 0.8, 0.2))
        if n == "Ch01_Pants": klunk_toon._flat(o, klunk_toon._mat("toon_pantalon_k", (0.62, 0.50, 0.30), 0.8, 0.2))
    S.key(a.root, 1, loc=(x, y, 0.0), rot=(0, 0, R(yaw)), interp="LINEAR")
    return a


PSI = 180.0 + 15.0                                  # yaw empujando: mira hacia la punta (-U)


def push_root(S, a, hl, s, yaw=PSI, lunge=0.0, up=0.0):
    """Posicion de la raiz para que las manos queden sobre el extremo trasero del sofa."""
    H = trailing(s, 0.02) - U * lunge
    off = Matrix.Rotation(R(yaw), 3, "Z") @ Vector((hl.x, hl.y, 0))
    return Vector((H.x - off.x, H.y - off.y, up))


_E = [None]


def setup(S):
    _E[0] = stage(S); P = build_props(S); sofa = build_sofa(S); Dr = build_door(S, _E[0]); return P, sofa, Dr


def cam_keys(S, shake=None, focus=None, n=N + 10):
    bpy.context.preferences.edit.keyframe_new_interpolation_type = "LINEAR"
    for f in range(1, n + 1):
        sh = shake(f) if shake else (0.0, 0.0)
        S.cam.location = (CAM[0] + sh[0], CAM[1], CAM[2] + sh[1]); S.cam.keyframe_insert("location", frame=f)
        S.cam.data.dof.focus_distance = focus(f) if focus else 3.1; S.cam.data.dof.keyframe_insert("focus_distance", frame=f)


def dust(S, pos, f0, n=4, r=0.10, col=(0.85, 0.78, 0.65), spread=0.12, seed=1):
    m = mmat(S, "polvo", col, 0.95)
    for i in range(n):
        ang = 2.4 * i + seed; d = Vector((math.cos(ang) * spread, -0.05 - 0.05 * (i % 2), 0.05 + 0.04 * i))
        o = O(S, "uv_sphere", "polvo", m, tuple(pos), (0, 0, 0), segments=10, ring_count=6)
        S.key(o, f0, loc=tuple(pos), scale=(0, 0, 0), interp="LINEAR"); S.key(o, f0 + 5, loc=tuple(Vector(pos) + d * 0.6), scale=(r, r, r), interp="LINEAR")
        S.key(o, f0 + 14, loc=tuple(Vector(pos) + d * 1.6 + Vector((0, 0, 0.10))), scale=(0, 0, 0), interp="LINEAR")


# ------------------------------------------------------------------ nivel -300
def l1(S):
    """-300: f1 sofa encajado y hombre empujando; f9 el sofa rebota (muelle) y lo estampa contra la pantalla (fump); se desliza hacia abajo."""
    P, sofa, Dr = setup(S); leaf_keys(S, Dr, 1, 0.0, ANG_R)
    a = new_man(S, ["Pushing", "Surprised"], 0, 0, PSI)
    f_sp, f_hit, f_splat, f_slide = 9, 13, 21, 54
    seg(S, a, "Pushing", 1, f_hit, start=14, speed=1.25, blend=0)
    seg(S, a, "Surprised", f_hit - 1, None, start=0, speed=1.0, blend=3)
    key_path(S, a, [(1, 0, 0, PSI)], 1, N + 11)
    S.sc.frame_set(1); bpy.context.view_layer.update()
    hl = hand_offset(S, a, (4, 8))
    def s_of(f):
        if f < f_sp: return 0.010 * math.sin(f * 2.7) + 0.02 * seg01(f, 4, f_sp)
        if f < f_sp + 4: return lerp(0.03, -0.75, seg01(f, f_sp, f_sp + 4))
        t = f - (f_sp + 4)
        return -0.75 * math.exp(-0.17 * t) * math.cos(0.55 * t) * 0.9 if t > 0 else -0.75
    def sq_of(f):
        if f < f_sp - 2: return (1.0 + 0.01 * math.sin(f * 2.7), 1, 1)
        if f < f_sp + 1: t = seg01(f, f_sp - 2, f_sp + 1); return (lerp(1.0, 0.78, t), lerp(1, 1.14, t), lerp(1, 1.18, t))          # comprimido antes de soltarse
        if f < f_sp + 4: t = seg01(f, f_sp + 1, f_sp + 4); return (lerp(0.78, 1.16, t), lerp(1.14, 0.88, t), lerp(1.18, 0.90, t))     # estirado en el aire
        t = f - (f_sp + 4); k = math.exp(-0.15 * t) * math.cos(0.6 * t)
        return (1.0 + 0.16 * k, 1.0 - 0.12 * k, 1.0 - 0.10 * k)
    for f in range(1, N + 12): sofa_key(S, sofa, f, s=s_of(f), sq=sq_of(f))
    # hombre: empuja pegado al sofa; golpe en f_hit: vuelo hacia la camara con giro; se estampa en f_splat (cara contra la pantalla)
    HIT = push_root(S, a, hl, s_of(f_hit)); END = Vector((0.58, CAM[1] + 0.78))
    zc = 1.50 - 1.70 * 0.80                                              # cabeza centrada en la pantalla, aplastado a 0,8 de alto
    def man_pos(f):
        if f < f_hit: p = push_root(S, a, hl, s_of(f)); return p.x, p.y, PSI, 0.0
        if f < f_splat:
            t = (f - f_hit) / float(f_splat - f_hit); u = t * t * (3 - 2 * t) * 0.55 + t * 0.45
            return lerp(HIT.x, END.x, u), lerp(HIT.y, END.y, u), lerp(PSI, 360.0, u), 0.7 * 4 * t * (1 - t) + lerp(0.0, zc, u * u)
        t = f - f_splat
        if f < f_slide: return END.x + 0.012 * math.sin(t * 1.3), END.y, 360.0 + 3 * math.sin(t * 0.9), zc
        u = sstep((f - f_slide) / 14.0); return END.x, END.y, 360.0, zc - 1.9 * u * u
    def man_sc(f):
        if f < f_hit: return (1, 1, 1)
        if f < f_splat: t = (f - f_hit) / float(f_splat - f_hit); return (lerp(1, 1.1, t), lerp(1, 0.9, t), lerp(1, 0.95, t))
        t = f - f_splat; e = max(0.0, 1 - t / 6.0)
        if f < f_slide: return (1.34 + 0.05 * e * math.sin(t * 2.2), 0.40, 0.80 - 0.06 * e)
        u = seg01(f, f_slide, f_slide + 12); return (lerp(1.34, 1.0, u), 0.40, lerp(0.80, 1.0, u))
    key_path(S, a, [(1, 0, 0, PSI)], 1, 2)
    for f in range(1, N + 12):
        x, y, yw, z = man_pos(f); S.key(a.root, f, loc=(x, y, z), rot=(0, 0, R(yw)), scale=man_sc(f), interp="LINEAR")
    pin_feet(S, a, 1, f_hit - 1, lambda f: 0.0)
    S.cue("huh", f_sp - 2, vol=-8); S.cue("boing", f_sp, vol=-4); S.cue("hit", f_hit, vol=-3); S.cue("whoosh", f_hit + 1, vol=-5)
    S.cue("hit", f_splat, vol=-1); S.cue("oof", f_splat + 1, vol=-3); S.cue("slide_down", f_slide, vol=-5); S.cue("wahwah", f_slide + 6, vol=-8)
    S.f = N; a.verify(S.f)
    faces(a, [(1, "enfado", 0.7), (f_sp - 2, "sorpresa", 0.6), (f_hit, "sorpresa", 1.0), (f_splat, "sorpresa", 1.0), (f_slide + 4, "neutra", 0.6)], N, first_blink=14, every=40)
    def shake(f):
        t = f - f_splat
        return (0.05 * math.sin(f * 2.1) * max(0.0, 1 - t / 8.0), 0.05 * math.cos(f * 1.7) * max(0.0, 1 - t / 8.0)) if 0 <= t < 10 else (0.0, 0.0)
    def focus(f):
        if f < f_hit: return 3.0
        if f < f_slide + 6: return lerp(3.0, 0.9, seg01(f, f_hit, f_splat))
        return lerp(0.9, 3.0, seg01(f, f_slide + 6, f_slide + 14))
    cam_keys(S, shake, focus)
    dust(S, (0.45, WY - 0.2, 0.9), f_sp + 1, n=5, r=0.12, seed=2)
    return a


# ------------------------------------------------------------------ nivel -60
def l2(S):
    """-60: empuja mas fuerte con el hombro; el marco cruje y asoma una astilla; el sofa avanza un dedo y se atasca; se enfada y mira a camara."""
    P, sofa, Dr = setup(S); leaf_keys(S, Dr, 1, 0.0, ANG_R)
    a = new_man(S, ["Pushing", "Angry"], 0, 0, PSI)
    f_w, f_c, f_t, f_a = 14, 21, 34, 38
    seg(S, a, "Pushing", 1, f_t + 2, start=10, speed=1.45, blend=0)
    seg(S, a, "Angry", f_t, None, start=0, speed=1.0, blend=5)
    key_path(S, a, [(1, 0, 0, PSI)], 1, N + 11)
    hl = hand_offset(S, a, (4, 8))
    def s_of(f):
        sh = 0.012 * math.sin(f * 3.1) * (1 if f < f_t else math.exp(-0.3 * (f - f_t)))
        return 0.02 + 0.07 * seg01(f, f_c, f_c + 3) + sh
    def lunge(f): return 0.13 * seg01(f, f_w, f_c) * (1 - seg01(f, f_c + 3, f_t))
    for f in range(1, N + 12):
        sq = (1.0 - 0.03 * seg01(f, f_w, f_c) * (1 - seg01(f, f_c, f_c + 4)), 1.0, 1.0)
        sofa_key(S, sofa, f, s=s_of(f), sq=sq)
    for f in range(1, N + 12):
        yw = lerp(PSI, 360.0 - 22.0, seg01(f, f_t, f_t + 12)); p = push_root(S, a, hl, s_of(f), yaw=PSI, lunge=lunge(f))
        pt = push_root(S, a, hl, s_of(f_t), yaw=PSI, lunge=0.0); u = seg01(f, f_t, f_t + 10)
        S.key(a.root, f, loc=(lerp(p.x, pt.x - 0.18, u), lerp(p.y, pt.y + 0.10, u), 0.0), rot=(0, 0, R(yw)), interp="LINEAR")
    pin_feet(S, a, 1, N + 11, lambda f: 0.0)
    # astilla en la jamba derecha (cuña clara que asoma) y polvo de yeso; la hoja abierta tiembla
    wood = mmat(S, "astilla", (1.0, 0.88, 0.60), 0.6, 0.0, ((1.0, 0.85, 0.5), 0.35))
    sp = S.empty("astilla", (0.03, WY - 0.05, 1.25)); sp.rotation_euler = (R(-20), R(0), R(60))
    box(S, "astilla_a", wood, -0.03, 0.03, -0.55, 0.0, -0.03, 0.03, sp); box(S, "astilla_b", wood, -0.05, 0.0, -0.30, 0.0, -0.08, 0.0, sp)
    S.key(sp, 1, scale=(0, 0, 0), interp="LINEAR"); S.key(sp, f_c - 1, scale=(0, 0, 0), interp="LINEAR"); S.key(sp, f_c + 3, scale=(1.5, 1.5, 1.5), interp="LINEAR"); S.key(sp, f_c + 6, scale=(1.2, 1.2, 1.2), interp="LINEAR")
    S.key(sp, N + 11, scale=(1.2, 1.2, 1.2), interp="LINEAR")
    for f in range(1, N + 12):
        sh = 2.0 * math.sin(f * 3.3) * (math.exp(-0.25 * (f - f_c)) if f >= f_c else 0.0)
        leaf_keys(S, Dr, f, 0.0, ANG_R + sh)
    dust(S, (0.66, WY - 0.12, 0.85), f_c, n=6, r=0.09, seed=1)
    S.cue("huh", f_w - 5, vol=-8); S.cue("creak", f_c - 2, vol=-3); S.cue("clunk", f_c + 1, vol=-3); S.cue("pop", f_c + 3, vol=-6)
    S.cue("hmm", f_t + 4, vol=-7); S.cue("wahwah", f_t + 20, vol=-7)
    S.f = N; a.verify(S.f)
    faces(a, [(1, "enfado", 0.5), (f_w, "enfado", 1.0), (f_c + 2, "sorpresa", 0.8), (f_t, "neutra", 1.0), (f_a + 6, "enfado", 1.0)], N, first_blink=12, every=36)
    cam_keys(S)
    return a


# ------------------------------------------------------------------ nivel 150
def l3(S):
    """150: lo tumba de lado (rueda sobre el respaldo), pasa rozando el marco con chirrido, casi se le cae encima; alivio."""
    P, sofa, Dr = setup(S); leaf_keys(S, Dr, 1, 0.0, ANG_R)
    a = new_man(S, ["Pushing", "Picking Up", "Surprised", "Shrugging"], 0, 0, PSI)
    f_t0, f_t1, f_in0, f_in1, f_wob, f_sur, f_shr = 6, 20, 22, 36, 38, 38, 54
    seg(S, a, "Pushing", 1, f_t0 + 3, start=18, speed=1.3, blend=0)
    seg(S, a, "Picking Up", f_t0, f_sur + 2, start=30, speed=1.6, blend=4)
    seg(S, a, "Surprised", f_sur, f_shr + 2, start=0, speed=1.0, blend=3)
    seg(S, a, "Shrugging", f_shr, None, start=0, speed=1.0, blend=5)
    key_path(S, a, [(1, 0, 0, PSI)], 1, N + 11)
    hl = hand_offset(S, a, (4,))
    def roll_of(f):
        r = 92.0 * seg01(f, f_t0, f_t1)
        if f >= f_wob: t = f - f_wob; r = 92.0 + 34.0 * math.sin(math.pi * min(1.0, t / 8.0)) * (1.0 if t < 8 else 0.0) + (-0 if t < 8 else 0.0)
        if f >= f_wob + 8: t = f - (f_wob + 8); r = 92.0 + 6.0 * damp(t, 0.22, 0.9)
        return r
    def s_of(f): return 0.05 + 0.95 * seg01(f, f_in0, f_in1) if f < f_wob else 1.0
    def dyaw(f):
        t = f - f_wob
        return 12.0 * math.sin(math.pi * min(1.0, t / 8.0)) if 0 <= t < 8 else (4.0 * damp(t - 8, 0.2, 0.8) if t >= 8 else 0.0)
    for f in range(1, N + 12):
        wob = 0.012 * math.sin(f * 2.9) if f < f_t0 else 0.0
        sofa_key(S, sofa, f, s=s_of(f) + wob, roll=roll_of(f), dyaw=dyaw(f))
    for f in range(1, N + 12):
        p = push_root(S, a, hl, s_of(f) if f < f_t0 + 14 else s_of(f_t0 + 14) + 0.0, lunge=0.0)
        back = 0.30 * seg01(f, f_wob - 2, f_wob + 6) * (1 - seg01(f, f_shr - 4, f_shr + 8))
        pt = Vector((p.x, p.y, 0.0)) + U * back
        yw = lerp(PSI, 360.0 - 15.0, seg01(f, f_sur - 2, f_sur + 8))
        S.key(a.root, f, loc=(pt.x, pt.y, 0.0), rot=(0, 0, R(yw)), interp="LINEAR")
    pin_feet(S, a, 1, N + 11, lambda f: 0.0)
    for f in (f_in0 + 3, f_in0 + 9): dust(S, (0.60, WY - 0.10, 0.9), f, n=3, r=0.07, spread=0.10, seed=f)
    S.cue("huh", f_t0 - 2, vol=-8); S.cue("whoosh", f_t0 + 3, vol=-6); S.cue("clunk", f_t1, vol=-4); S.cue("creak", f_in0 + 2, vol=-3); S.cue("creak", f_in0 + 8, vol=-4)
    S.cue("hit", f_in1, vol=-4); S.cue("huh", f_wob - 1, vol=-3); S.cue("boing", f_wob + 4, vol=-5); S.cue("clunk", f_wob + 10, vol=-4); S.cue("hmm", f_shr + 6, vol=-7)
    S.f = N; a.verify(S.f)
    faces(a, [(1, "enfado", 0.5), (f_t0 + 4, "enfado", 1.0), (f_wob - 2, "sorpresa", 1.0), (f_shr - 2, "neutra", 1.0), (f_shr + 8, "feliz", 0.7)], N, first_blink=14, every=38)
    cam_keys(S)
    return a


# ------------------------------------------------------------------ nivel 1200
def l4(S):
    """1200: corre a la hoja abierta, la saca de las bisagras y la apoya contra la pared; el sofa pasa; la puerta queda sin cerrar; mira el hueco."""
    P, sofa, Dr = setup(S); leaf_keys(S, Dr, 1, 0.0, ANG_R)
    a = new_man(S, ["Pushing", "Running", "Picking Up", "Shrugging"], 0, 0, PSI)
    f_r0, f_r1, f_off, f_lean, f_b0, f_b1, f_push, f_shr = 6, 13, 18, 28, 29, 35, 36, 56
    seg(S, a, "Pushing", 1, f_r0 + 2, start=18, speed=1.3, blend=0)
    seg(S, a, "Running", f_r0, f_r1 + 2, start=0, speed=1.0, blend=3, repeat=2)
    seg(S, a, "Picking Up", f_r1, f_lean, start=60, speed=1.2, blend=3)
    seg(S, a, "Running", f_b0, f_b1 + 2, start=0, speed=1.0, blend=3, repeat=2)
    seg(S, a, "Pushing", f_push, f_shr + 4, start=18, speed=1.3, blend=3)
    seg(S, a, "Shrugging", f_shr, None, start=0, speed=1.0, blend=5)
    key_path(S, a, [(1, 0, 0, PSI)], 1, N + 11)
    hl = hand_offset(S, a, (4,))
    p0 = push_root(S, a, hl, 0.02); LEAF = Vector((0.95, WY - 1.35))                # junto al borde libre de la hoja abierta (a su lado)
    pushpos = lambda f: push_root(S, a, hl, s_of(f), lunge=0.0)
    def s_of(f): return 0.02 if f < f_push else 0.02 + 1.33 * seg01(f, f_push + 2, f_push + 16)
    pts = [(1, p0.x, p0.y, PSI), (f_r0, p0.x, p0.y, PSI), (f_r0 + 1, p0.x, p0.y, 70.0), (f_r1, LEAF.x, LEAF.y, 150.0), (f_lean, LEAF.x, LEAF.y, 150.0)]
    pb = push_root(S, a, hl, 0.02)
    pts += [(f_lean + 1, LEAF.x, LEAF.y, 250.0), (f_b1, pb.x, pb.y, PSI), (f_push + 18, push_root(S, a, hl, s_of(f_push + 18)).x, push_root(S, a, hl, s_of(f_push + 18)).y, PSI),
            (f_shr - 2, push_root(S, a, hl, s_of(f_push + 18)).x - 0.1, push_root(S, a, hl, s_of(f_push + 18)).y + 0.05, PSI), (f_shr + 10, push_root(S, a, hl, s_of(f_push + 18)).x - 0.15, push_root(S, a, hl, s_of(f_push + 18)).y, 345.0),
            (N + 11, push_root(S, a, hl, s_of(f_push + 18)).x - 0.15, push_root(S, a, hl, s_of(f_push + 18)).y, 345.0)]
    key_path(S, a, pts, 1, N + 11)
    # empuje en vivo: mientras empuja, sigue el extremo del sofa
    for f in range(f_push, f_push + 20):
        p = pushpos(f); S.key(a.root, f, loc=(p.x, p.y, 0.0), rot=(0, 0, R(PSI)), interp="LINEAR")
    pin_feet(S, a, 1, N + 11, lambda f: 0.0)
    for f in range(1, N + 12): sofa_key(S, sofa, f, s=s_of(f) + (0.01 * math.sin(f * 2.8) if f < f_off else 0.0))
    # la hoja derecha: sale de las bisagras (salto), vuela a la pared y queda apoyada; el hueco ya no se puede cerrar
    hR = Dr["leaves"]["der"]
    for f in range(1, N + 12):
        if f < f_off - 2: ang, pos, tilt = ANG_R, (LW, WY - 0.03, 0.05), 0.0
        elif f < f_off + 2: u = seg01(f, f_off - 2, f_off + 2); ang, pos, tilt = ANG_R, (LW, WY - 0.03, 0.05 + 0.08 * u), 0.0
        else:
            u = seg01(f, f_off + 2, f_lean); ang = lerp(ANG_R, 172.0, u); pos = (lerp(LW, 1.62, u), lerp(WY - 0.03, WY - 0.08, u), lerp(0.13, 0.05, u)); tilt = -5.0 * u
        S.key(hR, f, loc=pos, rot=(R(tilt), 0, R(ang)), interp="LINEAR")
    pin = mmat(S, "pasador", (1.0, 0.72, 0.2), 0.2, 1.0)
    for i, zz in enumerate((0.35, 1.05)):                                      # pasadores de las bisagras que saltan
        o = O(S, "cylinder", "pasador", pin, (LW, WY - 0.07, zz), (0.022, 0.022, 0.07)); S.key(o, 1, loc=(LW, WY - 0.07, zz), scale=(0.022, 0.022, 0.07), interp="LINEAR"); S.key(o, f_off - 3, loc=(LW, WY - 0.07, zz), scale=(0.022, 0.022, 0.07), interp="LINEAR")
        S.key(o, f_off + 8, loc=(LW + 0.25 + 0.1 * i, WY - 0.9, zz + 0.5 + 0.2 * i), rot=(R(200), R(80), 0), scale=(0.022, 0.022, 0.07), interp="LINEAR"); S.key(o, f_off + 9, scale=(0, 0, 0), interp="LINEAR")
    dust(S, (1.05, WY - 0.2, 1.0), f_off, n=5, r=0.09, seed=4)
    S.cue("huh", f_r0 - 2, vol=-8); S.cue("whoosh", f_r0 + 2, vol=-6); S.cue("clunk", f_off - 1, vol=-2); S.cue("pop", f_off, vol=-4); S.cue("creak", f_off + 3, vol=-6)
    S.cue("clunk", f_lean, vol=-3); S.cue("whoosh", f_b0 + 1, vol=-6); S.cue("slide_down", f_push + 4, vol=-6); S.cue("hit", f_push + 17, vol=-6); S.cue("hmm", f_shr + 6, vol=-7); S.cue("wahwah", f_shr + 14, vol=-8)
    S.f = N; a.verify(S.f)
    faces(a, [(1, "enfado", 0.5), (f_r0, "neutra", 1.0), (f_off, "enfado", 0.9), (f_lean + 2, "feliz", 0.8), (f_push + 18, "sorpresa", 0.7), (f_shr + 2, "neutra", 1.0)], N, first_blink=14, every=40)
    cam_keys(S)
    return a


# ------------------------------------------------------------------ nivel 7000
def l5(S):
    """7000: duda (Thinking), corre a la maceta de la hoja fija y la patea; aparece la barra de laton; tira de ella: las dos hojas giran de par en par y
    el sofa pasa sin rozar (ding); celebra (Victory)."""
    P, sofa, Dr = setup(S); leaf_keys(S, Dr, 1, 0.0, ANG_R)
    a = new_man(S, ["Pushing", "Thinking", "Running", "Kicking", "Button Pushing", "Victory"], 0, 0, PSI)
    f_th0, f_r0, f_r1, f_k0, f_kick, f_bar0, f_pull, f_open, f_pass, f_v = 8, 22, 30, 31, 35, 40, 44, 47, 50, 56
    seg(S, a, "Pushing", 1, f_th0 + 2, start=18, speed=1.3, blend=0)
    seg(S, a, "Thinking", f_th0, f_r0 + 2, start=8, speed=1.2, blend=4)
    seg(S, a, "Running", f_r0, f_r1 + 2, start=0, speed=1.0, blend=3, repeat=2)
    seg(S, a, "Kicking", f_k0, f_bar0 + 2, start=6, speed=1.35, blend=3)
    seg(S, a, "Button Pushing", f_bar0, f_open + 8, start=10, speed=1.2, blend=3)
    seg(S, a, "Victory", f_v - 4, None, start=0, speed=1.1, blend=4)
    key_path(S, a, [(1, 0, 0, PSI)], 1, N + 11)
    hl = hand_offset(S, a, (4,))
    p0 = push_root(S, a, hl, 0.02); KICK = Vector((0.05, WY - 1.50)); BAR = Vector((0.04, WY - 1.10)); VIC = Vector((0.00, WY - 1.35))
    pts = [(1, p0.x, p0.y, PSI), (f_th0, p0.x, p0.y, PSI), (f_th0 + 6, p0.x + 0.08, p0.y, 330.0), (f_r0 - 2, p0.x + 0.08, p0.y, 330.0), (f_r0, p0.x + 0.08, p0.y, 245.0),
           (f_r1, KICK.x, KICK.y, 232.0), (f_kick + 4, KICK.x, KICK.y, 232.0), (f_bar0, BAR.x, BAR.y, 212.0), (f_open + 8, BAR.x, BAR.y, 212.0), (f_v, VIC.x, VIC.y, 360.0), (N + 11, VIC.x, VIC.y, 360.0)]
    key_path(S, a, pts, 1, N + 11); pin_feet(S, a, 1, N + 11, lambda f: 0.0)
    # maceta izquierda: patada, sale rodando a la izquierda (ruido grande) y deja ver la barra
    pl = P["pot_l"]; gl = P["grp_l"]
    for f in range(1, N + 12):
        u = seg01(f, f_kick, f_kick + 9); x = -1.75 * u
        S.key(gl, f, loc=(x, 0.18 * u, 0.10 * math.sin(math.pi * min(1.0, u * 2.0))), interp="LINEAR")
        S.key(pl, f, rot=(0, 0, R(20.0 + 110.0 * u)), interp="LINEAR")
    # barra: destello, tira hacia arriba (clunk); luego las dos hojas
    slide, glint = Dr["slide"], Dr["glint"]
    for f in range(1, N + 12):
        u = seg01(f, f_pull, f_pull + 4); S.key(slide, f, loc=(0, 0, 0.30 * u), interp="LINEAR")
        g = seg01(f, f_kick + 6, f_kick + 9) * (1 - seg01(f, f_bar0 + 3, f_bar0 + 8)); S.key(glint, f, scale=(g * 1.4,) * 3, rot=(0, R(60 * g), 0), interp="LINEAR")
    for f in range(1, N + 12):
        u = seg01(f, f_open, f_open + 11); e = u + 0.04 * math.sin(math.pi * u)            # pequeño sobreimpulso
        leaf_keys(S, Dr, f, 160.0 * e, lerp(ANG_R, 160.0, e))
    # sofa: encajado hasta que se abren las hojas; entonces entra sin rozar
    def s_of(f): return 0.02 + 0.013 * math.sin(f * 2.8) * (1 if f < f_th0 else 0) + 1.33 * seg01(f, f_pass, f_pass + 12)
    for f in range(1, N + 12): sofa_key(S, sofa, f, s=s_of(f), dyaw=-3.0 * seg01(f, f_pass - 2, f_pass + 6))
    S.cue("huh", f_th0 - 2, vol=-8); S.cue("hmm", f_th0 + 6, vol=-7); S.cue("huh", f_r0 - 4, vol=-6); S.cue("whoosh", f_r0 + 1, vol=-6)
    S.cue("clunk", f_kick, vol=-1); S.cue("hit", f_kick, vol=-4); S.cue("whoosh", f_kick + 2, vol=-6); S.cue("pop", f_kick + 6, vol=-5)
    S.cue("clunk", f_pull + 1, vol=-1); S.cue("creak", f_open, vol=-5); S.cue("whoosh", f_open + 3, vol=-7)
    S.cue("bell", f_pass + 6, vol=-2); S.cue("tada", f_pass + 7, vol=-3); S.cue("yay", f_v + 2, vol=-5)
    S.f = N; a.verify(S.f)
    faces(a, [(1, "enfado", 0.5), (f_th0 + 6, "neutra", 1.0), (f_r0 - 6, "sorpresa", 0.8), (f_r0 + 4, "neutra", 0.8), (f_kick, "enfado", 0.8), (f_kick + 7, "sorpresa", 1.0),
              (f_pull, "neutra", 1.0), (f_open, "sorpresa", 0.7), (f_pass + 6, "feliz", 1.0)], N, first_blink=14, every=36)
    cam_keys(S)
    return a


LEVELS = [(-300, l1), (-60, l2), (150, l3), (1200, l4), (7000, l5)]
