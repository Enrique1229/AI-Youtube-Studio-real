"""ep013 — Cada nivel de IQ saca un snack de la máquina expendedora. Rincón pavimentado del parque (realista, humano de Mixamo
con el protagonista de dibujo de klunk_toon). Sin río ni muelle: baldosas, farola, papelera y seto.
Máquina roja con cristal, espirales y bolsas; una bolsa de patatas amarilla CUELGA ladeada de su espiral (con su gemela detrás) y se ve
desde el fotograma 1, igual que la ranura de monedas iluminada en ámbar.
-450 empuja el lateral con ambas manos (ya empujando en el fotograma 1), la máquina ni se mueve, rebota de espaldas (silencio total);
-80 mete el brazo por la trampilla de salida, se le atasca hasta el hombro, tira, duda ("hmm") y se suelta de espaldas ("oof"; "tonk" al golpear);
120 empuja de lado, la bolsa se tambalea y baja medio centímetro (clunk pequeño); se queda mirando sin respirar;
900 salta y cae pesado: la bolsa baja UN escalón y sigue colgada (clunk grande sin premio, "wahwah");
5469 piensa con la moneda brillando en la mano, mete otra moneda, la segunda bolsa empuja a la colgada y caen las dos (doble clunk, "tada", "yay")."""
import math
import bpy
from mathutils import Vector
from mixamo import MixamoActor
from klunk_toon import apply as klunk, expression, blink   # protagonista fijo del canal (estilo dibujo)

TITLE = "Every IQ Level Gets a Snack From the Vending Machine"
ONSCREEN = "Every IQ level gets the snack"
ENV = "parque"
CUSTOM_CAMERA = True
LABEL_STYLE = "big"

# ---- geometría (metros). La máquina mira a la cámara (-y); el centro de su huella está en (MX, MY).
MX, MY = -7.60, 0.95
MW, MD, MH = 1.00, 0.80, 1.90
FRONT_Y = MY - MD / 2                                 # plano frontal (0.55)
X_L, X_R = MX - MW / 2, MX + MW / 2                   # lateral izquierdo (-8.10) y derecho (-7.10)
BAG_X = -0.145                                        # columna central de la ventana (local)
SHELF = (0.72, 1.067, 1.414)                          # cara superior de las baldas (local z)
BAG_Y = -0.19                                         # profundidad de las bolsas (local)
POSE_A = dict(z=0.93, roll=-20.0)                     # bolsa colgada (reposo)
POSE_B = dict(z=0.925, roll=-21.5)                    # tras el empujón del 120 (medio centímetro)
POSE_C = dict(z=0.865, roll=-34.0)                    # tras el salto del 900: baja UN escalón y sigue colgada
BAG_W, BAG_H, BAG_T = 0.155, 0.22, 0.035
COIN_SLOT = Vector((MX + 0.325, FRONT_Y, 1.07))       # centro de la ranura iluminada (mundo)
FLAP_X = MX - 0.29                                   # centro de la trampilla
FLAP_Z = 0.53


def R(d): return math.radians(d)


# ------------------------------------------------------------------ materiales y utilidades
def mmat(S, name, rgb, rough=0.5, metal=0.0, emit=None, alpha=None, spec=None):
    k = "m_" + name
    if k in S.mats: return S.mats[k]
    m = bpy.data.materials.new(k); m.use_nodes = True
    b = m.node_tree.nodes["Principled BSDF"]
    b.inputs["Base Color"].default_value = (*rgb, 1); b.inputs["Roughness"].default_value = rough; b.inputs["Metallic"].default_value = metal
    if spec is not None and "Specular IOR Level" in b.inputs: b.inputs["Specular IOR Level"].default_value = spec
    if emit:
        b.inputs["Emission Color"].default_value = (*emit[:3], 1); b.inputs["Emission Strength"].default_value = emit[3]
    if alpha is not None: b.inputs["Alpha"].default_value = alpha
    S.mats[k] = m
    return m


def box(S, name, mat, dims, loc, parent=None, rot=(0, 0, 0)):
    """Caja con dimensiones reales (escala aplicada)."""
    o = S.obj("cube", name, "white", loc, (dims[0] / 2, dims[1] / 2, dims[2] / 2), rot, None, False)
    o.data.materials[0] = mat
    for o2 in bpy.context.view_layer.objects: o2.select_set(False)
    bpy.context.view_layer.objects.active = o; o.select_set(True)
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    if parent: o.parent = parent
    return o


def O(S, prim, name, mat, loc=(0, 0, 0), scale=(1, 1, 1), rot=(0, 0, 0), parent=None, smooth=True, **kw):
    o = S.obj(prim, name, "white", loc, scale, rot, parent, smooth, **kw); o.data.materials[0] = mat; return o


def bone_pos(S, a, bone, f, frac=0.0):
    S.sc.frame_set(f); bpy.context.view_layer.update()
    pb = a.arm.pose.bones[a.pfx + bone]
    return a.arm.matrix_world @ (pb.head + (pb.tail - pb.head) * frac)


def place(S, a, f, x, y, z=0.0, yaw=0.0, interp="BEZIER"):
    S.key(a.root, f, loc=(x, y, z), rot=(0, 0, R(yaw)), interp=interp)


def seg(S, a, clip, f0, f1=None, start=0, speed=1.0, blend=4, repeat=1):
    S.f = f0
    cl = a.clips[clip]; avail = int((cl.frame_range[1] - cl.frame_range[0] - start) / speed)
    a.play(clip, frames=(min(avail * repeat, f1 - f0 + blend) if f1 is not None else None), speed=speed, blend=blend, start=start, repeat=repeat)


def foot_lift(S, a, f):
    return min(bone_pos(S, a, "RightFoot", f, 0.6).z, bone_pos(S, a, "LeftFoot", f, 0.6).z)


def sstep(t): t = max(0.0, min(1.0, t)); return t * t * (3 - 2 * t)


def cam_static(S, dist=4.1, tz=1.35, cx=-7.0, az=18.0, ch=1.70, lens=30, ty=0.8):
    """Cámara fija algo a la izquierda de la máquina (az grados): se ve el frente de la máquina y la cara del que empuja desde la derecha."""
    S.cam.location = (cx - math.sin(R(az)) * dist, ty - math.cos(R(az)) * dist, ch); S.cam.data.lens = lens; S.tgt.location = (cx, ty, tz)
    S.cam.keyframe_insert("location", frame=1); S.cam.data.keyframe_insert("lens", frame=1); S.tgt.keyframe_insert("location", frame=1)


# ------------------------------------------------------------------ escenario
def tile_mat(S):
    """Baldosas de piedra gris de 45 cm con juntas oscuras, variación de tono y relieve (procedural)."""
    if "m_baldosa" in S.mats: return S.mats["m_baldosa"]
    m = bpy.data.materials.new("baldosa"); m.use_nodes = True; nt = m.node_tree; N = nt.nodes; L = nt.links
    b = N["Principled BSDF"]; b.inputs["Roughness"].default_value = 0.78
    tc = N.new("ShaderNodeTexCoord"); br = N.new("ShaderNodeTexBrick")
    br.offset = 0.0; br.squash = 1.0
    for k, v in (("Scale", 2.2), ("Mortar Size", 0.018), ("Mortar Smooth", 0.15), ("Brick Width", 1.0), ("Row Height", 1.0), ("Bias", 0.0)):
        br.inputs[k].default_value = v
    br.inputs["Color1"].default_value = (0.50, 0.49, 0.46, 1); br.inputs["Color2"].default_value = (0.38, 0.37, 0.35, 1)
    br.inputs["Mortar"].default_value = (0.10, 0.095, 0.09, 1)
    nz = N.new("ShaderNodeTexNoise"); nz.inputs["Scale"].default_value = 18.0; nz.inputs["Detail"].default_value = 6.0
    mx = N.new("ShaderNodeMix"); mx.data_type = "RGBA"; mx.blend_type = "MULTIPLY"; mx.inputs[0].default_value = 0.5
    L.new(tc.outputs["Object"], br.inputs["Vector"]); L.new(tc.outputs["Object"], nz.inputs["Vector"])
    L.new(br.outputs["Color"], mx.inputs[6]); L.new(nz.outputs["Color"], mx.inputs[7]); L.new(mx.outputs[2], b.inputs["Base Color"])
    bp = N.new("ShaderNodeBump"); bp.inputs["Strength"].default_value = 0.35; bp.inputs["Distance"].default_value = 0.02
    L.new(br.outputs["Fac"], bp.inputs["Height"]); L.new(bp.outputs["Normal"], b.inputs["Normal"])
    S.mats["m_baldosa"] = m
    return m


def helix(name, mat, r=0.036, pitch=0.034, length=0.50, wire=0.0034):
    cu = bpy.data.curves.new(name, "CURVE"); cu.dimensions = "3D"; cu.bevel_depth = wire; cu.bevel_resolution = 2; cu.use_fill_caps = True
    turns = length / pitch; n = int(turns * 12)
    sp = cu.splines.new("POLY"); sp.points.add(n)
    for i in range(n + 1):
        t = i / n; ang = t * turns * 2 * math.pi
        sp.points[i].co = (r * math.cos(ang), t * length, r * math.sin(ang), 1)
    cu.materials.append(mat)
    return cu


def clear_env(S):
    """Quita hierba, rocas y troncos de la zona de juego y TAPA el río: no se ve agua ni muelle."""
    for o in list(S.sc.objects):
        if o.instance_type == "COLLECTION" and -14.0 < o.location.x < -3.0 and -8.0 < o.location.y < 9.0:
            keep = "grass" in o.name and o.location.y > 5.5
            if not keep: bpy.data.objects.remove(o, do_unlink=True)
    ref = bpy.data.objects.get("orillaL")
    if getattr(S, "water", None): S.water.hide_render = True; S.water.hide_viewport = True
    dock = bpy.data.objects.get("muelle")
    if dock: dock.hide_render = True
    bpy.ops.mesh.primitive_plane_add(size=1, location=(0, 0, -0.002)); g = bpy.context.object; g.name = "suelo_rio"
    g.scale = (6.0, 400.0, 1.0)
    if ref is not None and ref.type == "MESH" and ref.data.materials: g.data.materials.append(ref.data.materials[0])


class W: pass


def bag(S, name, rgb, label, parent, loc, rot_y=0.0):
    """Bolsa de snack: cuerpo brillante, cierres arriba y abajo y una etiqueta redonda. Origen en el centro."""
    g = S.empty(name, loc, parent); g.rotation_euler = (0, R(rot_y), 0)
    body = mmat(S, "bolsa_" + name.split("_")[0] + str(rgb), rgb, rough=0.30, spec=0.6)
    lab = mmat(S, "etiq_" + str(label), label, rough=0.5)
    cr = mmat(S, "cierre_" + str(rgb), tuple(min(1.0, c * 0.55 + 0.30) for c in rgb), rough=0.4)
    box(S, name + "_cuerpo", body, (BAG_W, BAG_T, BAG_H), (0, 0, 0), parent=g)
    box(S, name + "_cierre_a", cr, (BAG_W, BAG_T * 0.8, 0.018), (0, 0, BAG_H / 2 - 0.007), parent=g)
    box(S, name + "_cierre_b", cr, (BAG_W, BAG_T * 0.8, 0.018), (0, 0, -BAG_H / 2 + 0.007), parent=g)
    O(S, "cylinder", name + "_etiqueta", lab, (0, -BAG_T / 2 - 0.0008, 0.005), (0.046, 0.046, 0.0012), (R(90), 0, 0), g, vertices=20)
    return g


def build_machine(S, w):
    m = w.m = S.empty("maquina", (MX, MY, 0)); m.rotation_euler = (0, 0, 0)
    red = mmat(S, "rojo", (0.50, 0.012, 0.02), rough=0.20, spec=0.8)
    dark = mmat(S, "plastico", (0.022, 0.022, 0.026), rough=0.45)
    gray = mmat(S, "gris_int", (0.30, 0.30, 0.32), rough=0.6)
    inner = mmat(S, "interior", (0.10, 0.10, 0.115), rough=0.7)
    metal = mmat(S, "metal", (0.78, 0.78, 0.80), rough=0.28, metal=1.0)
    white = mmat(S, "cartel", (0.96, 0.96, 0.92), rough=0.4, emit=(1.0, 1.0, 0.95, 1.1))
    # carcasa
    box(S, "zocalo", dark, (0.98, 0.76, 0.18), (0, 0, 0.09), m)
    box(S, "lateral_izq", red, (0.04, 0.80, 1.72), (-0.48, 0, 1.04), m)
    box(S, "lateral_der", red, (0.04, 0.80, 1.72), (0.48, 0, 1.04), m)
    box(S, "trasera", red, (1.0, 0.04, 1.72), (0, 0.38, 1.04), m)
    box(S, "techo", red, (1.0, 0.80, 0.04), (0, 0, 1.88), m)
    # frontal: cartel luminoso arriba, columna de mandos a la derecha, fajas alrededor de ventana y trampilla
    box(S, "cartel", white, (0.92, 0.05, 0.14), (0, -0.385, 1.82), m)
    t = bpy.data.curves.new("txt", "FONT"); t.body = "SNACKS"; t.size = 0.075; t.extrude = 0.003; t.align_x = "CENTER"; t.align_y = "CENTER"
    to = bpy.data.objects.new("SNACKS", t); S.sc.collection.objects.link(to); t.materials.append(red)
    to.parent = m; to.location = (-0.0, -0.4125, 1.82); to.rotation_euler = (R(90), 0, 0)
    box(S, "col_mandos", red, (0.27, 0.04, 1.57), (0.325, -0.38, 0.965), m)
    box(S, "divisor", dark, (0.03, 0.05, 1.04), (0.18, -0.385, 1.235), m)
    for nm, dims, loc in (("faja_baja", (0.63, 0.04, 0.18), (-0.145, -0.38, 0.27)), ("faja_alta", (0.63, 0.04, 0.06), (-0.145, -0.38, 0.69)),
                          ("faja_der", (0.29, 0.04, 0.30), (0.025, -0.38, 0.51))):
        box(S, nm, red, dims, loc, m)
    # interior de la ventana: fondo oscuro, luz superior, baldas, espirales y bolsas
    box(S, "fondo_ventana", inner, (0.63, 0.01, 1.03), (-0.145, 0.34, 1.235), m)
    box(S, "luz_ventana", mmat(S, "luz_int", (1, 1, 1), emit=(1, 1, 0.95, 7.0)), (0.55, 0.03, 0.015), (-0.145, -0.30, 1.735), m)
    cols = (-0.355, -0.145, 0.065)
    coil = helix("espiral", metal)
    pal = [  # fila 0 (abajo), 1, 2: (rgb bolsa, rgb etiqueta) o None = hueco con la espiral vacía
        [((0.10, 0.55, 0.16), (0.95, 0.95, 0.90)), "A", None],
        [((0.12, 0.28, 0.85), (1.0, 0.85, 0.15)), None, ((0.55, 0.12, 0.65), (0.95, 0.95, 0.90))],
        [((0.95, 0.42, 0.04), (0.20, 0.10, 0.05)), ((0.05, 0.60, 0.62), (0.95, 0.95, 0.90)), None]]
    w.spirals = {}
    for k, s_top in enumerate(SHELF):
        box(S, f"balda{k}", gray, (0.63, 0.58, 0.02), (-0.145, 0.05, s_top - 0.01), m)
        for j, cx in enumerate(cols):
            sp = bpy.data.objects.new(f"espiral{k}{j}", coil); S.sc.collection.objects.link(sp); sp.parent = m
            sp.location = (cx, -0.22, s_top + 0.045); w.spirals[(k, j)] = sp
            item = pal[k][j]
            if item is None or item == "A": continue
            bag(S, f"b{k}{j}_bolsa", item[0], item[1], m, (cx, BAG_Y, s_top + 0.09 + BAG_H / 2))
    yellow, red_l = (0.97, 0.78, 0.04), (0.80, 0.07, 0.05)
    w.bag_a = bag(S, "a_patatas", yellow, red_l, m, (BAG_X, BAG_Y, POSE_A["z"]), POSE_A["roll"])       # la colgada
    w.bag_b = bag(S, "b_patatas", yellow, red_l, m, (BAG_X, BAG_Y + 0.075, SHELF[0] + 0.09 + BAG_H / 2))  # su gemela, detrás
    # cristal (alfa) con dos reflejos
    box(S, "cristal", mmat(S, "cristal", (0.75, 0.88, 0.95), rough=0.02, alpha=0.07, spec=1.0), (0.63, 0.006, 1.03), (-0.145, -0.403, 1.235), m)
    refl = mmat(S, "reflejo", (1, 1, 1), emit=(1, 1, 1, 1.0), alpha=0.16)
    box(S, "reflejo1", refl, (0.05, 0.002, 0.95), (-0.31, -0.4068, 1.235), m, rot=(0, R(16), 0))
    box(S, "reflejo2", refl, (0.022, 0.002, 0.95), (-0.21, -0.4068, 1.235), m, rot=(0, R(16), 0))
    # trampilla de salida (humo translúcido, bisagra arriba) y bahía iluminada detrás
    box(S, "bahia_suelo", gray, (0.34, 0.70, 0.02), (-0.29, -0.05, 0.27), m)
    box(S, "bahia_fondo", gray, (0.34, 0.02, 0.40), (-0.29, 0.31, 0.47), m)
    for sx in (-0.455, -0.125): box(S, "bahia_lado", gray, (0.01, 0.70, 0.40), (sx, -0.05, 0.47), m)
    box(S, "bahia_luz", mmat(S, "luz_bahia", (1, 1, 1), emit=(1, 1, 0.95, 9.0)), (0.28, 0.25, 0.01), (-0.29, -0.12, 0.665), m)
    w.hinge = S.empty("bisagra", (-0.29, -0.395, 0.66), m)
    box(S, "trampilla", mmat(S, "humo", (0.03, 0.03, 0.035), rough=0.12, alpha=0.42, spec=1.0), (0.34, 0.015, 0.30), (0, 0, -0.155), w.hinge)
    box(S, "asa_trampilla", dark, (0.22, 0.02, 0.02), (0, -0.01, -0.29), w.hinge)
    # mandos: pantalla, teclado, ranura de monedas iluminada (ámbar), lector y devolución
    box(S, "pantalla", dark, (0.16, 0.012, 0.07), (0.325, -0.405, 1.62), m)
    box(S, "pantalla_lcd", mmat(S, "lcd", (0.1, 1.0, 0.25), emit=(0.15, 1.0, 0.3, 2.2)), (0.14, 0.004, 0.05), (0.325, -0.4115, 1.62), m)
    box(S, "teclado", dark, (0.19, 0.012, 0.25), (0.325, -0.405, 1.33), m)
    key = mmat(S, "tecla", (0.82, 0.82, 0.80), rough=0.35)
    for r_, zz in enumerate((1.42, 1.36, 1.30, 1.24)):
        for c_, xx in enumerate((0.27, 0.325, 0.38)):
            O(S, "cylinder", f"tecla{r_}{c_}", key, (xx, -0.413, zz), (0.0125, 0.0125, 0.004), (R(90), 0, 0), m, vertices=14)
    w.slot_pad = box(S, "ranura_pad", mmat(S, "ranura", (1.0, 0.6, 0.08), emit=(1.0, 0.55, 0.05, 5.0)), (0.15, 0.01, 0.11), (0.325, -0.406, 1.06), m)
    box(S, "ranura_corte", dark, (0.06, 0.004, 0.012), (0.325, -0.4128, 1.07), m)
    box(S, "lector", dark, (0.07, 0.012, 0.10), (0.285, -0.405, 0.90), m)
    box(S, "lector_luz", mmat(S, "azul", (0.1, 0.4, 1.0), emit=(0.1, 0.45, 1.0, 3.0)), (0.05, 0.004, 0.012), (0.285, -0.4115, 0.92), m)
    box(S, "devolucion", dark, (0.07, 0.012, 0.045), (0.375, -0.405, 0.87), m)
    return m


def build_set(S):
    w = W(); clear_env(S)
    # suelo: baldosas en un rincón pavimentado, con un bordillo y un seto al fondo
    bpy.ops.mesh.primitive_plane_add(size=1, location=(-8.0, -1.5, 0.004)); fl = bpy.context.object; fl.name = "baldosas"
    fl.scale = (10.0, 12.0, 1.0)
    for o2 in bpy.context.view_layer.objects: o2.select_set(False)
    bpy.context.view_layer.objects.active = fl; fl.select_set(True)
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    fl.data.materials.append(tile_mat(S))
    curb = mmat(S, "bordillo", (0.55, 0.54, 0.51), rough=0.8)
    box(S, "bordillo", curb, (10.0, 0.18, 0.14), (-8.0, 4.50, 0.07))
    hedge = S.pmat("seto", [(0.2, (0.03, 0.12, 0.03)), (0.5, (0.07, 0.24, 0.05)), (0.8, (0.12, 0.34, 0.07))], scale=22, rough=0.9, bump=0.9, detail=8)
    h1 = box(S, "seto", hedge, (10.0, 0.9, 0.95), (-8.0, 5.15, 0.475)); h1.data.materials[0] = hedge
    build_machine(S, w)
    # farola (detrás, a la izquierda) y papelera (a la derecha, al fondo)
    pole = mmat(S, "farola", (0.025, 0.05, 0.035), rough=0.4, metal=0.7)
    O(S, "cylinder", "farola_base", pole, (-8.70, 2.8, 0.18), (0.11, 0.11, 0.18), parent=None, vertices=20)
    O(S, "cylinder", "farola_poste", pole, (-8.70, 2.8, 1.7), (0.045, 0.045, 1.7), parent=None, vertices=16)
    O(S, "cylinder", "farola_brazo", pole, (-8.55, 2.8, 3.38), (0.025, 0.025, 0.17), rot=(0, R(90), 0), vertices=10)
    O(S, "uv_sphere", "farola_globo", mmat(S, "globo", (1.0, 0.95, 0.8), rough=0.3, emit=(1.0, 0.92, 0.7, 2.0)), (-8.40, 2.8, 3.30), (0.13, 0.13, 0.11), segments=20, ring_count=12)
    bin_m = mmat(S, "papelera", (0.05, 0.22, 0.10), rough=0.45, metal=0.5)
    O(S, "cylinder", "papelera_cuerpo", bin_m, (-8.85, 1.7, 0.42), (0.23, 0.23, 0.42), vertices=28)
    O(S, "cylinder", "papelera_tapa", pole, (-8.85, 1.7, 0.86), (0.25, 0.25, 0.025), vertices=28)
    O(S, "torus", "papelera_aro", pole, (-8.85, 1.7, 0.55), (1, 1, 1), major_radius=0.235, minor_radius=0.012, major_segments=28, minor_segments=6)
    O(S, "cylinder", "papelera_boca", mmat(S, "boca_pap", (0.01, 0.01, 0.01), rough=0.9), (-8.85, 1.7, 0.89), (0.15, 0.06, 0.012), vertices=20)
    # tablilla en el suelo con el hueco para tirar: nada más; las ruedas del suelo ya son baldosas
    S.key(w.m, 1, loc=(MX, MY, 0), rot=(0, 0, 0))
    S.key(w.bag_a, 1, loc=(BAG_X, BAG_Y, POSE_A["z"]), rot=(0, R(POSE_A["roll"]), 0))
    S.key(w.hinge, 1, rot=(0, 0, 0))
    return w


# ------------------------------------------------------------------ gestos del escenario
def bag_pose(S, w, f, pose, interp="BEZIER", y=BAG_Y):
    S.key(w.bag_a, f, loc=(BAG_X, y, pose["z"]), rot=(0, R(pose["roll"]), 0), interp=interp)


def shake_machine(S, w, f0, amp_deg=1.4, n=5, step=3, toward=-1.0):
    """La máquina se bambolea alrededor de su base (amortiguada)."""
    S.key(w.m, f0 - 1, loc=(MX, MY, 0), rot=(0, 0, 0), interp="BEZIER")
    for i in range(n):
        a_ = amp_deg * (0.55 ** i) * (toward if i % 2 == 0 else -toward)
        S.key(w.m, f0 + i * step + 1, loc=(MX, MY, 0), rot=(R(a_ * 0.25), R(a_), 0), interp="BEZIER")
    S.key(w.m, f0 + n * step + 3, loc=(MX, MY, 0), rot=(0, 0, 0), interp="BEZIER")


def add_ik(S, a, side="Right"):
    """Cinemática inversa del brazo (antebrazo + brazo) hacia un objetivo; la influencia se anima con ik_infl."""
    pb = a.arm.pose.bones[a.pfx + side + "ForeArm"]
    t = bpy.data.objects.new("ik_" + side, None); S.sc.collection.objects.link(t)
    c = pb.constraints.new("IK"); c.target = t; c.chain_count = 2; c.use_stretch = False; c.influence = 0.0
    return c, t


def ik_infl(c, f, v):
    c.influence = v; c.keyframe_insert("influence", frame=f)


def ik_to(S, t, f, p, interp="BEZIER"):
    S.key(t, f, loc=tuple(p), interp=interp)


def fit_push(S, a, y0, frames, gap=0.02):
    """Raíz x para que las manos (punta, tramo 1,3 del hueso) no entren nunca en el lateral derecho: la más cercana queda a `gap`."""
    place(S, a, 1, -6.25, y0, 0, 270)
    xm = min(min(bone_pos(S, a, b, f, 1.3).x for b in ("RightHand", "LeftHand")) for f in frames)
    return -6.25 + (X_R + gap - xm)


def faces(S, a, ev, n_end=None, first_blink=16):
    """Parpadeos cada 2-3 s (48-66 fotogramas) y una expresión por emoción: ev = [(fotograma, nombre, valor)]."""
    n_end = n_end or S.f
    f = first_blink
    while f < n_end - 6:
        blink(a, f); f += 56
    for f, name, v in ev: expression(a, name, f, v, ramp=3)


def machine_box(margin=0.0):
    return (X_L - margin, X_R + margin, FRONT_Y - margin, MY + MD / 2 + margin, 0.0, MH)


# ------------------------------------------------------------------ nivel -450
def l1(S):
    """-450: ya empujando el lateral con las dos manos en el fotograma 1; la máquina ni se mueve; empuja más fuerte y rebota de espaldas.
    Silencio total (sin ningún cue)."""
    w = build_set(S); cam_static(S, dist=4.6, cx=-6.9)
    y0 = MY - 0.02
    a = MixamoActor(S, x=-6.25, yaw=270, use=["Pushing", "Falling Back Death"]); klunk(a)
    seg(S, a, "Pushing", 1, 70, start=0, blend=4)
    seg(S, a, "Pushing", 52, 76, start=30, speed=1.7, blend=4)                      # empuja más fuerte
    f_fall = 74
    seg(S, a, "Falling Back Death", f_fall, None, start=0, blend=3)
    place(S, a, 1, -6.25, y0, 0, 270)
    x0 = fit_push(S, a, y0, range(1, 100, 2))                                         # manos a 2 cm del lateral en el punto más cercano del ciclo
    place(S, a, 1, x0, y0, 0, 270); place(S, a, f_fall - 1, x0, y0, 0, 270)
    x1 = x0 + 0.10
    place(S, a, f_fall + 14, x1, y0, 0, 270); place(S, a, f_fall + 26, x1 + 0.05, y0, 0, 270)
    S.f = 128
    a.verify(S.f)
    faces(S, a, [(1, "enfado", 1.0), (f_fall + 1, "sorpresa", 1.0), (f_fall + 34, "enfado", 0.5)], first_blink=22)
    return a


# ------------------------------------------------------------------ nivel -80
def l2(S):
    """-80: de perfil (cara y afro a cámara), inclinado delante de la trampilla, mete el BRAZO IZQUIERDO de lado por ella: queda con el hombro
    pegado a la trampilla; tira dos veces, duda ("hmm") y a la tercera se suelta y cae de espaldas ("oof")."""
    w = build_set(S); cam_static(S, cx=-8.5, az=-12.0, dist=4.4)
    xr, yr = -8.34, 0.19
    a = MixamoActor(S, x=xr, yaw=90, use=["Picking Up", "Falling Back Death", "Looking Around"]); klunk(a)
    ikc, ikt = add_ik(S, a, "Left")
    seg(S, a, "Picking Up", 1, 40, start=22, speed=1.2, blend=4)                       # ya inclinándose en el fotograma 1
    seg(S, a, "Picking Up", 38, 94, start=47, speed=0.05, blend=4)                     # inclinado, casi congelado
    f_rel = 90
    seg(S, a, "Falling Back Death", f_rel, None, start=0, blend=3)
    place(S, a, 1, xr, yr, 0, 90); place(S, a, 30, xr, yr, 0, 90)
    tug = ((44, 0.0), (48, -0.07), (52, 0.0), (62, 0.0), (66, -0.09), (70, 0.0))
    for f, d in tug: place(S, a, f, xr + d, yr, 0, 90, interp="LINEAR")
    place(S, a, 84, xr, yr, 0, 90); place(S, a, f_rel - 1, xr - 0.10, yr - 0.05, 0, 90, interp="LINEAR")
    place(S, a, f_rel + 14, xr - 0.12, yr - 0.80, 0, 90)
    ik_infl(ikc, 1, 0.0); ik_infl(ikc, 12, 0.0); ik_infl(ikc, 28, 1.0); ik_infl(ikc, f_rel - 1, 1.0); ik_infl(ikc, f_rel + 2, 0.0)
    wx = FLAP_X + 0.02
    ik_to(S, ikt, 1, (wx, FRONT_Y - 0.25, 0.55)); ik_to(S, ikt, 12, (wx, FRONT_Y - 0.12, 0.45))
    ik_to(S, ikt, 30, (wx, FRONT_Y + 0.11, FLAP_Z - 0.04)); ik_to(S, ikt, f_rel - 1, (wx, FRONT_Y + 0.11, FLAP_Z - 0.04))
    S.key(w.hinge, 18, rot=(0, 0, 0)); S.key(w.hinge, 30, rot=(R(52), 0, 0)); S.key(w.hinge, f_rel, rot=(R(52), 0, 0))
    S.key(w.hinge, f_rel + 6, rot=(R(-6), 0, 0), interp="BOUNCE"); S.key(w.hinge, f_rel + 14, rot=(0, 0, 0))
    S.cue("hit", 33, vol=-15); S.cue("hit", 47, vol=-16); S.cue("hmm", 56, vol=-8)
    S.cue("oof", f_rel + 18, vol=-6)
    S.f = 134
    a.verify(S.f)
    faces(S, a, [(1, "neutra", 1.0), (30, "enfado", 0.7), (72, "enfado", 1.0), (f_rel + 2, "sorpresa", 1.0), (f_rel + 28, "enfado", 1.0)], first_blink=20)
    return a


# ------------------------------------------------------------------ nivel 120
def l3(S):
    """120: se pone a un lado y empuja con el hombro; la máquina se bambolea, la bolsa se tambalea y baja medio centímetro (clunk pequeño);
    se queda mirando sin respirar (pose congelada, ojos muy abiertos, sin parpadear)."""
    w = build_set(S); cam_static(S)
    y0 = MY - 0.02
    a = MixamoActor(S, x=-6.25, yaw=270, use=["Pushing"]); klunk(a)
    seg(S, a, "Pushing", 1, 54, start=8, blend=4)
    seg(S, a, "Pushing", 52, None, start=40, speed=0.02, blend=5)                      # se queda congelado
    place(S, a, 1, -6.25, y0, 0, 270)
    x0 = fit_push(S, a, y0, range(1, 130, 2))
    place(S, a, 1, x0, y0, 0, 270); place(S, a, 60, x0, y0, 0, 270)
    # máquina y bolsa
    f_c = 42
    shake_machine(S, w, f_c, amp_deg=1.8, n=4, step=3, toward=-1.0)
    bag_pose(S, w, f_c - 3, POSE_A)
    for k, (dz, dr) in enumerate(((0.012, -2.2), (0.0, +1.5), (0.006, -1.0), (0.0, +0.6))):
        S.key(w.bag_a, f_c + 1 + 3 * k, loc=(BAG_X, BAG_Y, POSE_A["z"] - dz - 0.003 * (k > 1)), rot=(0, R(POSE_A["roll"] + dr), 0))
    bag_pose(S, w, f_c + 16, POSE_B)
    S.cue("clunk", f_c + 1, vol=-14); S.cue("huh", f_c + 14, vol=-8)
    S.f = 120
    a.verify(S.f)
    for f in (12,):
        blink(a, f)
    expression(a, "enfado", 1, 0.8, ramp=1); expression(a, "sorpresa", f_c + 12, 1.0, ramp=3)
    return a


# ------------------------------------------------------------------ nivel 900
def l4(S):
    """900: coge carrerilla con el cuerpo y SALTA ENCIMA de la máquina: aterriza pesado en el techo; la máquina retumba y la bolsa baja
    UN escalón, pero sigue colgada (clunk grande sin premio); él mira hacia abajo, se le cae la cara y suena el "wahwah"."""
    w = build_set(S); cam_static(S, dist=5.6, tz=2.45, cx=-7.2, az=12.0, ch=2.3)
    y0 = MY
    x_a, x_b = X_R + 0.65, MX + 0.05                  # salida (a la derecha de la máquina) y techo
    z_roof = MH + 0.03
    a = MixamoActor(S, x=x_a, yaw=270, use=["Jumping", "Angry", "Thinking"]); klunk(a)
    f_jump = 12; sp = 1.15; j0 = 8
    seg(S, a, "Thinking", 1, f_jump + 3, start=0, blend=3)
    seg(S, a, "Jumping", f_jump, 74, start=j0, speed=sp, blend=4)
    f_land = int(f_jump + (43 - j0) / sp)
    seg(S, a, "Angry", 70, None, start=0, blend=8)
    place(S, a, 1, x_a, y0, 0, 270); place(S, a, f_jump, x_a, y0, 0, 270); place(S, a, f_land + 3, x_a, y0, 0, 270)
    base = foot_lift(S, a, f_land + 3)
    lifts = {f: foot_lift(S, a, f) - base for f in range(f_jump, f_land + 1)}
    for f in range(f_jump, f_land + 1):
        t = (f - f_jump) / float(f_land - f_jump)
        want = z_roof * t + 0.85 * math.sin(math.pi * t)
        xk = x_a + (x_b - x_a) * sstep((t - 0.42) / 0.58)
        place(S, a, f, xk, y0, want - lifts[f], 270, interp="LINEAR")
    place(S, a, f_land + 2, x_b, y0, z_roof, 270, interp="LINEAR"); place(S, a, f_land + 70, x_b, y0, z_roof, 270)
    # impacto: el techo retumba y la bolsa baja un escalón (se queda colgada, más ladeada)
    shake_machine(S, w, f_land, amp_deg=2.0, n=5, step=3, toward=-1.0)
    bag_pose(S, w, f_land - 1, POSE_A)
    S.key(w.bag_a, f_land + 2, loc=(BAG_X, BAG_Y, POSE_A["z"] + 0.012), rot=(0, R(POSE_A["roll"] + 3), 0))
    S.key(w.bag_a, f_land + 7, loc=(BAG_X, BAG_Y, POSE_C["z"] - 0.012), rot=(0, R(POSE_C["roll"] - 3), 0))
    S.key(w.bag_a, f_land + 11, loc=(BAG_X, BAG_Y, POSE_C["z"] + 0.006), rot=(0, R(POSE_C["roll"] + 1.5), 0))
    bag_pose(S, w, f_land + 16, POSE_C)
    S.cue("whoosh", f_jump + 2, vol=-12); S.cue("hit", f_land, vol=-6); S.cue("clunk", f_land + 5, vol=-1)
    S.cue("wahwah", f_land + 30, vol=-6)
    S.f = f_land + 84
    a.verify(S.f)
    blink(a, 6); blink(a, f_land + 58); blink(a, f_land + 90)
    expression(a, "feliz", f_jump, 0.8, ramp=1); expression(a, "sorpresa", f_land + 3, 1.0, ramp=3); expression(a, "enfado", f_land + 26, 0.8, ramp=5)
    return a


# ------------------------------------------------------------------ nivel 5469
def l5(S):
    """5469: piensa con la moneda brillando en la mano (mirando a cámara), se le ocurre, mete otra moneda en la ranura iluminada;
    la segunda bolsa empuja a la colgada y caen las dos a la bahía (doble clunk grande); se gira a cámara con los brazos arriba."""
    w = build_set(S); cam_static(S, cx=-7.45, az=20.0)
    xr = COIN_SLOT.x - 0.20; yr = FRONT_Y - 0.48; YC = -22
    a = MixamoActor(S, x=xr, yaw=YC, use=["Thinking", "Victory"]); klunk(a)
    ikc, ikt = add_ik(S, a, "Right")
    seg(S, a, "Thinking", 1, 50, start=12, blend=4)
    f_idea, f_in, f_coin = 46, 62, 66
    seg(S, a, "Thinking", 46, 104, start=60, speed=0.04, blend=4)
    f_win = 96
    seg(S, a, "Victory", f_win, None, start=18, speed=1.2, blend=6)
    # raíz: de cara a cámara pensando -> gira hacia la máquina -> gira otra vez a cámara
    S.key(a.root, 1, loc=(xr, yr, 0), rot=(0, 0, R(YC)), interp="BEZIER")
    S.key(a.root, f_idea, loc=(xr, yr, 0), rot=(0, 0, R(YC)), interp="BEZIER")
    S.key(a.root, f_idea + 9, loc=(xr, yr, 0), rot=(0, 0, R(180)), interp="BEZIER")
    S.key(a.root, f_win - 11, loc=(xr, yr, 0), rot=(0, 0, R(180)), interp="BEZIER")
    S.key(a.root, f_win - 1, loc=(xr, yr, 0), rot=(0, 0, R(YC)), interp="BEZIER")
    # brazo derecho a la ranura
    ik_infl(ikc, 1, 0.0); ik_infl(ikc, f_idea + 6, 0.0); ik_infl(ikc, f_idea + 16, 1.0); ik_infl(ikc, f_win - 8, 1.0); ik_infl(ikc, f_win - 2, 0.0)
    ik_to(S, ikt, f_idea + 6, (COIN_SLOT.x, FRONT_Y - 0.28, COIN_SLOT.z - 0.12)); ik_to(S, ikt, f_in, (COIN_SLOT.x, FRONT_Y - 0.075, COIN_SLOT.z))
    ik_to(S, ikt, f_coin + 3, (COIN_SLOT.x, FRONT_Y - 0.03, COIN_SLOT.z)); ik_to(S, ikt, f_coin + 8, (COIN_SLOT.x + 0.05, FRONT_Y - 0.25, COIN_SLOT.z - 0.15))
    ik_to(S, ikt, f_win - 8, (COIN_SLOT.x + 0.15, FRONT_Y - 0.30, COIN_SLOT.z - 0.45))
    # moneda: en la mano desde el fotograma 1, brillando; desaparece al entrar en la ranura
    gold = mmat(S, "moneda", (1.0, 0.65, 0.05), rough=0.25, metal=0.8, emit=(1.0, 0.6, 0.04, 3.0))
    coin = O(S, "cylinder", "moneda", gold, (0, 0, 0), (0.055, 0.055, 0.007), vertices=24)
    halo = O(S, "uv_sphere", "halo_moneda", mmat(S, "halo", (1.0, 0.6, 0.1), emit=(1.0, 0.55, 0.05, 2.0), alpha=0.18), (0, 0, 0), (0.085, 0.085, 0.085), segments=16, ring_count=10)
    for ob in (coin, halo):
        for f in range(1, f_coin + 1):
            p = bone_pos(S, a, "RightHand", f, 1.0)
            S.key(ob, f, loc=(p.x, p.y - 0.02 if f < f_in else p.y, p.z), interp="LINEAR")
        ob.hide_render = False; ob.keyframe_insert("hide_render", frame=f_coin)
        ob.hide_render = True; ob.keyframe_insert("hide_render", frame=f_coin + 1)
    coin.rotation_euler = (R(90), 0, 0); coin.keyframe_insert("rotation_euler", frame=1)
    # ranura: destello al aceptar la moneda
    pad = w.slot_pad.data.materials[0].node_tree.nodes["Principled BSDF"].inputs["Emission Strength"]
    pad.default_value = 5.0; pad.keyframe_insert("default_value", frame=f_coin - 1)
    pad.default_value = 22.0; pad.keyframe_insert("default_value", frame=f_coin + 2)
    pad.default_value = 5.0; pad.keyframe_insert("default_value", frame=f_coin + 9)
    # la espiral gira y la segunda bolsa avanza; empuja a la colgada y caen las dos a la bahía
    f_sp, f_hit = f_coin + 10, f_coin + 26
    spi = w.spirals[(0, 1)]
    spi.rotation_euler = (0, 0, 0); spi.keyframe_insert("rotation_euler", frame=f_sp)
    spi.rotation_euler = (0, R(360), 0); spi.keyframe_insert("rotation_euler", frame=f_hit)
    bz = SHELF[0] + 0.09 + BAG_H / 2
    S.key(w.bag_b, f_sp, loc=(BAG_X, BAG_Y + 0.075, bz), rot=(0, 0, 0), interp="LINEAR")
    S.key(w.bag_b, f_hit - 3, loc=(BAG_X + 0.02, BAG_Y + 0.02, bz), rot=(0, R(-6), 0), interp="LINEAR")
    S.key(w.bag_b, f_hit, loc=(BAG_X + 0.03, -0.30, bz - 0.01), rot=(0, R(-10), 0), interp="LINEAR")
    S.key(w.bag_a, f_hit - 4, loc=(BAG_X, BAG_Y, POSE_A["z"]), rot=(0, R(POSE_A["roll"]), 0), interp="LINEAR")
    S.key(w.bag_a, f_hit, loc=(BAG_X - 0.01, -0.30, POSE_A["z"] - 0.01), rot=(0, R(POSE_A["roll"] - 6), 0), interp="LINEAR")
    # caída (gravedad) hasta el suelo de la bahía: b primero un poco antes, a encima
    z_floor = 0.28 + BAG_T / 2 + 0.002
    for (bg, fx, zs, yaw0, ex) in ((w.bag_b, f_hit, bz - 0.01, -10, 0.02), (w.bag_a, f_hit, POSE_A["z"] - 0.01, POSE_A["roll"] - 6, -0.0)):
        tf = 9
        for k in range(1, tf + 1):
            t = k / tf; z = zs - (zs - (z_floor + (0.04 if bg is w.bag_a else 0.0))) * t * t
            rr = yaw0 + (-8 - yaw0) * t
            rx = R(90 * t * t) if bg is w.bag_b else R(60 * t * t)
            S.key(bg, fx + k, loc=(BAG_X - 0.145 * t + (0.04 if bg is w.bag_b else -0.04) * t, -0.30 + 0.04 * t, z), rot=(rx, R(rr), 0), interp="LINEAR")
        S.key(bg, fx + tf + 3, loc=(-0.29 + (0.04 if bg is w.bag_b else -0.04), -0.26, z_floor + (0.045 if bg is w.bag_a else 0.0)),
              rot=(R(90 if bg is w.bag_b else 78), R(-4 if bg is w.bag_b else 10), 0), interp="BEZIER")
    # sonido
    S.cue("pop", f_idea, vol=-9); S.cue("pop", f_coin, vol=-8)
    S.cue("clunk", f_hit + 1, vol=-3); S.cue("clunk", f_hit + 10, vol=-1); S.cue("hit", f_hit + 10, vol=-10)
    S.cue("tada", f_hit + 15, vol=-6); S.cue("yay", f_hit + 17, vol=-6)
    S.f = f_hit + 70
    a.verify(S.f)
    f_blink = 8
    blink(a, f_blink); blink(a, 56); blink(a, f_win + 40)
    expression(a, "neutra", 1, 1.0, ramp=1); expression(a, "sorpresa", f_idea - 2, 1.0, ramp=3)
    expression(a, "neutra", f_idea + 14, 1.0, ramp=4); expression(a, "feliz", f_hit + 12, 1.0, ramp=3)
    return a


LEVELS = [(-450, l1), (-80, l2), (120, l3), (900, l4), (5469, l5)]
