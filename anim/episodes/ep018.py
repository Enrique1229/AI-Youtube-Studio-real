"""ep018 — Mini-historia: "The Bollard That Went for Pie" (story-021, idea b20261123-3-i05). Plaza urbana (env_real.build_plaza, sin atrezo de suelo)
con una FACHADA de geometría pegada al bolardo: ventana de primer piso abierta (marco, alféizar, contraventanas, maceta) a 2,7 m, con una tarta grande
y humeante en el alféizar. Rótulo fijo arriba: "POV: the bollard wants pie". Un solo ojo en la banda amarilla del bolardo.
  1-46    plano 1 (general): hombre sentado en el bolardo (1 m), tarta humeante en la ventana; el ojo del bolardo mira la tarta (deseo).
  46-102  1.er estirón por anillos telescópicos: se queda corto (la tarta sigue más arriba); pausa: el hombre mira a cámara.
  102-120 el bolardo hace fuerza: tiembla, ojo entornado.
  120-158 2.º estirón: llega al alféizar; el hombre (aferrado) coge la tarta.
  158-196 el bolardo baja con el hombre y la tarta (feliz).
  196-270 REMATE (primer plano, corte): hombre de pie con la tarta, va a morder; la tapa del bolardo se abre como una boca, se inclina y se la come de
          sus manos de un bocado; él mira sus manos vacías (Shrugging); el ojo se cierra satisfecho.
  270-312 general: el bolardo vuelve a mirar a la ventana y aparece OTRA tarta humeante (bucle con el plano 1).
Convenio: yaw 0 mira a cámara (-y); mira hacia (sin yaw, -cos yaw). 24 fps, 312 fotogramas = 13 s."""
import math
import bpy
from mathutils import Vector, Euler
from mixamo import MixamoActor
from klunk_toon import apply as klunk, expression, blink
import env_real

TITLE = "The Bollard That Went for Pie"
CAPTION = "POV: the bollard wants pie"
SPEED = 1.0
ENV = "mesa"
CUSTOM_CAMERA = True

FPS = 24
F_END = 312
BP = Vector((-0.2, 0.4, 0.0))          # pie del bolardo
WY = 1.5                                # cara de la fachada (plano y = WY)
WX = 0.45                               # centro de la ventana
SILL = 2.7                              # cara superior del alféizar
PIE_P = Vector((WX, 1.289, SILL + 0.21))   # tarta apoyada en una tabla inclinada sobre el alféizar (se ve la cara de arriba)
PIE_RX = 50.0
E1, E2 = 0.7, 1.65                      # extensión: 1.er estirón (corto) y 2.º (llega)
LEAN_PIE = Vector((0.57, 0.82))         # dirección de la inclinación hacia la ventana
LEAN_EAT = Vector((0.60, -0.80))        # inclinación hacia el hombre en el remate
MAN_D = Vector((BP.x + 0.88, BP.y - 0.55, 0.0))   # hombre de pie junto al bolardo (remate y final)
YAW_D = -42.0
F_GRAB, F_DESC0, F_DESC1, F_CUT_D, F_CUT_E = 150, 170, 192, 196, 270
F_LID0, F_CHOMP, F_SHRUG = 212, 236, 246


def R(d): return math.radians(d)
def sstep(t): t = max(0.0, min(1.0, t)); return t * t * (3 - 2 * t)
def lerp(a, b, t): return a + (b - a) * t
def seg01(f, a, b): return sstep((f - a) / float(b - a))


# ------------------------------------------------------------------ estados animados
def ext(f):
    """Extensión del bolardo (m). Estirón corto, pausa, fuerza, llega, baja."""
    e = 0.0
    if f < 46: return 0.0
    if f < 104:
        t = (f - 46) / 24.0
        e = E1 * (sstep(min(1.0, t)) + 0.05 * math.sin(min(1.0, max(0.0, (f - 70) / 12.0)) * math.pi) * (1 if f < 82 else 0))
        return e
    if f < 120: return E1 + 0.012 * math.sin(f * 2.2)                    # hace fuerza: tiembla sin avanzar
    if f < 150:
        t = (f - 120) / 22.0
        if t < 1.0: return lerp(E1, E2 + 0.07, sstep(t))
        return lerp(E2 + 0.07, E2, sstep((f - 142) / 8.0))
    if f < F_DESC0: return E2
    if f < F_DESC1:
        t = sstep((f - F_DESC0) / float(F_DESC1 - F_DESC0)); return E2 * (1 - t)
    return 0.0


def lean_pie(f):
    return 0.20 * min(1.0, ext(f) / E2) if f < F_CUT_D else 0.0


def lean_eat(f):
    if f < F_LID0: return 0.0
    if f < F_LID0 + 16: return 0.42 * seg01(f, F_LID0, F_LID0 + 16)
    if f < F_CHOMP - 2: return 0.42
    if f < F_CHOMP + 3: return lerp(0.42, 0.62, seg01(f, F_CHOMP - 2, F_CHOMP + 3))
    if f < F_CHOMP + 18: return lerp(0.62, 0.0, seg01(f, F_CHOMP + 3, F_CHOMP + 18))
    return 0.0


def lid_open(f):
    """Ángulo (grados) de la tapa-boca del bolardo."""
    if f < F_LID0: return 0.0
    if f < F_LID0 + 10: return 100.0 * seg01(f, F_LID0, F_LID0 + 10)
    if f < F_CHOMP - 2: return 100.0 + 3 * math.sin((f - F_LID0) * 0.7)
    if f < F_CHOMP + 2: return lerp(100.0, 0.0, seg01(f, F_CHOMP - 2, F_CHOMP + 2))
    if f < F_CHOMP + 7: return 14.0 * math.sin(math.pi * (f - F_CHOMP - 2) / 5.0)     # rebota al cerrar
    return 0.0


def bulge(f):
    t = f - (F_CHOMP + 3)
    return 0.16 * math.sin(math.pi * t / 10.0) if 0 <= t <= 10 else 0.0


def shake(f):
    return (math.sin(f * 2.3) * 0.5 + math.sin(f * 3.7) * 0.5) if 102 <= f < 122 else 0.0


# mirada del ojo: (fotograma, gx, gz, párpado superior 0-1, inferior 0-1, tamaño del ojo)
GAZE = [(1, 0.55, 0.85, 0.0, 0.0, 1.10), (36, 0.55, 0.85, 0.0, 0.0, 1.25), (46, 0.55, 0.9, 0.0, 0.0, 1.25),
        (72, 0.55, 1.0, 0.0, 0.0, 1.2), (100, 0.6, 1.0, 0.1, 0.0, 1.2), (104, 0.6, 1.0, 0.45, 0.25, 1.15), (120, 0.6, 1.0, 0.5, 0.3, 1.15),
        (123, 0.6, 1.0, 0.0, 0.0, 1.25), (146, 0.5, 0.7, 0.0, 0.0, 1.3), (158, 0.1, -0.6, 0.0, 0.0, 1.15), (190, -0.1, -0.5, 0.4, 0.4, 1.1),
        (F_CUT_D, 0.2, -0.3, 0.0, 0.0, 1.2), (F_LID0 - 2, 0.2, -0.3, 0.0, 0.0, 1.3), (F_CHOMP - 1, 0.3, -0.2, 0.0, 0.0, 1.4),
        (F_CHOMP + 2, 0.0, 0.0, 0.9, 0.9, 1.1), (F_SHRUG + 4, 0.0, 0.0, 0.9, 0.9, 1.1), (262, 0.0, 0.0, 1.0, 1.0, 1.1),
        (267, 0.0, 0.0, 1.0, 1.0, 1.1), (272, 0.3, 0.9, 0.0, 0.0, 1.1), (284, 0.5, 0.9, 0.0, 0.0, 1.2), (300, 0.55, 0.85, 0.0, 0.0, 1.3),
        (312, 0.55, 0.85, 0.0, 0.0, 1.3)]


def gaze(f):
    for (f0, *a), (f1, *b) in zip(GAZE, GAZE[1:]):
        if f0 <= f <= f1:
            t = sstep((f - f0) / float(max(1, f1 - f0))); return [lerp(x, y, t) for x, y in zip(a, b)]
    return list(GAZE[-1][1:])


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
    return O(S, "cube", name, mat, ((x0 + x1) / 2, (y0 + y1) / 2, (z0 + z1) / 2), ((x1 - x0) / 2, (y1 - y0) / 2, (z1 - z0) / 2), parent=parent)


def steam_mat(S, name="vapor"):
    """Vapor: Mix(Transparent, Emission) con alfa = ruido * borde suave."""
    k = "steam_" + name
    if k in S.mats: return S.mats[k]
    m = bpy.data.materials.new(k); m.use_nodes = True; nt = m.node_tree; N, L = nt.nodes, nt.links
    for n in list(N): N.remove(n)
    out = N.new("ShaderNodeOutputMaterial"); mix = N.new("ShaderNodeMixShader"); tr = N.new("ShaderNodeBsdfTransparent"); em = N.new("ShaderNodeEmission")
    em.inputs["Color"].default_value = (0.97, 0.97, 1.0, 1); em.inputs["Strength"].default_value = 1.6
    tc = N.new("ShaderNodeTexCoord"); mp = N.new("ShaderNodeMapping"); mp.inputs["Scale"].default_value = (3.2, 3.2, 2.0)
    nz = N.new("ShaderNodeTexNoise"); nz.inputs["Scale"].default_value = 1.6; nz.inputs["Detail"].default_value = 6.0; nz.inputs["Roughness"].default_value = 0.6
    rp = N.new("ShaderNodeValToRGB"); rp.color_ramp.elements[0].position = 0.28; rp.color_ramp.elements[1].position = 0.70
    lw = N.new("ShaderNodeLayerWeight"); lw.inputs["Blend"].default_value = 0.5
    inv = N.new("ShaderNodeMath"); inv.operation = "SUBTRACT"; inv.inputs[0].default_value = 1.0
    m1 = N.new("ShaderNodeMath"); m1.operation = "MULTIPLY"; m3 = N.new("ShaderNodeMath"); m3.operation = "MULTIPLY"; m3.inputs[1].default_value = 0.6
    L.new(tc.outputs["Generated"], mp.inputs["Vector"]); L.new(mp.outputs["Vector"], nz.inputs["Vector"]); L.new(nz.outputs["Fac"], rp.inputs["Fac"])
    L.new(lw.outputs["Facing"], inv.inputs[1]); L.new(rp.outputs["Color"], m1.inputs[0]); L.new(inv.outputs[0], m1.inputs[1]); L.new(m1.outputs[0], m3.inputs[0])
    L.new(m3.outputs[0], mix.inputs["Fac"]); L.new(tr.outputs[0], mix.inputs[1]); L.new(em.outputs[0], mix.inputs[2]); L.new(mix.outputs[0], out.inputs["Surface"])
    S.mats[k] = m; S._steam_map = getattr(S, "_steam_map", []) + [mp]
    return m


def wall_mat(S):
    """Fachada: textura PBR beige_wall_001 con proyección en caja sobre coordenadas del mundo (sirve para todas las caras)."""
    k = "wall_beige"
    if k in S.mats: return S.mats[k]
    d = env_real.PH / "beige_wall_001"; m = bpy.data.materials.new(k); m.use_nodes = True; N = m.node_tree.nodes; L = m.node_tree.links
    b = N["Principled BSDF"]; geo = N.new("ShaderNodeNewGeometry"); mp = N.new("ShaderNodeMapping"); mp.inputs["Scale"].default_value = (0.5, 0.5, 0.5)
    L.new(geo.outputs["Position"], mp.inputs["Vector"])
    def tex(suffix, cs="sRGB"):
        t = N.new("ShaderNodeTexImage"); t.image = bpy.data.images.load(str(next(iter(sorted(d.glob(f"*_{suffix}_2k.*")))))); t.image.colorspace_settings.name = cs
        t.projection = "BOX"; t.projection_blend = 0.2; L.new(mp.outputs["Vector"], t.inputs["Vector"]); return t
    c = tex("diff"); r = tex("rough", "Non-Color"); n = tex("nor_gl", "Non-Color")
    tint = N.new("ShaderNodeMix"); tint.data_type = "RGBA"; tint.blend_type = "MULTIPLY"; tint.inputs[0].default_value = 1.0; tint.inputs[7].default_value = (1.0, 0.86, 0.62, 1)
    L.new(c.outputs["Color"], tint.inputs[6]); L.new(tint.outputs[2], b.inputs["Base Color"]); L.new(r.outputs["Color"], b.inputs["Roughness"])
    nm = N.new("ShaderNodeNormalMap"); L.new(n.outputs["Color"], nm.inputs["Color"]); L.new(nm.outputs["Normal"], b.inputs["Normal"])
    S.mats[k] = m; return m


# ------------------------------------------------------------------ fachada
def build_facade(S):
    wall = wall_mat(S); white = mmat(S, "marco_blanco", (0.86, 0.85, 0.80), 0.6); green = mmat(S, "contraventana", (0.12, 0.30, 0.22), 0.55)
    dgreen = mmat(S, "contra_oscuro", (0.07, 0.19, 0.14), 0.6); stone = mmat(S, "zocalo", (0.30, 0.27, 0.24), 0.9)
    iron = mmat(S, "hierro_f", (0.03, 0.03, 0.035), 0.5, 0.7); terra = mmat(S, "terracota", (0.62, 0.30, 0.16), 0.8)
    dark = mmat(S, "interior", (0.07, 0.045, 0.035), 0.9); warm = mmat(S, "interior_luz", (0.9, 0.55, 0.22), 0.9, 0.0, ((1.0, 0.55, 0.2), 1.4))
    leaf = mmat(S, "hoja_v", (0.10, 0.32, 0.08), 0.7); red = mmat(S, "geranio", (0.85, 0.07, 0.10), 0.6)
    X0, X1, Z0, Z1, T = -0.20, 1.10, SILL, 4.30, 0.5
    box(S, "muro_izq", wall, -9, X0, WY, WY + T, 0, 9); box(S, "muro_der", wall, X1, 9, WY, WY + T, 0, 9)
    box(S, "muro_bajo", wall, X0, X1, WY, WY + T, 0, Z0); box(S, "muro_alto", wall, X0, X1, WY, WY + T, Z1, 9)
    # habitación: fondo cálido oscuro, techo, estantería con tarros y cortinas
    box(S, "hab_fondo", dark, X0, X1, WY + T, WY + T + 0.05, Z0, Z1); box(S, "hab_suelo", dark, X0, X1, WY + T, WY + 1.8, Z0 - 0.05, Z0)
    box(S, "hab_techo", dark, X0, X1, WY + T, WY + 1.8, Z1, Z1 + 0.05); box(S, "hab_pared_i", dark, X0 - 0.05, X0, WY + T, WY + 1.8, Z0, Z1)
    box(S, "hab_pared_d", dark, X1, X1 + 0.05, WY + T, WY + 1.8, Z0, Z1)
    box(S, "hab_luz", warm, X0 + 0.15, X1 - 0.15, WY + T + 0.04, WY + T + 0.06, Z0 + 0.35, Z1 - 0.35)
    for i, zz in enumerate((Z0 + 0.7, Z0 + 1.2)):
        box(S, "estante", mmat(S, "madera_i", (0.30, 0.17, 0.08), 0.7), X0 + 0.05, X1 - 0.05, WY + T - 0.02, WY + T + 0.3, zz, zz + 0.04)
        for j in range(5):
            O(S, "cylinder", "tarro", mmat(S, "tarro%d" % ((i + j) % 3), [(0.6, 0.1, 0.08), (0.8, 0.55, 0.1), (0.3, 0.45, 0.15)][(i + j) % 3], 0.4),
              (X0 + 0.2 + j * 0.2, WY + T + 0.12, zz + 0.12), (0.055, 0.055, 0.09))
    cur = mmat(S, "cortina", (0.85, 0.80, 0.68), 0.9)
    box(S, "cortina_i", cur, X0, X0 + 0.22, WY + 0.1, WY + 0.17, Z0 + 0.05, Z1 - 0.05); box(S, "cortina_d", cur, X1 - 0.20, X1, WY + 0.1, WY + 0.17, Z0 + 0.05, Z1 - 0.05)
    box(S, "barra_cortina", iron, X0 - 0.03, X1 + 0.03, WY + 0.08, WY + 0.11, Z1 - 0.07, Z1 - 0.045)
    # marco blanco, alféizar con goterón y dintel
    fy0, fy1 = WY - 0.07, WY + 0.2
    box(S, "marco_i", white, X0 - 0.07, X0 + 0.02, fy0, fy1, Z0, Z1); box(S, "marco_d", white, X1 - 0.02, X1 + 0.07, fy0, fy1, Z0, Z1)
    box(S, "marco_s", white, X0 - 0.07, X1 + 0.07, fy0, fy1, Z1 - 0.02, Z1 + 0.09)
    box(S, "dintel", stone, X0 - 0.22, X1 + 0.22, WY - 0.10, WY + 0.2, Z1 + 0.09, Z1 + 0.22)
    box(S, "alfeizar", white, X0 - 0.17, X1 + 0.17, WY - 0.52, WY + 0.2, Z0 - 0.09, Z0); box(S, "alf_goteron", white, X0 - 0.13, X1 + 0.13, WY - 0.50, WY - 0.38, Z0 - 0.17, Z0 - 0.09)
    for sx in (X0 - 0.12, X1 + 0.12): box(S, "alf_ménsula", white, sx - 0.04, sx + 0.04, WY - 0.3, WY, Z0 - 0.38, Z0 - 0.09)
    # hojas de la ventana abiertas hacia dentro
    for sg, xe in ((1, X0 + 0.02), (-1, X1 - 0.02)):
        s = S.empty("hoja_vent", (xe, fy1 - 0.02, (Z0 + Z1) / 2)); s.rotation_euler = (0, 0, R(sg * -70))
        box(S, "hv_marco_s", white, 0, sg * 0.45, 0, 0.05, 0.78, 0.84, s) if False else None
        for (a, b, c, d_) in ((0, sg * 0.55, 0.77, 0.80), (0, sg * 0.55, -0.80, -0.77), (0, sg * 0.03, -0.80, 0.80), (sg * 0.52, sg * 0.55, -0.80, 0.80)):
            xx = sorted((a, b)); box(S, "hv", white, xx[0], xx[1], 0, 0.045, c, d_, s)
    # contraventanas verdes abiertas contra el muro (con lamas)
    for sg, xe in ((-1, X0 - 0.07), (1, X1 + 0.07)):
        xa, xb = (xe - 0.56, xe) if sg < 0 else (xe, xe + 0.56)
        box(S, "contra", green, xa, xb, WY - 0.055, WY - 0.02, Z0 - 0.05, Z1 + 0.09)
        for i in range(14):
            zz = Z0 + 0.02 + i * 0.12; box(S, "lama", dgreen, xa + 0.05, xb - 0.05, WY - 0.075, WY - 0.055, zz, zz + 0.05)
        box(S, "contra_marco", dgreen, xa, xb, WY - 0.07, WY - 0.055, Z0 - 0.05, Z0 + 0.0); box(S, "contra_marco2", dgreen, xa, xb, WY - 0.07, WY - 0.055, Z1 + 0.04, Z1 + 0.09)
        for zz in (Z0 + 0.15, Z1 - 0.1): O(S, "cylinder", "bisagra", iron, ((xa if sg > 0 else xb) + sg * -0.02, WY - 0.03, zz), (0.025, 0.025, 0.05), (R(90), 0, 0))
    # maceta con geranios en el borde derecho del alféizar
    O(S, "cylinder", "maceta", terra, (X1 - 0.12, WY - 0.20, Z0 + 0.10), (0.10, 0.10, 0.10)); O(S, "uv_sphere", "mata", leaf, (X1 - 0.12, WY - 0.20, Z0 + 0.26), (0.17, 0.15, 0.11))
    for i in range(7):
        a = i * 0.9; O(S, "uv_sphere", "flor", red, (X1 - 0.12 + 0.11 * math.cos(a), WY - 0.20 + 0.10 * math.sin(a), Z0 + 0.34 + 0.03 * (i % 3)), (0.045,) * 3)
    for i in range(5):
        O(S, "uv_sphere", "mata", leaf, (X1 - 0.30 + i * 0.05, WY - 0.30 - 0.03 * i, Z0 + 0.04), (0.06, 0.05, 0.04))
    # cornisa, zócalo, puerta, farol, bajante, hiedra, guirnalda
    box(S, "cornisa", stone, -9, 9, WY - 0.10, WY + 0.1, 2.15, 2.30); box(S, "zocalo", stone, -9, 9, WY - 0.06, WY + 0.1, 0, 0.55)
    brown = mmat(S, "puerta", (0.25, 0.13, 0.06), 0.6)
    box(S, "puerta", brown, -2.0, -1.05, WY - 0.05, WY + 0.05, 0, 2.05); box(S, "puerta_marco", white, -2.08, -0.97, WY - 0.08, WY + 0.0, 2.05, 2.18)
    box(S, "escalon", stone, -2.15, -0.9, WY - 0.45, WY - 0.05, 0, 0.12)
    O(S, "uv_sphere", "pomo", mmat(S, "laton", (0.8, 0.6, 0.2), 0.3, 0.9), (-1.2, WY - 0.08, 1.0), (0.04,) * 3)
    pipe = mmat(S, "bajante", (0.18, 0.19, 0.20), 0.5, 0.6)
    O(S, "cylinder", "bajante", pipe, (1.78, WY - 0.06, 3.0), (0.045, 0.045, 3.0))
    for zz in (0.8, 2.0, 3.4, 4.8): O(S, "cylinder", "abrazadera", pipe, (1.78, WY - 0.06, zz), (0.06, 0.06, 0.03))
    O(S, "cylinder", "brazo_farol", iron, (-0.95, WY - 0.2, 3.9), (0.015, 0.015, 0.2), (R(90), 0, 0)); O(S, "cylinder", "farol", warm, (-0.95, WY - 0.42, 3.82), (0.07, 0.07, 0.13))
    O(S, "cone", "farol_tejado", iron, (-0.95, WY - 0.42, 3.99), (0.09, 0.09, 0.05), vertices=12, radius1=1.0, radius2=0.1, depth=2.0)
    for i in range(0, 20):                                   # hiedra por el muro, a la derecha
        a = i * 2.39996; zz = 0.7 + (i * 0.11) % 2.7; xx = 1.55 + 0.25 * math.sin(a) + 0.04 * zz
        O(S, "uv_sphere", "hiedra", leaf, (xx, WY - 0.03, zz), (0.10 + 0.04 * (i % 3), 0.04, 0.08))
    flag_cols = [(0.85, 0.15, 0.1), (0.95, 0.75, 0.1), (0.15, 0.4, 0.75), (0.9, 0.9, 0.85)]
    for i in range(9):                                       # guirnalda de banderines de farol a bajante
        u = (i + 0.5) / 9; xx = lerp(-0.95, 1.78, u); zz = 4.15 - 0.45 * math.sin(math.pi * u) + 0.0
        O(S, "cone", "banderin", mmat(S, "band%d" % (i % 4), flag_cols[i % 4], 0.8), (xx, WY - 0.30 + 0.0, zz - 0.07), (0.07, 0.07, 0.07), (R(180), 0, R(30)),
          vertices=3, radius1=1.0, radius2=0.0, depth=2.0)
    # letrero colgante sin texto (icono de tarta) y focos
    box(S, "letrero", mmat(S, "madera_l", (0.40, 0.22, 0.10), 0.6), 1.35, 1.85, WY - 0.55, WY - 0.50, 3.0, 3.45)
    O(S, "cylinder", "icono_tarta", mmat(S, "icono", (0.85, 0.55, 0.15), 0.5), (1.6, WY - 0.56, 3.22), (0.13, 0.13, 0.01), (R(90), 0, 0))
    O(S, "cylinder", "ménsula_letrero", iron, (1.6, WY - 0.25, 3.5), (0.012, 0.28, 0.012), (R(90), 0, 0))
    box(S, "tabla", mmat(S, "madera_t", (0.50, 0.30, 0.14), 0.6), -0.3, 0.3, -0.008, 0.008, -0.3, 0.3, S.empty("tabla_e", (WX, 1.30, SILL + 0.20))).parent.rotation_euler = (R(PIE_RX), 0, 0)
    # luz cálida desde la habitación
    bpy.ops.object.light_add(type="POINT", location=(WX, WY + 1.2, SILL + 0.9)); L = bpy.context.object; L.data.energy = 250; L.data.color = (1.0, 0.6, 0.28); L.data.shadow_soft_size = 0.4


# ------------------------------------------------------------------ bolardo
def build_bollard(S):
    black = mmat(S, "bolardo_negro", (0.015, 0.015, 0.018), 0.35, 0.2); steel = mmat(S, "bolardo_acero", (0.55, 0.55, 0.57), 0.25, 0.95)
    yel = mmat(S, "bolardo_banda", (0.98, 0.74, 0.03), 0.45); tooth = mmat(S, "diente", (0.95, 0.92, 0.82), 0.35)
    throat = mmat(S, "garganta", (0.35, 0.02, 0.04), 0.5); ring_m = mmat(S, "anillo_tel", (0.07, 0.07, 0.08), 0.3, 0.6)
    white = mmat(S, "ojo_blanco", (0.97, 0.97, 0.95), 0.25); pup = mmat(S, "pupila", (0.0, 0.0, 0.0), 0.15); glint = mmat(S, "brillo", (1, 1, 1), 0.1, 0.0, ((1, 1, 1), 3.0))
    bol = S.empty("bolardo", (BP.x, BP.y, 0))
    O(S, "cylinder", "base", black, (0, 0, 0.10), (0.25, 0.25, 0.10), parent=bol, vertices=48)
    O(S, "cylinder", "base_collar", steel, (0, 0, 0.03), (0.30, 0.30, 0.03), parent=bol, vertices=48)
    O(S, "torus", "base_borde", steel, (0, 0, 0.2), (1, 1, 1), parent=bol, major_radius=0.235, minor_radius=0.018, major_segments=40, minor_segments=8)
    rings = []
    for k, rr in ((1, 0.195), (2, 0.172), (3, 0.150)):
        r = O(S, "cylinder", "anillo", ring_m, (0, 0, 0.0), (rr, rr, 0.45), parent=bol, vertices=40)
        c = O(S, "torus", "collar", steel, (0, 0, 0.2), (1, 1, 1), parent=bol, major_radius=rr + 0.006, minor_radius=0.014, major_segments=40, minor_segments=8)
        rings.append((k, r, c))
    head = S.empty("cabeza_b", (0, 0, 0.2), bol)
    O(S, "cylinder", "cabeza", black, (0, 0, 0.40), (0.30, 0.30, 0.40), parent=head, vertices=48)
    O(S, "cylinder", "banda", yel, (0, 0, 0.60), (0.306, 0.306, 0.17), parent=head, vertices=48)
    O(S, "cylinder", "garganta", throat, (0, 0, 0.792), (0.27, 0.27, 0.004), parent=head, vertices=40)
    for i in range(16):
        a = R(i * 22.5 + 10); O(S, "cone", "diente_b", tooth, (0.27 * math.cos(a), 0.27 * math.sin(a), 0.83), (0.024, 0.024, 0.034), parent=head, vertices=8, radius1=1.0, radius2=0.0, depth=2.0)
    hinge = S.empty("bisagra_tapa", (0, 0.30, 0.81), head)
    O(S, "cylinder", "tapa", black, (0, -0.30, 0.012), (0.31, 0.31, 0.025), parent=hinge, vertices=48)
    O(S, "cylinder", "tapa_borde", steel, (0, -0.30, 0.03), (0.30, 0.30, 0.006), parent=hinge, vertices=48)
    for i in range(16):
        a = R(i * 22.5 + 25); O(S, "cone", "diente_t", tooth, (0.27 * math.cos(a), -0.30 + 0.27 * math.sin(a), -0.04), (0.024, 0.024, 0.034), (R(180), 0, 0), parent=hinge, vertices=8, radius1=1.0, radius2=0.0, depth=2.0)
    # UN ojo grande en la banda
    EZ, EY = 0.60, -0.292
    eye = S.empty("ojo", (0, EY, EZ), head)
    ball = O(S, "uv_sphere", "ojo_bola", white, (0, 0, 0), (0.115, 0.055, 0.115), parent=eye, segments=24, ring_count=12)
    pupil = O(S, "uv_sphere", "pupila", pup, (0, -0.046, 0), (0.058, 0.03, 0.058), parent=eye, segments=20, ring_count=10)
    gl = O(S, "uv_sphere", "brillo", glint, (0.02, -0.07, 0.02), (0.016, 0.01, 0.016), parent=eye, segments=10, ring_count=6)
    lt = O(S, "uv_sphere", "parpado_s", yel, (0, -0.005, 0.25), (0.132, 0.066, 0.132), parent=eye, segments=24, ring_count=12)
    lb = O(S, "uv_sphere", "parpado_i", yel, (0, -0.005, -0.25), (0.132, 0.066, 0.132), parent=eye, segments=24, ring_count=12)
    line = O(S, "uv_sphere", "linea_feliz", pup, (0, -0.074, 0), (0.001, 0.008, 0.010), parent=eye, segments=12, ring_count=6)
    return {"bol": bol, "rings": rings, "head": head, "hinge": hinge, "eye": eye, "ball": ball, "pupil": pupil, "glint": gl, "lt": lt, "lb": lb, "line": line}


# ------------------------------------------------------------------ tarta
def build_pie(S):
    e = S.empty("tarta", (0, 0, -9))
    pew = mmat(S, "peltre", (0.55, 0.55, 0.58), 0.3, 0.9); fill = mmat(S, "relleno", (0.55, 0.03, 0.08), 0.2); gold = mmat(S, "masa", (0.86, 0.55, 0.16), 0.55)
    gold2 = mmat(S, "masa2", (0.72, 0.42, 0.10), 0.6); plate = mmat(S, "plato", (0.92, 0.90, 0.84), 0.3)
    O(S, "cylinder", "plato", plate, (0, 0, 0.01), (0.27, 0.27, 0.012), parent=e, vertices=48)
    O(S, "cylinder", "molde", pew, (0, 0, 0.04), (0.235, 0.235, 0.035), parent=e, vertices=48)
    O(S, "cylinder", "relleno", fill, (0, 0, 0.065), (0.205, 0.205, 0.025), parent=e, vertices=48)
    for d in (-0.13, -0.065, 0.0, 0.065, 0.13):
        c = math.sqrt(0.205 ** 2 - d ** 2)
        O(S, "cube", "tira_x", gold, (0, d, 0.094), (c, 0.022, 0.011), parent=e)
        O(S, "cube", "tira_y", gold2, (d, 0, 0.107), (0.022, c, 0.011), parent=e)
    O(S, "torus", "borde", gold, (0, 0, 0.085), (1, 1, 1), parent=e, major_radius=0.215, minor_radius=0.034, major_segments=48, minor_segments=10)
    return e


def parab(p0, p1, apex_h, u):
    return Vector((lerp(p0.x, p1.x, u), lerp(p0.y, p1.y, u), lerp(p0.z, p1.z, u) + 4 * apex_h * u * (1 - u)))


def hand_mid(S, a, f):
    S.sc.frame_set(f); bpy.context.view_layer.update()
    mw, pb = a.arm.matrix_world, a.arm.pose.bones
    return (mw @ pb[a.pfx + "LeftHand"].head + mw @ pb[a.pfx + "RightHand"].head) / 2


def seg(S, a, clip, f0, f1, start=0, speed=1.0, blend=4, repeat=1):
    S.f = f0
    cl = a.clips[clip]; avail = int((cl.frame_range[1] - cl.frame_range[0] - start) / speed)
    a.play(clip, frames=min(avail * repeat, f1 - f0 + blend), speed=speed, blend=blend, start=max(0, start), repeat=repeat)


# ------------------------------------------------------------------ cámara
SHOT_A = ((0.10, -5.4, 2.02), (0.10, 1.0, 2.02), 50, 6.2)
SHOT_TOP = ((0.35, -4.9, 3.25), (0.30, 1.0, 3.25), 60, 5.6)
SHOT_D = ((0.45, -4.1, 1.62), (0.45, 0.0, 1.50), 50, 4.6)


def cam_set(S, f, loc, tgt, lens, focus):
    S.cam.location = loc; S.cam.keyframe_insert("location", frame=f)
    S.cam.data.lens = lens; S.cam.data.keyframe_insert("lens", frame=f)
    S.cam.data.dof.focus_distance = focus; S.cam.data.dof.keyframe_insert("focus_distance", frame=f)
    S.tgt.location = tgt; S.tgt.keyframe_insert("location", frame=f)


def top_pos(f):
    """Centro de la cara superior de la tapa (donde se sienta el hombre)."""
    L = lean_pie(f); d = LEAN_PIE
    m = Euler((-L * d.y, L * d.x, 0)).to_matrix()
    return Vector((BP.x, BP.y, 0)) + m @ Vector((0, 0, 1.0 + ext(f)))


# ------------------------------------------------------------------ la historia
def l1(S):
    props = env_real.build_plaza(S, rot_deg=20, dress=False)
    S.cam.data.dof.aperture_fstop = 3.2
    build_facade(S)
    # atrezo realista (Poly Haven CC0) en los flancos y la base de la fachada; bien repartido en profundidad
    P = [("planter_box_01", "2k", -1.5, 1.05, 0.78, 4), ("potted_plant_01", "1k", 1.65, 1.0, 1.0, 40), ("utility_box_01", "1k", -2.3, 1.0, 1.4, 0),
         ("wooden_barrels_01", "1k", 2.2, 0.95, 0.95, 10), ("street_lamp_01", "2k", -1.25, -0.2, 4.6, 0), ("planter_box_02", "1k", 1.2, 1.08, 0.8, -8),
         ("plastic_crate_01", "1k", -0.8, 1.05, 0.34, 20), ("wooden_crate_01", "1k", 0.1, 1.05, 0.5, -15), ("fire_hydrant", "1k", -1.3, -1.6, 0.8, 25),
         ("trashbag", "1k", 2.6, 0.3, 0.5, 60), ("cardboard_box_01", "1k", 1.85, 0.7, 0.45, 32), ("metal_trash_can", "2k", -3.3, 0.6, 1.0, 20),
         ("painted_wooden_bench", "1k", 3.4, 0.7, 0.9, 0), ("street_lamp_02", "1k", 3.0, 4.0, 4.8, 180), ("street_lamp_02", "1k", -4.5, 9.0, 4.8, 0)]
    cols = {}
    for (name, res, x, y, h, rot) in P:
        if (name, res) not in cols: cols[(name, res)] = env_real._model(name, res)
        bpy.context.view_layer.update(); env_real._place_fit(S, cols[(name, res)], (x, y, 0.0), h, R(rot))

    bl = build_bollard(S); pie = build_pie(S)
    a = MixamoActor(S, x=0.0, yaw=0.0, use=["Sitting Idle", "Picking Up", "Shrugging", "Head Nod Yes"]); klunk(a)

    # ---- hombre: clips ----
    seg(S, a, "Sitting Idle", 1, F_CUT_D, start=0, speed=1.0, blend=0, repeat=3)
    seg(S, a, "Picking Up", F_CUT_D, 212, start=190, speed=1.0, blend=0)
    seg(S, a, "Head Nod Yes", 212, 232, start=0, speed=1.1, blend=4)
    seg(S, a, "Shrugging", F_SHRUG, F_END, start=0, speed=0.9, blend=4)

    # ---- hombre: posición ----
    def yaw(f):
        if f < 140: return 62.0
        if f < 150: return lerp(62.0, 125.0, seg01(f, 140, 150))
        if f < 160: return 125.0
        if f < 170: return lerp(125.0, 55.0, seg01(f, 160, 170))
        if f < F_CUT_D: return 55.0
        return YAW_D
    def man_pos(f):
        if f < F_CUT_D:
            t = top_pos(f); return Vector((t.x, t.y, t.z - 0.46))
        return MAN_D
    bpy.context.preferences.edit.keyframe_new_interpolation_type = "LINEAR"
    for f in range(1, F_END + 1):
        p = man_pos(f); jx = 0.012 * shake(f) if f < F_CUT_D else 0.0
        S.key(a.root, f, loc=(p.x + jx, p.y, p.z), rot=(0, 0, R(yaw(f) + (4 * shake(f) if f < F_CUT_D else 0))), interp="LINEAR")

    # ---- bolardo ----
    for f in range(1, F_END + 1):
        E = ext(f); L1 = lean_pie(f); L2 = lean_eat(f); d1, d2 = LEAN_PIE, LEAN_EAT
        rx = -(L1 * d1.y + L2 * d2.y) + 0.025 * shake(f); ry = (L1 * d1.x + L2 * d2.x) + 0.02 * shake(f)
        bl["bol"].rotation_euler = (rx, ry, 0.05 * shake(f)); bl["bol"].keyframe_insert("rotation_euler", frame=f)
        for k, r, c in bl["rings"]:
            top = 0.2 + E * k / 3.0
            r.location = (0, 0, top - 0.45); c.location = (0, 0, top)
            r.keyframe_insert("location", frame=f); c.keyframe_insert("location", frame=f)
        h = bl["head"]; b = bulge(f); h.location = (0, 0, 0.2 + E); h.scale = (1 + b, 1 + b, 1 - 0.6 * b)
        h.keyframe_insert("location", frame=f); h.keyframe_insert("scale", frame=f)
        bl["hinge"].rotation_euler = (-R(lid_open(f)), 0, 0); bl["hinge"].keyframe_insert("rotation_euler", frame=f)
        gx, gz, st, sb, wd = gaze(f)
        vib = 0.12 * shake(f)
        bl["ball"].scale = (0.115 * wd, 0.055, 0.115 * wd); bl["ball"].keyframe_insert("scale", frame=f)
        bl["pupil"].location = (0.052 * gx + vib * 0.1, -0.046 * wd, 0.052 * gz); bl["pupil"].scale = (0.058 * (1.0 + 0.2 * (wd - 1.1)), 0.03, 0.058 * (1.0 + 0.2 * (wd - 1.1)))
        bl["glint"].location = (0.052 * gx + 0.02, -0.07 * wd, 0.052 * gz + 0.02)
        for o in (bl["pupil"], bl["glint"]): o.keyframe_insert("location", frame=f)
        bl["pupil"].keyframe_insert("scale", frame=f)
        zs = 0.115 * wd
        for o, cv, sg in ((bl["lt"], st, 1), (bl["lb"], sb, -1)):
            rl = 0.132 * wd; rz = 0.072 * wd; k = (1.0 if cv >= 0.3 else 0.0) + 0.0005
            o.location = (0, -0.005, sg * (zs * (1.0 - cv) + rz))
            o.scale = (rl * k, 0.066 * k, rz * k); o.keyframe_insert("location", frame=f); o.keyframe_insert("scale", frame=f)
        cl = 1.0 if (st > 0.85 and sb > 0.85) else 0.0
        bl["line"].scale = (0.1 * cl + 0.001, 0.008, 0.008 + 0.004 * cl); bl["line"].keyframe_insert("scale", frame=f)
    # sonrisa feliz: línea del ojo cerrado curvada (se queda recta, el parpadeo la lee como ojo cerrado contento)

    # ---- tarta: sobre el alféizar, a las manos, en brazos, a la boca; reaparece al final ----
    for f in range(1, F_END + 1):
        pass
    hp_grab = None
    keys = []
    for f in range(1, F_END + 1):
        sc = 1.0; rot = (R(PIE_RX), 0, 0)
        if f < F_GRAB: p = PIE_P.copy()
        elif f < F_GRAB + 8:
            u = seg01(f, F_GRAB, F_GRAB + 8)
            hp = hand_mid(S, a, F_GRAB + 8); fw = Vector((math.sin(R(yaw(F_GRAB + 8))), -math.cos(R(yaw(F_GRAB + 8))), 0)); tgt = hp + fw * 0.22 + Vector((0, 0, 0.05))
            p = parab(PIE_P, tgt, 0.25, u); rot = (R(PIE_RX * (1 - u)), 0, R(40 * u))
        elif f < F_CHOMP - 4:
            hp = hand_mid(S, a, f); fw = Vector((math.sin(R(yaw(f))), -math.cos(R(yaw(f))), 0)); p = hp + fw * 0.22 + Vector((0, 0, 0.05))
            rot = (0, 0, R(40))
            if f >= F_CUT_D: p = hp + fw * 0.20 + Vector((0, 0, 0.07))
        elif f < F_CHOMP + 3:
            hp = hand_mid(S, a, F_CHOMP - 4); fw = Vector((math.sin(R(YAW_D)), -math.cos(R(YAW_D)), 0)); p0 = hp + fw * 0.20 + Vector((0, 0, 0.07))
            L2 = lean_eat(F_CHOMP + 2); m = Euler((-L2 * LEAN_EAT.y, L2 * LEAN_EAT.x, 0)).to_matrix()
            mouth = Vector((BP.x, BP.y, 0)) + m @ Vector((0, 0, 1.12))
            u = seg01(f, F_CHOMP - 4, F_CHOMP + 3); p = p0.lerp(mouth, u); sc = max(0.05, 1.0 - 0.95 * u ** 2); rot = (0, 0, R(40 + 120 * u))
        elif f < 276: p = Vector((0, 0, -9)); sc = 0.001
        else:
            u = min(1.0, (f - 276) / 10.0); p = PIE_P.copy(); rot = (R(PIE_RX), 0, 0); sc = (1 + 0.15 * math.sin(math.pi * u)) * sstep(u * 1.3) + 0.001
        keys.append((f, p, sc, rot)); pie.location = p; pie.scale = (sc,) * 3; pie.rotation_euler = rot
        for pth in ("location", "scale", "rotation_euler"): pie.keyframe_insert(pth, frame=f)
    # vapor: espiral que sube desde la tarta, donde esté
    pm = steam_mat(S); N = 12; PER = 56
    puffs = [O(S, "uv_sphere", "vapor", pm, (0, 0, -9), (0.001,) * 3, segments=14, ring_count=8) for _ in range(N)]
    pdata = {f: (p, sc) for f, p, sc, rot in keys}
    rise = lambda f: 0.85 if (f < F_GRAB + 6 or f >= 276) else 0.30
    for f in range(1, F_END + 1):
        p, sc = pdata[f]; vis = sstep((sc - 0.5) / 0.5) if sc < 0.99 else 1.0
        for i, q in enumerate(puffs):
            t = ((f / float(PER)) + i / float(N)) % 1.0
            ang = 2 * math.pi * (1.4 * t + i / float(N) * 0.6)
            rr = 0.03 + 0.10 * t; s = (0.12 * math.sin(math.pi * t) ** 0.8 + 0.001) * vis + 0.0005
            q.location = (p.x + rr * math.cos(ang), p.y + rr * math.sin(ang), p.z + 0.12 + rise(f) * t); q.scale = (s, s, s * 0.9)
            q.keyframe_insert("location", frame=f); q.keyframe_insert("scale", frame=f)
    for mp in S._steam_map:
        for f in range(1, F_END + 12, 4):
            mp.inputs["Location"].default_value = (0, 0, -0.06 * f); mp.inputs["Location"].keyframe_insert("default_value", frame=f)

    # ---- palomas (si el plaza las crea) ----
    for b in props["birds"]:
        b.location = (0, 0, -9)

    # ---- sonido ----
    S.cue("creak", 44, vol=-6)
    S.cue("boing", 50, vol=-4); S.cue("whoosh", 52, vol=-10); S.cue("clunk", 72, vol=-8)
    S.cue("huh", 76, vol=-6)
    S.cue("creak", 104, vol=-4); S.cue("creak", 110, vol=-5); S.cue("creak", 116, vol=-5)
    S.cue("boing", 120, vol=-3); S.cue("whoosh", 124, vol=-10); S.cue("clunk", 143, vol=-6)
    S.cue("pop", F_GRAB + 4, vol=-5); S.cue("tada", F_GRAB + 10, vol=-10)
    S.cue("slide_down", F_DESC0, vol=-5); S.cue("clunk", F_DESC1, vol=-5)
    S.cue("creak", F_LID0, vol=-5)
    S.cue("hit", F_CHOMP, vol=-1); S.cue("clunk", F_CHOMP + 2, vol=-3); S.cue("squeak", F_CHOMP + 6, vol=-9)
    S.cue("sigh", F_SHRUG + 6, vol=-6)
    S.cue("pop", 278, vol=-4); S.cue("tada", 282, vol=-10)

    # ---- cara del hombre ----
    expression(a, "neutra", 1, 1.0, ramp=2)
    expression(a, "sorpresa", 46, 1.0, ramp=4); expression(a, "neutra", 90, 1.0, ramp=6); expression(a, "sorpresa", 102, 0.7, ramp=4)
    expression(a, "sorpresa", 124, 1.0, ramp=4); expression(a, "feliz", F_GRAB + 6, 1.0, ramp=4); expression(a, "feliz", F_CUT_D - 2, 0.6, ramp=3)
    expression(a, "feliz", 212, 1.0, ramp=4); expression(a, "sorpresa", F_CHOMP - 1, 1.0, ramp=3); expression(a, "neutra", F_SHRUG + 12, 1.0, ramp=8)
    for f in (30, 80, 140, 200, 262, 300): blink(a, f)

    # ---- cámara ----
    shots = [(1, SHOT_A), (44, SHOT_A), (72, ((0.12, -5.3, 2.45), (0.12, 1.0, 2.45), 50, 6.0)), (118, ((0.12, -5.3, 2.45), (0.12, 1.0, 2.45), 50, 6.0)),
             (146, SHOT_TOP), (168, SHOT_TOP), (F_DESC1, ((0.15, -5.0, 2.2), (0.12, 1.0, 2.2), 55, 5.6)), (F_CUT_D - 1, ((0.12, -5.3, 2.0), (0.12, 1.0, 2.0), 52, 5.8)),
             (F_CUT_D, SHOT_D), (F_CUT_E - 1, SHOT_D), (F_CUT_E, SHOT_A), (F_END, SHOT_A)]
    cuts = {F_CUT_D - 1, F_CUT_E - 1}
    bpy.context.preferences.edit.keyframe_new_interpolation_type = "BEZIER"
    for f, (loc, tg, lens, foc) in shots: cam_set(S, f, loc, tg, lens, foc)
    for idb in (S.cam, S.cam.data, S.tgt):
        for fc in S.fcurves(idb):
            for kp in fc.keyframe_points:
                if int(kp.co[0]) in cuts: kp.interpolation = "CONSTANT"
    S.f = F_END
    a.verify(S.f)
    return a


LEVELS = [(0, l1)]
