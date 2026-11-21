"""ep014 — Cada nivel de IQ intenta que el autobús pare. Calle de las afueras (realista, humano de Mixamo con el protagonista de
dibujo de klunk_toon). Sin río ni muelle: asfalto con líneas, acera, marquesina con banco, poste de BUS STOP y el CUADRO AMARILLO
de PARADA pintado en el asfalto (x 0..3.4, y 1.8..3.3), visible desde el fotograma 1 en todos los niveles.
Autobús azul de 10 m (caja redondeada, ventanas oscuras, ruedas que giran, faros, puertas dobles que se abren). Entra por la izquierda
(+x) y sale por la derecha; frena con ease-out (cuadrática) cuando para. Bocina (horn) cada nivel MÁS CERCA: -20, -14, -8, -3, 0 dB.
-450 saluda al bus que se acerca (ya agitando la mano en el fotograma 1); el bus cruza el cuadro sin frenar (whoosh fuerte + bocina
lejana), el viento lo tumba de espaldas ("oof", golpe), "wahwah";
-80 corre tras el bus (que pasa otra vez sobre el cuadro), lanza un zapato a su trasera (tonk flojo) y se enfada;
120 se planta en mitad de la calzada, el bus frena con un "pssh" largo y bocina a un palmo de su nariz, pero muy lejos del cuadro; tiembla;
900 trepa a la marquesina, salta al techo del bus (clunk grande, bocina cercana) y se va riendo encima, de pie, sin que pare;
5469 piensa, mira el cuadro, camina y se planta en él: el bus frena solo con bocina clara, "pssh" de puertas, "tada" y "yay"."""
import math
import os
import bpy
from mathutils import Vector
from mixamo import MixamoActor
from klunk_toon import apply as klunk, expression, blink   # protagonista fijo del canal (estilo dibujo)

TITLE = "Every IQ Level Stops the Bus"
ONSCREEN = "Every IQ level stops the bus"
ENV = "parque"
CUSTOM_CAMERA = True
LABEL_STYLE = "big"

# ---- geometría (metros). Cámara en la acera mirando a +y; el bus circula hacia +x por el carril y=BUS_Y; las puertas están en su lado -y.
BUS_Y = 4.75
BUS_HL, BUS_HW = 5.0, 1.25                  # medio largo y medio ancho
BUS_ZTOP = 2.95                             # techo plano
DOOR_X = 3.6                                # centro de la puerta delantera respecto al centro del bus
BOX = (0.0, 3.4, 1.8, 3.3)                  # cuadro amarillo de PARADA (x0, x1, y0, y1)
STOP_X = 1.6                                # x del mundo donde queda la puerta cuando el bus para
BUS_STOP_CENTER = STOP_X - DOOR_X           # centro del bus al parar (-2.0)
SH_ROOF_Z = 2.5                             # cara superior del techo de la marquesina


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


def rounded(o, width=0.3, seg=4):
    """Bisela la caja (esquinas redondeadas) y deja liso solo lo pequeño (las caras grandes quedan planas, sin degradados)."""
    for o2 in bpy.context.view_layer.objects: o2.select_set(False)
    bpy.context.view_layer.objects.active = o; o.select_set(True)
    md = o.modifiers.new("bisel", "BEVEL"); md.width = width; md.segments = seg; md.limit_method = "ANGLE"
    bpy.ops.object.modifier_apply(modifier="bisel")
    for p in o.data.polygons: p.use_smooth = p.area < 0.6
    return o


def text(S, name, body, size, mat, loc, rot=(0, 0, 0), parent=None):
    t = bpy.data.curves.new(name, "FONT"); t.body = body; t.size = size; t.extrude = 0.004; t.align_x = "CENTER"; t.align_y = "CENTER"
    to = bpy.data.objects.new(name, t); S.sc.collection.objects.link(to); t.materials.append(mat)
    to.location = loc; to.rotation_euler = rot
    if parent: to.parent = parent
    return to


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


def sstep(t): t = max(0.0, min(1.0, t)); return t * t * (3 - 2 * t)


def cam_to(S, f, pos, tgt, lens, interp="BEZIER"):
    """Clave de cámara: posición, punto de mira y objetivo (la cámara mira siempre a S.tgt)."""
    bpy.context.preferences.edit.keyframe_new_interpolation_type = interp
    S.cam.location = pos; S.cam.data.lens = lens; S.tgt.location = tgt
    S.cam.keyframe_insert("location", frame=f); S.cam.data.keyframe_insert("lens", frame=f); S.tgt.keyframe_insert("location", frame=f)
    S.cam.data.dof.use_dof = True; S.cam.data.dof.focus_object = S.tgt; S.cam.data.dof.aperture_fstop = 4.0


def lift_feet(S, a, f0, f1, floor=-0.01):
    """Pies nunca bajo el suelo: sube la raíz lo que haga falta en cada fotograma (se mide con las claves actuales)."""
    fix = {}
    for f in range(f0, f1 + 1):
        S.sc.frame_set(f); bpy.context.view_layer.update()
        z = min((a.arm.matrix_world @ a.arm.pose.bones[a.pfx + b].head).z for b in ("LeftFoot", "RightFoot"))
        z = min(z, *((a.arm.matrix_world @ a.arm.pose.bones[a.pfx + b].tail).z for b in ("LeftToeBase", "RightToeBase")))
        if z < floor: fix[f] = (a.root.location.copy(), a.root.rotation_euler.z, floor - z)
    for f, (loc, yaw, d) in fix.items():
        S.key(a.root, f, loc=(loc.x, loc.y, loc.z + d), rot=(0, 0, yaw), interp="LINEAR")


def foot_lift(S, a, f):
    return min(bone_pos(S, a, "RightFoot", f, 0.6).z, bone_pos(S, a, "LeftFoot", f, 0.6).z)


def faces(S, a, ev, n_end=None, first_blink=16, every=56):
    """Parpadeos cada 2-3 s (48-66 fotogramas) y una expresión por emoción: ev = [(fotograma, nombre, valor)]."""
    n_end = n_end or S.f
    f = first_blink
    while f < n_end - 6:
        blink(a, f); f += every
    for f, name, v in ev: expression(a, name, f, v, ramp=3)


# ------------------------------------------------------------------ escenario
def tile_mat(S):
    """Baldosas de acera de 50 cm, gris claro, con juntas oscuras, variación de tono y relieve (procedural)."""
    if "m_baldosa" in S.mats: return S.mats["m_baldosa"]
    m = bpy.data.materials.new("baldosa"); m.use_nodes = True; nt = m.node_tree; N = nt.nodes; L = nt.links
    b = N["Principled BSDF"]; b.inputs["Roughness"].default_value = 0.8
    tc = N.new("ShaderNodeTexCoord"); br = N.new("ShaderNodeTexBrick")
    br.offset = 0.0; br.squash = 1.0
    for k, v in (("Scale", 2.0), ("Mortar Size", 0.02), ("Mortar Smooth", 0.15), ("Brick Width", 1.0), ("Row Height", 1.0), ("Bias", 0.0)):
        br.inputs[k].default_value = v
    br.inputs["Color1"].default_value = (0.62, 0.60, 0.56, 1); br.inputs["Color2"].default_value = (0.50, 0.48, 0.45, 1)
    br.inputs["Mortar"].default_value = (0.16, 0.15, 0.14, 1)
    nz = N.new("ShaderNodeTexNoise"); nz.inputs["Scale"].default_value = 16.0; nz.inputs["Detail"].default_value = 6.0
    mx = N.new("ShaderNodeMix"); mx.data_type = "RGBA"; mx.blend_type = "MULTIPLY"; mx.inputs[0].default_value = 0.45
    L.new(tc.outputs["Object"], br.inputs["Vector"]); L.new(tc.outputs["Object"], nz.inputs["Vector"])
    L.new(br.outputs["Color"], mx.inputs[6]); L.new(nz.outputs["Color"], mx.inputs[7]); L.new(mx.outputs[2], b.inputs["Base Color"])
    bp = N.new("ShaderNodeBump"); bp.inputs["Strength"].default_value = 0.3; bp.inputs["Distance"].default_value = 0.02
    L.new(br.outputs["Fac"], bp.inputs["Height"]); L.new(bp.outputs["Normal"], b.inputs["Normal"])
    S.mats["m_baldosa"] = m
    return m


def clear_env(S):
    """Quita del parque el río, el muelle, las orillas, la hierba y los árboles cercanos: solo queda cielo HDRI, luces y árboles lejanos."""
    for o in list(S.sc.objects):
        if o.instance_type == "COLLECTION":
            if o.location.y < 14.0 or abs(o.location.x) < 12.0 and o.location.y < 22.0: bpy.data.objects.remove(o, do_unlink=True)
        elif o.name.startswith(("orilla", "lecho", "agua", "muelle", "prado", "hierba", "suelo_rio")):
            bpy.data.objects.remove(o, do_unlink=True)
    S.water = None
    import env_real
    g = env_real._pbr(S, "aerial_grass_rock", scale=60.0)
    bpy.ops.mesh.primitive_plane_add(size=1, location=(0, 150, -0.03)); fl = bpy.context.object; fl.name = "hierba_lejos"; fl.scale = (500, 400, 1)
    fl.data.materials.append(g)


class W: pass


def build_street(S):
    """Calle de las afueras: acera de baldosas, bordillo, asfalto con líneas, cuadro de parada amarillo, marquesina, banco, poste, casas."""
    clear_env(S)
    tile = tile_mat(S)
    asf = S.pmat("asfalto", [(0.25, (0.045, 0.045, 0.05)), (0.55, (0.09, 0.09, 0.095)), (0.85, (0.15, 0.145, 0.14))], scale=70, rough=0.92, bump=0.5, detail=10)
    kerb = mmat(S, "bordillo", (0.72, 0.71, 0.68), rough=0.8)
    white = mmat(S, "pintura_blanca", (0.88, 0.88, 0.84), rough=0.7)
    yellow = mmat(S, "pintura_amarilla", (1.0, 0.74, 0.0), rough=0.55, emit=(1.0, 0.62, 0.0, 0.35))
    black = mmat(S, "pintura_negra", (0.015, 0.015, 0.018), rough=0.6)
    def slab(name, mat, x0, x1, y0, y1, ztop, th=0.02):
        return box(S, name, mat, (x1 - x0, y1 - y0, th), ((x0 + x1) / 2, (y0 + y1) / 2, ztop - th / 2))
    slab("acera", tile, -60, 60, -14, 1.45, 0.002)
    slab("bordillo", kerb, -60, 60, 1.45, 1.65, 0.03, 0.06)
    slab("calzada", asf, -60, 60, 1.65, 9.2, 0.0)
    slab("acera_lejos", tile, -60, 60, 9.2, 10.6, 0.002)
    seto = S.pmat("seto", [(0.2, (0.03, 0.12, 0.03)), (0.5, (0.07, 0.24, 0.05)), (0.8, (0.12, 0.34, 0.07))], scale=22, rough=0.9, bump=0.9, detail=8)
    box(S, "seto_lejos", seto, (120, 0.9, 1.0), (0, 11.2, 0.5))
    # líneas: raya central discontinua y raya del borde lejano
    for i in range(-14, 15): slab(f"raya{i}", white, i * 3.0 - 0.7, i * 3.0 + 0.7, 6.94, 7.06, 0.004, 0.006)
    slab("raya_borde", white, -60, 60, 8.7, 8.82, 0.004, 0.006)
    # CUADRO DE PARADA: pintura amarilla con "STOP" en negro
    slab("cuadro_parada", yellow, BOX[0], BOX[1], BOX[2], BOX[3], 0.007, 0.01)
    text(S, "stop_txt", "STOP", 0.52, black, (2.55, (BOX[2] + BOX[3]) / 2, 0.0135), (0, 0, 0))
    # marquesina: techo, 4 postes, cristal trasero, barandillas laterales y banco
    frame = mmat(S, "marco", (0.10, 0.11, 0.12), rough=0.4, metal=0.6)
    roof = mmat(S, "techo_marq", (0.82, 0.83, 0.85), rough=0.35, metal=0.3)
    glass = mmat(S, "cristal_marq", (0.70, 0.88, 0.95), rough=0.03, alpha=0.18, spec=1.0)
    box(S, "marq_techo", roof, (2.9, 1.4, 0.1), (-1.65, 0.85, SH_ROOF_Z - 0.05))
    box(S, "marq_borde", frame, (2.9, 0.05, 0.16), (-1.65, 1.55, SH_ROOF_Z - 0.10))
    for nm, x, y in (("p1", -2.95, 0.3), ("p2", -0.25, 0.3), ("p3", -2.95, 1.35), ("p4", -0.25, 1.35)):
        box(S, "marq_" + nm, frame, (0.07, 0.07, 2.4), (x, y, 1.2))
    box(S, "marq_cristal", glass, (2.7, 0.02, 1.9), (-1.6, 0.3, 1.4))
    box(S, "marq_cristal_marco", frame, (2.7, 0.04, 0.05), (-1.6, 0.3, 0.42))
    for k, z in enumerate((0.95, 1.9)):
        box(S, f"marq_barra_der{k}", frame, (0.04, 1.05, 0.04), (-0.25, 0.83, z))
        box(S, f"marq_barra_izq{k}", frame, (0.04, 1.05, 0.04), (-2.95, 0.83, z))
    wood = mmat(S, "banco_madera", (0.45, 0.27, 0.12), rough=0.6)
    box(S, "banco_asiento", wood, (1.7, 0.45, 0.06), (-1.75, 0.80, 0.45))
    box(S, "banco_respaldo", wood, (1.7, 0.05, 0.30), (-1.75, 0.55, 0.78))
    for x in (-2.5, -1.0):
        box(S, "banco_pata", frame, (0.06, 0.40, 0.42), (x, 0.80, 0.21))
        box(S, "banco_apoyo", frame, (0.06, 0.05, 0.40), (x, 0.55, 0.62))
    # poste con la señal de BUS STOP (mira a cámara)
    pole = mmat(S, "poste", (0.55, 0.56, 0.58), rough=0.35, metal=0.8)
    O(S, "cylinder", "poste_bus", pole, (3.9, 1.2, 1.5), (0.04, 0.04, 1.5), vertices=16)
    blue = mmat(S, "senal_azul", (0.03, 0.22, 0.62), rough=0.4)
    box(S, "senal", blue, (0.72, 0.03, 0.52), (3.9, 1.16, 2.62))
    text(S, "senal_txt", "BUS", 0.20, mmat(S, "senal_blanco", (0.95, 0.95, 0.95), rough=0.5), (3.9, 1.13, 2.70), (R(90), 0, 0))
    text(S, "senal_txt2", "STOP", 0.15, mmat(S, "senal_blanco", (0.95, 0.95, 0.95), rough=0.5), (3.9, 1.13, 2.50), (R(90), 0, 0))
    # casas de las afueras al fondo
    cols = [(0.82, 0.74, 0.58), (0.70, 0.45, 0.35), (0.62, 0.72, 0.78), (0.86, 0.80, 0.70), (0.55, 0.62, 0.50)]
    tejado = mmat(S, "tejado", (0.30, 0.12, 0.09), rough=0.8)
    for i, x in enumerate((-18, -9, 0, 9, 18)):
        c = mmat(S, f"casa{i}", cols[i], rough=0.85)
        box(S, f"casa{i}", c, (6.0, 5.0, 3.6 + (i % 2) * 0.6), (x, 16.5, 1.8 + (i % 2) * 0.3))
        O(S, "cone", f"tejado{i}", tejado, (x, 16.5, 4.9 + (i % 2) * 0.6), (4.6, 4.0, 1.5), (0, 0, R(45)), vertices=4, smooth=False)
        box(S, f"puerta{i}", mmat(S, "puerta_casa", (0.25, 0.14, 0.09), rough=0.6), (0.9, 0.05, 2.0), (x, 13.97, 1.0))


def build_bus(S):
    """Autobús: caja redondeada de 10 x 2,5 x ~3 m, azul vivo, ventanas oscuras, ruedas con radios, faros y puertas dobles en el lado -y."""
    b = W(); b.root = S.empty("bus", (-30, BUS_Y, 0)); b.shell = S.empty("bus_carroceria", (0, 0, 0), b.root)
    blue = mmat(S, "bus_azul", (0.02, 0.36, 0.88), rough=0.28, spec=0.7)
    white = mmat(S, "bus_blanco", (0.93, 0.94, 0.95), rough=0.35)
    dark = mmat(S, "bus_negro", (0.015, 0.015, 0.02), rough=0.55)
    glass = mmat(S, "bus_cristal", (0.012, 0.022, 0.04), rough=0.06, spec=1.0)
    amber = mmat(S, "bus_ambar", (1.0, 0.55, 0.05), emit=(1.0, 0.5, 0.04, 3.0))
    sh = b.shell
    body = box(S, "bus_cuerpo", blue, (2 * BUS_HL, 2 * BUS_HW, 2.53), (0, 0, 0.42 + 1.265)); rounded(body, 0.30, 4); body.parent = sh
    box(S, "bus_chasis", dark, (9.4, 2.1, 0.30), (0, 0, 0.45), sh)
    # banda blanca baja y ventanas (lado cercano -y y lado lejano +y)
    for sgn in (-1, 1):
        y = sgn * (BUS_HW + 0.008)
        box(S, f"bus_banda{sgn}", white, (9.4, 0.012, 0.16), (0, y, 1.18), sh)
        for i, (x0, x1) in enumerate(((-4.6, -3.4), (-3.2, -2.0), (-1.8, -0.6), (-0.4, 0.8), (1.0, 2.2), (2.35, 2.9))):
            box(S, f"bus_ventana{sgn}_{i}", glass, (x1 - x0, 0.006, 0.70), ((x0 + x1) / 2, sgn * (BUS_HW + 0.003), 2.20), sh)
    # delante: parabrisas, faros, parachoques y cartel de destino ámbar
    box(S, "bus_parabrisas", glass, (0.012, 1.85, 0.95), (BUS_HL + 0.004, 0, 2.00), sh)
    box(S, "bus_cartel", amber, (0.014, 1.45, 0.20), (BUS_HL + 0.004, 0, 2.56), sh)
    box(S, "bus_parachoques", dark, (0.16, 2.0, 0.26), (BUS_HL - 0.02, 0, 0.62), sh)
    lamp = mmat(S, "bus_faro", (1.0, 0.95, 0.80), emit=(1.0, 0.92, 0.7, 14.0))
    for sy in (-0.78, 0.78): O(S, "uv_sphere", f"bus_faro{sy}", lamp, (BUS_HL, sy, 0.98), (0.07, 0.17, 0.12), parent=sh, segments=16, ring_count=10)
    box(S, "bus_trasera_cristal", glass, (0.012, 1.7, 0.8), (-BUS_HL - 0.004, 0, 2.05), sh)
    tail = mmat(S, "bus_piloto", (1.0, 0.04, 0.03), emit=(1.0, 0.03, 0.02, 4.0))
    for sy in (-0.85, 0.85): box(S, f"bus_piloto{sy}", tail, (0.014, 0.22, 0.30), (-BUS_HL - 0.004, sy, 1.0), sh)
    box(S, "bus_aire", white, (2.4, 1.4, 0.22), (-3.0, 0, BUS_ZTOP + 0.11), sh)
    # interior iluminado tras las puertas (solo se ve cuando se abren) y las dos hojas deslizantes
    box(S, "bus_interior", mmat(S, "bus_luz_int", (1, 0.9, 0.7), emit=(1.0, 0.82, 0.55, 3.0)), (1.05, 0.004, 1.8), (DOOR_X, -BUS_HW - 0.001, 1.65), sh)
    leaf = mmat(S, "bus_hoja", (0.02, 0.05, 0.09), rough=0.08, spec=1.0)
    b.leafs = []
    for sgn in (-1, 1):
        L = box(S, f"bus_hoja{sgn}", leaf, (0.52, 0.04, 1.80), (DOOR_X + sgn * 0.26, -BUS_HW - 0.035, 1.65), sh)
        box(S, f"bus_hoja_marco{sgn}", mmat(S, "bus_marco", (0.9, 0.9, 0.92), rough=0.3), (0.03, 0.05, 1.8), (-sgn * 0.26, -0.004, 0), L)
        b.leafs.append((L, sgn))
    # ruedas (con radios para que se vea que giran) y pasos de rueda
    tire = mmat(S, "bus_neumatico", (0.02, 0.02, 0.022), rough=0.85)
    hub = mmat(S, "bus_llanta", (0.62, 0.64, 0.68), rough=0.3, metal=0.9)
    spoke = mmat(S, "bus_radio", (0.06, 0.06, 0.07), rough=0.5)
    b.wheels = []
    for xw in (3.3, -3.0):
        for sy in (-1, 1):
            w = S.empty(f"bus_rueda{xw}{sy}", (xw, sy * 1.14, 0.5), b.root)
            O(S, "cylinder", "n", tire, (0, 0, 0), (0.5, 0.5, 0.15), (R(90), 0, 0), w, vertices=28)
            O(S, "cylinder", "l", hub, (0, sy * 0.01, 0), (0.30, 0.30, 0.155), (R(90), 0, 0), w, vertices=20)
            for k in range(3):
                bx = box(S, f"r{k}", spoke, (0.52, 0.02, 0.07), (0, sy * 0.16, 0), w, (0, R(60 * k), 0))
            b.wheels.append(w)
            O(S, "cylinder", "arco", dark, (xw, sy * 1.262, 0.58), (0.64, 0.64, 0.012), (R(90), 0, 0), sh, vertices=28)
    S.key(b.root, 1, loc=(-30, BUS_Y, 0), rot=(0, 0, 0))
    return b


def build_set(S):
    build_street(S)
    return build_bus(S)


# ------------------------------------------------------------------ gestos del bus
def drive(S, b, f0, f1, xf, rock=True):
    """Claves por fotograma (lineales): x del centro del bus, giro de ruedas y cabeceo de la carrocería con las frenadas."""
    xs = [xf(f) for f in range(f0, f1 + 1)]
    pitch = 0.0
    for i, f in enumerate(range(f0, f1 + 1)):
        x = xs[i]
        S.key(b.root, f, loc=(x, BUS_Y, 0), rot=(0, 0, 0), interp="LINEAR")
        for wl in b.wheels: S.key(wl, f, rot=(0, x / 0.5, 0), interp="LINEAR")
        dec = (xs[i] - xs[i - 1]) - (xs[i + 1] - xs[i]) if 0 < i < len(xs) - 1 else 0.0
        pitch = 0.6 * pitch + 0.4 * max(-1.0, min(1.0, dec * 70.0))
        S.key(b.shell, f, rot=(0, R(pitch), 0), interp="LINEAR")
    if rock:        # tras parar, la carrocería se balancea y se asienta
        for k in range(1, 16):
            S.key(b.shell, f1 + k, rot=(0, R(-0.7 * math.exp(-k / 5.0) * math.cos(k * 0.9)), 0), interp="LINEAR")


def stop_path(x_stop, v0, T, f_brake):
    """x(f): constante v0 hasta f_brake, frena con ease-out (decelera uniforme) durante T fotogramas y queda en x_stop."""
    xb = x_stop - v0 * T / 2.0
    def xf(f):
        if f <= f_brake: return xb + v0 * (f - f_brake)
        t = min(f - f_brake, T)
        return xb + v0 * t - 0.5 * (v0 / T) * t * t
    return xf


def doors(S, b, f0, f1, open_=True):
    """Puertas dobles que se abren (o se cierran) entre f0 y f1."""
    for L, sgn in b.leafs:
        a_, b_ = (DOOR_X + sgn * 0.26, DOOR_X + sgn * 0.78) if open_ else (DOOR_X + sgn * 0.78, DOOR_X + sgn * 0.26)
        S.key(L, f0, loc=(a_, -BUS_HW - 0.035, 1.65)); S.key(L, f1, loc=(b_, -BUS_HW - 0.035, 1.65))


def shoe_obj(S):
    red = mmat(S, "zapato", (0.70, 0.03, 0.03), rough=0.5); sole = mmat(S, "suela", (0.92, 0.92, 0.9), rough=0.6)
    s = S.empty("zapato", (0, 0, -20))
    box(S, "zap_suela", sole, (0.28, 0.10, 0.04), (0, 0, -0.04), s)
    box(S, "zap_cuerpo", red, (0.26, 0.095, 0.10), (-0.01, 0, 0.03), s)
    box(S, "zap_puntera", red, (0.10, 0.092, 0.07), (0.12, 0, 0.005), s)
    return s


# ------------------------------------------------------------------ auditorías
FINGERS = ("Thumb", "Index", "Middle", "Ring", "Pinky")


def solids_static():
    """(nombre, mín, máx) de lo que no se mueve: marquesina, banco, poste."""
    V = Vector
    return [("techo", V((-3.1, 0.15, 2.4)), V((-0.2, 1.55, 2.5))), ("poste1", V((-2.99, 0.26, 0)), V((-2.91, 0.34, 2.4))),
            ("poste2", V((-0.29, 0.26, 0)), V((-0.21, 0.34, 2.4))), ("poste3", V((-2.99, 1.31, 0)), V((-2.91, 1.39, 2.4))),
            ("poste4", V((-0.29, 1.31, 0)), V((-0.21, 1.39, 2.4))), ("cristal", V((-2.95, 0.28, 0.45)), V((-0.25, 0.32, 2.35))),
            ("banco", V((-2.6, 0.575, 0)), V((-0.9, 1.03, 0.48))), ("respaldo", V((-2.6, 0.52, 0.45)), V((-0.9, 0.58, 0.93))),
            ("barra_der", V((-0.27, 0.3, 0.92)), V((-0.23, 1.35, 0.98))), ("barra_der2", V((-0.27, 0.3, 1.87)), V((-0.23, 1.35, 1.93))),
            ("poste_bus", V((3.86, 1.16, 0)), V((3.94, 1.24, 3.0)))]


def audit(S, a, tag, f0, f1, bus=None, step=2, tol=0.0, ignore=()):
    """Cuerpo (huesos, con grosor) contra el bus (caja del cuerpo + techo), la marquesina, el banco y el poste. Imprime lo que se cruce."""
    if os.environ.get("EP014_NOAUDIT"): return {}
    bad = {}
    for f in range(f0, f1 + 1, step):
        S.sc.frame_set(f); bpy.context.view_layer.update()
        sol = [s for s in solids_static() if s[0] not in ignore]
        if bus is not None:
            bx = bus.root.location.x; V = Vector
            sol.append(("bus", V((bx - BUS_HL, BUS_Y - BUS_HW, 0.40)), V((bx + BUS_HL, BUS_Y + BUS_HW, BUS_ZTOP))))
            sol.append(("bus_aire", V((bx - 4.2, BUS_Y - 0.7, BUS_ZTOP)), V((bx - 1.8, BUS_Y + 0.7, BUS_ZTOP + 0.22))))
        for pb in a.arm.pose.bones:
            n = pb.name.split(":")[-1]
            if any(k in n for k in FINGERS): continue
            r = 0.12 if n in ("Head", "Spine", "Spine1", "Spine2", "Hips", "Neck") else 0.045
            r = max(0.0, r - tol)
            for fr in (0.0, 0.5, 1.0):
                p = a.arm.matrix_world @ (pb.head + (pb.tail - pb.head) * fr)
                for sn, lo, hi in sol:
                    if lo.x - r < p.x < hi.x + r and lo.y - r < p.y < hi.y + r and lo.z - r < p.z < hi.z + r: bad.setdefault((n, sn), []).append(f)
    msg = "limpia (nada atraviesa nada)" if not bad else "; ".join(f"{k[0]} dentro de {k[1]}: f{v[0]}-{v[-1]} ({len(v)})" for k, v in bad.items())
    print(f"AUDITORIA {tag}: {msg}")
    return bad


def audit_feet(S, a, tag, f0, f1, step=3):
    """Altura mínima de los pies (tobillo y punta) en el rango."""
    if os.environ.get("EP014_NOAUDIT"): return
    lo, hi = 9.0, -9.0
    for f in range(f0, f1 + 1, step):
        S.sc.frame_set(f); bpy.context.view_layer.update()
        zs = [(a.arm.matrix_world @ a.arm.pose.bones[a.pfx + b].tail).z for b in ("LeftToeBase", "RightToeBase")]
        zs += [(a.arm.matrix_world @ a.arm.pose.bones[a.pfx + b].head).z - 0.09 for b in ("LeftFoot", "RightFoot")]
        lo = min(lo, min(zs)); hi = max(hi, min(zs))
    print(f"AUDITORIA pies {tag}: z mínima {lo:+.3f} m (suelo en 0; límite -0.03); pie más bajo nunca por encima de {hi:+.3f}")


# ------------------------------------------------------------------ nivel -450
def l1(S):
    """-450: ya saludando con la mano al bus que llega (fotograma 1); el bus cruza el cuadro SIN frenar (whoosh fuerte, bocina lejana);
    el viento lo tumba de espaldas: "oof", golpe y "wahwah"."""
    b = build_set(S)
    cam_to(S, 1, (1.7, -3.1, 1.45), (1.7, 1.2, 1.30), 30)
    xr, yr, f_fall = 0.85, 0.7, 24
    a = MixamoActor(S, x=xr, yaw=292, use=["Waving", "Falling Back Death"]); klunk(a)
    S.f = 1; a.play("Waving", frames=f_fall + 6, speed=0.62, repeat=4, blend=0)
    S.f = f_fall; a.play("Falling Back Death", frames=None, speed=1.25, blend=3, start=0)
    place(S, a, 1, xr, yr, 0, 292); place(S, a, f_fall - 1, xr, yr, 0, 292)
    place(S, a, f_fall + 8, xr + 0.05, yr, 0, 270); place(S, a, f_fall + 30, xr + 0.35, yr, 0, 270)
    lift_feet(S, a, f_fall - 2, f_fall + 52)
    drive(S, b, 1, 52, lambda f: -9.4 + 0.5 * f, rock=False)
    S.cue("horn", 3, vol=-20); S.cue("whoosh", 14, vol=0); S.cue("huh", f_fall - 2, vol=-8)
    S.cue("hit", f_fall + 27, vol=-6); S.cue("oof", f_fall + 25, vol=-6); S.cue("wahwah", f_fall + 52, vol=-8)
    S.f = 112
    a.verify(S.f)
    faces(S, a, [(1, "feliz", 0.9), (f_fall - 3, "sorpresa", 1.0), (f_fall + 32, "enfado", 0.6), (f_fall + 52, "neutra", 1.0)], first_blink=14)
    audit(S, a, "nivel -450", 1, 100, bus=b); audit_feet(S, a, "nivel -450", 1, 60)
    return a


# ------------------------------------------------------------------ nivel -80
def l2(S):
    """-80: corre tras el bus (que acelera por delante del cuadro), le lanza un zapato a la trasera (tonk flojo) y se enfada."""
    b = build_set(S)
    yr = 0.55
    f_thr, f_rel, f_hit = 9, 27, 36
    def run(f):                                           # 0,20 m/f al correr; derrapa mientras lanza
        if f <= f_thr + 1: return -1.3 + 0.20 * (f - 1)
        t = (f - f_thr - 1) / 14.0
        return -1.3 + 0.20 * f_thr + 0.20 * 14.0 * 0.5 * (1 - (1 - min(t, 1.0)) ** 2) * 1.0 + (0.0 if t < 1 else 0.0)
    a = MixamoActor(S, x=-1.3, yaw=90, use=["Running", "Throw", "Angry"]); klunk(a)
    S.f = 1; a.play("Running", frames=f_thr + 6, speed=1.15, repeat=4, blend=0)
    S.f = f_thr; a.play("Throw", frames=48, speed=1.0, blend=4, start=0)
    S.f = 62; a.play("Angry", frames=None, speed=1.0, blend=8, start=0)
    for f in range(1, 62): place(S, a, f, run(f), yr, 0, 90, interp="LINEAR")
    place(S, a, 68, run(61), yr, 0, 40); place(S, a, 82, run(61), yr, 0, 20)
    xb = lambda f: 4.5 + 0.22 * (f - 1) + 0.0016 * (f - 1) ** 2
    drive(S, b, 1, 90, xb, rock=False)
    # zapato: aparece en la mano al armar el brazo, vuela a la trasera y desaparece en el golpe
    sh = shoe_obj(S)
    for f in range(f_thr + 8, f_rel + 1):
        p = bone_pos(S, a, "RightHand", f, 1.0)
        S.key(sh, f, loc=(p.x, p.y - 0.04, p.z), rot=(0, 0, 0), interp="LINEAR")
    x_hit, y_hit = xb(f_hit) - BUS_HL - 0.02, BUS_Y - 1.0
    p0 = bone_pos(S, a, "RightHand", f_rel, 1.0)
    for f in range(f_rel + 1, f_hit + 1):
        t = (f - f_rel) / float(f_hit - f_rel)
        xh = xb(f_hit) - BUS_HL - 0.02
        S.key(sh, f, loc=(p0.x + (xh - p0.x) * t, p0.y + (y_hit - p0.y) * t, p0.z + (1.55 - p0.z) * t + 0.9 * math.sin(math.pi * t)),
              rot=(0, R(560 * t), R(25 * t)), interp="LINEAR")
    for f, hid in ((f_thr + 8, False), (f_hit + 1, True)):
        sh.hide_render = hid; sh.keyframe_insert("hide_render", frame=f)
    sh.hide_render = True; sh.keyframe_insert("hide_render", frame=1)
    sh.hide_render = False; sh.keyframe_insert("hide_render", frame=f_thr + 8)
    # cámara: sigue al corredor con un travelling a la derecha, luego se acerca al enfado
    for f, cx in ((1, 1.9), (24, 4.0), (40, 4.7), (62, 4.7), (100, 4.7)):
        z_t = 1.35
        cam_to(S, f, (cx - 2.0, -3.4, 1.5), (cx + 0.2, 1.4, z_t), 31 if f < 40 else 34, interp="BEZIER")
    S.cue("horn", 5, vol=-14); S.cue("whoosh", 2, vol=-5); S.cue("pop", f_thr + 8, vol=-10)
    S.cue("clunk", f_hit, vol=-12); S.cue("hmm", f_hit + 22, vol=-6)
    S.f = 100
    a.verify(S.f)
    faces(S, a, [(1, "enfado", 0.7), (f_rel - 3, "enfado", 1.0), (f_hit + 3, "sorpresa", 0.8), (f_hit + 14, "enfado", 1.0)], first_blink=12)
    audit(S, a, "nivel -80", 1, 95, bus=b); audit_feet(S, a, "nivel -80", 1, 95)
    return a


# ------------------------------------------------------------------ nivel 120
def l3(S):
    """120: se planta en mitad de la calzada, de cara al bus; el bus frena con un "pssh" largo y bocina a un palmo de su nariz, pero
    se queda lejos del cuadro; él tiembla y por fin mira el cuadro ("wahwah")."""
    b = build_set(S)
    xh, yh = -1.35, BUS_Y
    x_front = xh - 0.40                                   # morro del bus a 40 cm del pecho
    a = MixamoActor(S, x=xh, yaw=300, use=["Looking Around"]); klunk(a)
    S.f = 1; a.play("Looking Around", frames=118, speed=0.9, blend=0, start=0)
    place(S, a, 1, xh, yh, 0, 300)
    f_b = 15; T = 20; v0 = 0.30
    xs = stop_path(x_front - BUS_HL, v0, T, f_b)
    drive(S, b, 1, 70, xs)
    for k in range(0, 34):                                # temblor tras la frenada (cuerpo entero, pequeñas oscilaciones)
        f = f_b + T + 3 + k
        place(S, a, f, xh + 0.012 * math.sin(k * 2.4), yh, 0, 300 + 2.2 * math.sin(k * 2.4 + 1.0), interp="LINEAR")
    place(S, a, f_b + T + 40, xh, yh, 0, 300); place(S, a, 118, xh, yh, 0, 300)
    cam_to(S, 1, (1.2, -0.1, 1.40), (-1.05, 4.75, 1.45), 34)
    cam_to(S, 40, (1.2, -0.1, 1.40), (-1.05, 4.75, 1.50), 34)
    S.cue("horn", f_b - 1, vol=-8); S.cue("huh", f_b + 2, vol=-8); S.cue("door", f_b + T - 2, vol=-6)
    S.cue("hmm", f_b + T + 14, vol=-10); S.cue("wahwah", 92, vol=-8)
    S.f = 112
    a.verify(S.f)
    faces(S, a, [(1, "neutra", 1.0), (f_b - 2, "sorpresa", 1.0), (f_b + T + 16, "sorpresa", 0.7), (90, "enfado", 0.6)], first_blink=40, every=70)
    audit(S, a, "nivel 120", 1, 110, bus=b); audit_feet(S, a, "nivel 120", 1, 110)
    return a


# ------------------------------------------------------------------ nivel 900
def l4(S):
    """900: trepa por el lateral de la marquesina, sube al techo, salta al techo del bus que pasa (clunk grande, bocina cercana) y se va
    riendo, de pie encima, sin que el bus pare."""
    b = build_set(S)
    x_r, y_r = 0.30, 0.83
    a = MixamoActor(S, x=x_r, yaw=270, use=["Climbing Up Wall", "Jumping", "Laughing"]); klunk(a)
    f_c1 = 32                                              # fin de la trepada (el clip llega a su fotograma 37 con las manos en el techo)
    S.f = 1; a.play("Climbing Up Wall", frames=f_c1 + 5, speed=1.2, blend=0, start=0)
    f_v = f_c1 - 2; f_up = f_v + 9                         # trepa al techo (se incorpora) y se prepara
    f_j, sp, j0 = f_up + 6, 1.15, 8                         # despegue
    S.f = f_v; a.play("Jumping", frames=None, speed=sp, blend=5, start=j0)
    f_land = int(f_j + (43 - j0) / sp)
    S.f = f_land + 6; a.play("Laughing", frames=None, speed=1.0, blend=6, start=0)
    # raíz: sube trepando, se encarama al techo (x hacia dentro), salta en +y al techo del bus
    place(S, a, 1, x_r, y_r, 0, 270); place(S, a, f_c1, x_r, y_r, 0, 270)
    roof_x, roof_y = -0.65, 1.0
    place(S, a, f_up, roof_x, roof_y, SH_ROOF_Z, 180)
    place(S, a, f_j, roof_x, roof_y + 0.25, SH_ROOF_Z, 180)
    xc_land = -0.45                                        # centro del bus en el aterrizaje
    x_land, y_land, z_land = xc_land + 1.4, BUS_Y, BUS_ZTOP
    base = foot_lift(S, a, f_land + 3)
    lifts = {f: foot_lift(S, a, f) - base for f in range(f_j, f_land + 1)}
    for f in range(f_j, f_land + 1):
        t = (f - f_j) / float(f_land - f_j)
        zz = SH_ROOF_Z + (z_land - SH_ROOF_Z) * t + 1.05 * math.sin(math.pi * t)
        xk = (roof_x) + (x_land - roof_x) * sstep(t)
        yk = (roof_y + 0.25) + (y_land - roof_y - 0.25) * sstep(t * 1.05)
        place(S, a, f, xk, yk, zz - lifts[f], 180 + 0 * t, interp="LINEAR")
    # tras aterrizar: gira hacia la cámara y va de pie encima del bus (pegado a su techo, sigue su avance)
    v = 0.40
    xcb = lambda f: xc_land + v * (f - f_land)
    for f in range(f_land + 1, f_land + 70):
        yaw = 180 + 180 * sstep((f - f_land) / 10.0)
        place(S, a, f, xcb(f) + 1.4, BUS_Y, z_land, yaw, interp="LINEAR")
    drive(S, b, 1, f_land + 70, lambda f: xc_land + v * (f - f_land), rock=False)
    # cámara: encuadre de la trepada; luego sigue al bus con el que va encima
    cam_to(S, 1, (1.4, -3.0, 1.6), (0.2, 1.0, 2.0), 30)
    cam_to(S, f_up + 4, (1.3, -3.0, 1.7), (0.0, 1.5, 2.6), 30)
    cam_to(S, f_land - 6, (xcb(f_land - 6) + 0.5, -3.0, 1.7), (xcb(f_land - 6) + 1.0, 4.0, 3.0), 36)
    for f in range(f_land + 6, f_land + 70, 6):
        cam_to(S, f, (xcb(f) - 0.2, -3.0, 1.6), (xcb(f) + 1.4, BUS_Y, 3.7), 50, interp="LINEAR")
    S.cue("horn", f_j - 2, vol=-3); S.cue("whoosh", f_land - 8, vol=-6)
    S.cue("hit", f_land, vol=-5); S.cue("clunk", f_land + 1, vol=0); S.cue("laugh", f_land + 14, vol=-5)
    S.f = f_land + 66
    a.verify(S.f)
    faces(S, a, [(1, "enfado", 0.6), (f_up, "neutra", 1.0), (f_j - 2, "sorpresa", 0.7), (f_land + 3, "feliz", 1.0)], first_blink=18)
    audit(S, a, "nivel 900 trepada", 1, f_c1, bus=b, tol=0.04); audit(S, a, "nivel 900 salto y paseo", f_up, f_land + 66, bus=b)
    audit_feet(S, a, "nivel 900 (suelo, solo trepada)", 1, 3)
    return a


# ------------------------------------------------------------------ nivel 5469
def l5(S):
    """5469: piensa (mano en la barbilla), se le ocurre, camina y se planta sobre el cuadro amarillo; el bus frena solo con ease-out y
    bocina clara, "pssh" de las puertas, "tada" y "yay"; se gira a cámara y levanta los brazos."""
    b = build_set(S)
    f_idea, f_walk, f_plant = 34, 38, 66
    x0, y0, x1, y1 = -0.50, 0.95, 1.55, 2.50
    a = MixamoActor(S, x=x0, yaw=15, use=["Thinking", "Walking Left Turn", "Victory"]); klunk(a)
    S.f = 1; a.play("Thinking", frames=f_walk - 1 + 4, speed=1.0, blend=0, start=12)
    S.f = f_walk; a.play("Walking Left Turn", frames=30, speed=1.0, blend=4, start=0)
    S.f = f_plant; a.play("Victory", frames=26, speed=0.03, blend=5, start=0)          # quieto, esperando
    f_stop = 96; T = 26; v0 = 0.45; f_b = f_stop - T
    f_win = f_stop + 6
    S.f = f_win; a.play("Victory", frames=None, speed=1.1, blend=5, start=12)
    place(S, a, 1, x0, y0, 0, 15); place(S, a, f_idea, x0, y0, 0, 15)
    place(S, a, f_idea + 5, x0, y0, 0, 90)                                           # se gira hacia el cuadro (+x)
    n_w = 28
    for k in range(0, n_w + 1):                                                      # un cuarto de arco: +x y luego +y hasta el cuadro
        u = k / float(n_w)
        px = x0 + (x1 - x0) * sstep(u * 1.1) * 0.55 + (x1 - x0) * 0.45 * sstep((u - 0.2) / 0.8)
        py = y0 + (y1 - y0) * sstep((u - 0.35) / 0.65)
        place(S, a, f_walk + 2 + k, px, py, 0, 90, interp="LINEAR")
    f_e = f_walk + 2 + n_w
    place(S, a, f_e, x1, y1, 0, 90, interp="LINEAR"); place(S, a, f_win - 6, x1, y1, 0, 90)
    place(S, a, f_win + 3, x1, y1, 0, 270)                                           # se gira hacia la cámara (y mira al bus)
    place(S, a, f_win + 12, x1, y1, 0, 360); place(S, a, 160, x1, y1, 0, 360)
    xs = stop_path(BUS_STOP_CENTER, v0, T, f_b)
    drive(S, b, 1, f_stop + 20, xs)
    doors(S, b, f_stop + 3, f_stop + 12, True)
    cam_to(S, 1, (1.1, -3.0, 1.45), (1.1, 1.5, 1.30), 30)
    cam_to(S, f_stop, (1.4, -3.0, 1.50), (1.4, 1.5, 1.40), 30)
    S.cue("pop", f_idea, vol=-9); S.cue("whoosh", f_b - 6, vol=-8); S.cue("horn", f_b - 2, vol=0)
    S.cue("door", f_stop + 3, vol=-1); S.cue("tada", f_stop + 11, vol=-5); S.cue("yay", f_stop + 13, vol=-4)
    S.f = f_win + 52
    a.verify(S.f)
    faces(S, a, [(1, "neutra", 1.0), (f_idea - 2, "sorpresa", 1.0), (f_idea + 14, "neutra", 1.0), (f_stop + 8, "feliz", 1.0)], first_blink=10, every=60)
    audit(S, a, "nivel 5469", 1, f_win + 50, bus=b); audit_feet(S, a, "nivel 5469", 1, f_win + 50)
    return a


LEVELS = [(-450, l1), (-80, l2), (120, l3), (900, l4), (5469, l5)]
