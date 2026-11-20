"""klunk_look.py — aspecto propio y fijo del protagonista del canal sobre el personaje de Mixamo (episodios 11+).

    from mixamo import MixamoActor
    from klunk_look import apply
    a = MixamoActor(S, ...); apply(a)

Protagonista: hombre afroamericano con pelo afro (volumen + cientos de rizos pequeños con relieve),
cara y ojos naturales del modelo, y ropa reconocible a primera vista en el móvil: camiseta de rayas horizontales
naranja y crema, pantalón azul marino y zapatillas rojas.
El pelo va pegado al hueso de la cabeza: sigue a cualquier animación de Mixamo sin tocar los clips.
"""
import math, random
import bmesh, bpy
from mathutils import Vector

STRIPE_A = (1.00, 0.42, 0.04)    # naranja
STRIPE_B = (0.95, 0.90, 0.80)    # crema
PANTS = (0.05, 0.08, 0.22)       # azul marino
SHOES = (0.75, 0.05, 0.04)       # rojo
SKIN = (0.30, 0.18, 0.12)        # multiplica la piel clara de Mixamo: tono marrón
SKIN_EVEN = (0.12, 0.068, 0.045)  # tono fijo con el que se iguala (cara y manos del mismo color)


def _base_tex(obj, name, bright):
    """Copia el material del atlas de Mixamo; devuelve (árbol, principled, salida de la textura aclarada o None)."""
    m = obj.data.materials[0].copy(); m.name = name; obj.data.materials[0] = m
    nt = m.node_tree; b = nt.nodes.get("Principled BSDF"); link = b.inputs["Base Color"].links; out = None
    if link:
        out = link[0].from_socket; nt.links.remove(link[0])
        bc = nt.nodes.new("ShaderNodeBrightContrast"); bc.inputs["Bright"].default_value = bright
        nt.links.new(out, bc.inputs["Color"]); out = bc.outputs["Color"]
    return nt, b, out


def _multiply(nt, b, tex_out, color_socket=None, color=None):
    mix = nt.nodes.new("ShaderNodeMix"); mix.data_type = "RGBA"; mix.blend_type = "MULTIPLY"; mix.inputs["Factor"].default_value = 1.0
    if tex_out is not None: nt.links.new(tex_out, mix.inputs[6])
    else: mix.inputs[6].default_value = (1, 1, 1, 1)
    if color_socket is not None: nt.links.new(color_socket, mix.inputs[7])
    else: mix.inputs[7].default_value = (*color, 1)
    nt.links.new(mix.outputs[2], b.inputs["Base Color"])


def _tint(obj, color, name, bright=0.35):
    """Multiplica la textura por un color: conserva pliegues y costuras de la ropa."""
    nt, b, out = _base_tex(obj, name, bright); _multiply(nt, b, out, color=color)
    for k in ("Subsurface Weight", "Subsurface"):                       # la dispersión aclara la piel teñida
        if k in b.inputs: b.inputs[k].default_value = 0.0


def _eye_mask(obj, arm):
    """Atributo 'klunk_piel' = 0 en los ojos y 1 en el resto, para teñir la piel sin teñir los ojos."""
    inv = arm.parent.matrix_world.inverted() if arm.parent else None
    me = obj.data; at = me.color_attributes.get("klunk_piel") or me.color_attributes.new("klunk_piel", "FLOAT_COLOR", "POINT")
    eyes = [Vector((sx * 0.0328, -0.104, 1.6473)) for sx in (1, -1)]
    for v in me.vertices:
        p = obj.matrix_world @ v.co
        if inv: p = inv @ p
        d = min((p - e).length for e in eyes)
        k = 0.0 if d < 0.014 else (1.0 if d > 0.02 else (d - 0.014) / 0.006)
        at.data[v.index].color = (k, k, k, 1)


def _smooth(t, a, b):
    t = max(0.0, min(1.0, (t - a) / (b - a))); return t * t * (3 - 2 * t)


def _beard_mask(obj, arm):
    """Atributo 'klunk_barba': bigote y perilla cortos (0 = piel, 1 = barba), dejando libres los labios."""
    inv = arm.parent.matrix_world.inverted() if arm.parent else None
    me = obj.data; at = me.color_attributes.get("klunk_barba") or me.color_attributes.new("klunk_barba", "FLOAT_COLOR", "POINT")
    for v in me.vertices:
        p = obj.matrix_world @ v.co
        if inv: p = inv @ p
        k = 0.0
        if p.y < -0.09 and 1.50 < p.z < 1.62:
            ax = abs(p.x)
            must = _smooth(p.z, 1.595, 1.599) * (1 - _smooth(p.z, 1.606, 1.611)) * (1 - _smooth(ax, 0.026, 0.032))
            goat = (1 - _smooth(p.z, 1.572, 1.578)) * _smooth(p.z, 1.525, 1.535) * (1 - _smooth(ax, 0.02, 0.027))
            side = (1 - _smooth(p.z, 1.586, 1.592)) * _smooth(ax, 0.024, 0.028) * (1 - _smooth(ax, 0.03, 0.034)) * _smooth(p.z, 1.565, 1.57)
            k = max(must, goat, side)
        at.data[v.index].color = (k, k, k, 1)


def _skin(obj, arm):
    """Piel morena uniforme: la textura de Mixamo es más clara en la cara que en las manos, así que se mezcla el
    tinte con un tono fijo (conserva poros y sombras suaves, iguala cara y manos)."""
    nt, b, out = _base_tex(obj, "klunk_piel", 0.0)
    _eye_mask(obj, arm)
    mask = nt.nodes.new("ShaderNodeAttribute"); mask.attribute_name = "klunk_piel"
    tint = nt.nodes.new("ShaderNodeMix"); tint.data_type = "RGBA"; tint.blend_type = "MULTIPLY"
    nt.links.new(mask.outputs["Fac"], tint.inputs["Factor"])
    nt.links.new(out, tint.inputs[6]); tint.inputs[7].default_value = (*SKIN, 1)
    even = nt.nodes.new("ShaderNodeMix"); even.data_type = "RGBA"
    k6 = nt.nodes.new("ShaderNodeMath"); k6.operation = "MULTIPLY"; k6.inputs[1].default_value = 0.6
    nt.links.new(mask.outputs["Fac"], k6.inputs[0]); nt.links.new(k6.outputs[0], even.inputs["Factor"])
    nt.links.new(tint.outputs[2], even.inputs[6]); even.inputs[7].default_value = (*SKIN_EVEN, 1)
    _beard_mask(obj, arm)
    bm_ = nt.nodes.new("ShaderNodeAttribute"); bm_.attribute_name = "klunk_barba"
    hair = nt.nodes.new("ShaderNodeTexNoise"); hair.inputs["Scale"].default_value = 900; hair.inputs["Detail"].default_value = 2
    dens = nt.nodes.new("ShaderNodeMath"); dens.operation = "MULTIPLY"; dens.use_clamp = True
    nt.links.new(bm_.outputs["Fac"], dens.inputs[0]); nt.links.new(hair.outputs["Fac"], dens.inputs[1])
    dens2 = nt.nodes.new("ShaderNodeMath"); dens2.operation = "MULTIPLY"; dens2.use_clamp = True; dens2.inputs[1].default_value = 1.9
    nt.links.new(dens.outputs[0], dens2.inputs[0])
    beard = nt.nodes.new("ShaderNodeMix"); beard.data_type = "RGBA"; beard.inputs[7].default_value = (0.012, 0.009, 0.007, 1)
    nt.links.new(dens2.outputs[0], beard.inputs["Factor"]); nt.links.new(even.outputs[2], beard.inputs[6])
    nt.links.new(beard.outputs[2], b.inputs["Base Color"])
    for k in ("Subsurface Weight", "Subsurface"):
        if k in b.inputs: b.inputs[k].default_value = 0.0


def _stripes(obj, name, a, b_, bands=7.0):
    """Rayas horizontales pegadas a la tela (coordenadas de reposo: no resbalan al moverse)."""
    nt, b, out = _base_tex(obj, name, 0.35)
    tc = nt.nodes.new("ShaderNodeTexCoord"); sep = nt.nodes.new("ShaderNodeSeparateXYZ")
    mul = nt.nodes.new("ShaderNodeMath"); mul.operation = "MULTIPLY"; mul.inputs[1].default_value = bands
    fr = nt.nodes.new("ShaderNodeMath"); fr.operation = "FRACT"
    ramp = nt.nodes.new("ShaderNodeValToRGB"); ramp.color_ramp.interpolation = "CONSTANT"
    ramp.color_ramp.elements[0].color = (*a, 1); ramp.color_ramp.elements[1].position = 0.5; ramp.color_ramp.elements[1].color = (*b_, 1)
    nt.links.new(tc.outputs["Generated"], sep.inputs[0]); nt.links.new(sep.outputs["Y"], mul.inputs[0])   # malla FBX: Y es la altura
    nt.links.new(mul.outputs[0], fr.inputs[0]); nt.links.new(fr.outputs[0], ramp.inputs["Fac"])
    _multiply(nt, b, out, color_socket=ramp.outputs["Color"])


def _afro_mat():
    m = bpy.data.materials.get("klunk_afro") or bpy.data.materials.new("klunk_afro"); m.use_nodes = True
    nt = m.node_tree; b = nt.nodes["Principled BSDF"]
    b.inputs["Base Color"].default_value = (0.022, 0.016, 0.012, 1); b.inputs["Roughness"].default_value = 0.8
    vor = nt.nodes.new("ShaderNodeTexVoronoi"); vor.inputs["Scale"].default_value = 400
    nz = nt.nodes.new("ShaderNodeTexNoise"); nz.inputs["Scale"].default_value = 160
    add = nt.nodes.new("ShaderNodeMath"); add.operation = "ADD"
    nt.links.new(vor.outputs["Distance"], add.inputs[0]); nt.links.new(nz.outputs["Fac"], add.inputs[1])
    bump = nt.nodes.new("ShaderNodeBump"); bump.inputs["Strength"].default_value = 0.9; bump.inputs["Distance"].default_value = 0.002
    nt.links.new(add.outputs[0], bump.inputs["Height"]); nt.links.new(bump.outputs["Normal"], b.inputs["Normal"])
    return m


def _afro(C, R, seed):
    """Afro: volumen oscuro + cientos de rizos pequeños solapados en la superficie (contorno y textura de pelo rizado),
    con relieve fino en el material. Deja libres la frente y la cara."""
    rnd = random.Random(seed); bm = bmesh.new()
    core = bmesh.ops.create_uvsphere(bm, u_segments=32, v_segments=16, radius=1.0)
    for v in core["verts"]: v.co = Vector((v.co.x * R.x * 0.9, v.co.y * R.y * 0.9, v.co.z * R.z * 0.9))
    kill = [v for v in core["verts"] if (v.co.y < -0.045 and v.co.z < 0.012) or v.co.z < -0.06]
    bmesh.ops.delete(bm, geom=kill, context="VERTS")
    n = 0
    while n < 1500:
        u = Vector((rnd.gauss(0, 1), rnd.gauss(0, 1), rnd.gauss(0, 1))).normalized()
        p = Vector((u.x * R.x, u.y * R.y, u.z * R.z)) * rnd.uniform(0.9, 1.02)
        if p.y < -0.06 and p.z < -0.002: continue                         # frente y cara libres
        if p.z < -0.085 or (p.y < 0 and p.z < -0.03): continue            # sin tapar orejas ni sienes
        r = rnd.uniform(0.009, 0.016); g = bmesh.ops.create_uvsphere(bm, u_segments=8, v_segments=6, radius=r)
        bmesh.ops.translate(bm, vec=p, verts=g["verts"]); n += 1
    me = bpy.data.meshes.new("klunk_afro"); bm.to_mesh(me); bm.free()
    for p_ in me.polygons: p_.use_smooth = True
    o = bpy.data.objects.new("klunk_afro", me); bpy.context.scene.collection.objects.link(o); o.location = C
    me.materials.append(_afro_mat())
    return o


def _face_points(obj, arm):
    """Vértices de la cara en coordenadas del personaje en reposo: [(índice, punto)]."""
    inv = arm.parent.matrix_world.inverted() if arm.parent else None; out = []
    for v in obj.data.vertices:
        p = obj.matrix_world @ v.co
        if inv: p = inv @ p
        if p.z > 1.5 and p.y < -0.05: out.append((v.index, p))
    return out


def _surface_y(face, x, z):
    c = [p for _, p in face if abs(p.x - x) < 0.006 and abs(p.z - z) < 0.006]
    return min(p.y for p in c) if c else -0.12


def _brows(face):
    """Cejas gruesas y oscuras sobre el arco de la ceja (tubos con grosor que se afina hacia fuera)."""
    m = _mat("klunk_cejas", (0.012, 0.009, 0.007), 0.8); objs = []
    for sx in (1, -1):
        cu = bpy.data.curves.new("klunk_ceja", "CURVE"); cu.dimensions = "3D"; cu.bevel_depth = 0.0032; cu.bevel_resolution = 2
        sp = cu.splines.new("POLY"); xs = [0.010, 0.022, 0.036, 0.050, 0.060]; sp.points.add(len(xs) - 1)
        for i, x in enumerate(xs):
            z = 1.680 + 0.004 * math.sin(math.pi * (x - 0.01) / 0.05) - (0.002 if i == len(xs) - 1 else 0)
            y = _surface_y(face, x, z) - 0.0025
            sp.points[i].co = (sx * x, y, z, 1); sp.points[i].radius = (1.25, 1.2, 1.0, 0.8, 0.5)[i]
        o = bpy.data.objects.new("klunk_ceja", cu); bpy.context.scene.collection.objects.link(o)
        o.scale = (1, 0.7, 1); cu.materials.append(m); objs.append(o)
    return objs


def _expressions(obj, arm, face):
    """Claves de forma en la malla: 'sonrisa' (comisuras arriba y afuera, mejillas arriba) y 'sorpresa' (frente y
    cejas arriba). Se animan con expression(actor, nombre, fotograma, valor)."""
    me = obj.data
    if not me.shape_keys: obj.shape_key_add(name="Basis", from_mix=False)
    to_local = obj.matrix_world.inverted().to_3x3() @ (arm.parent.matrix_world.to_3x3() if arm.parent else 1)
    smile = obj.shape_key_add(name="sonrisa", from_mix=False); sur = obj.shape_key_add(name="sorpresa", from_mix=False)
    for i, p in face:
        ax = abs(p.x); sgn = 1 if p.x >= 0 else -1
        # sonrisa: máximo en las comisuras (x≈0,024, z≈1,589), con caída suave
        w = math.exp(-(((ax - 0.024) / 0.012) ** 2 + ((p.z - 1.589) / 0.012) ** 2))
        ck = math.exp(-(((ax - 0.038) / 0.016) ** 2 + ((p.z - 1.612) / 0.014) ** 2)) * 0.5
        d = Vector((sgn * 0.0035 * w, 0.002 * w, 0.0055 * w + 0.003 * ck))
        smile.data[i].co = me.vertices[i].co + to_local @ d
        # sorpresa: frente y arco de la ceja arriba
        wb = _smooth(p.z, 1.664, 1.678) * (1 - _smooth(p.z, 1.70, 1.73)) * (1 - _smooth(ax, 0.06, 0.075))
        sur.data[i].co = me.vertices[i].co + to_local @ Vector((0, 0, 0.0055 * wb))
    return smile, sur


def expression(actor, name, f, value, ramp=4):
    """Anima una expresión ('sonrisa' o 'sorpresa') hasta `value` (0-1) en el fotograma f, en `ramp` fotogramas.
    Las cejas acompañan a la sorpresa."""
    body = next((o for o in actor.meshes if o.name.startswith("Ch01_Body")), None)
    kb = body.data.shape_keys.key_blocks[name]
    kb.keyframe_insert("value", frame=f); kb.value = value; kb.keyframe_insert("value", frame=f + ramp)
    if name == "sorpresa":
        for o in getattr(actor, "brows", []):
            o.keyframe_insert("delta_location", frame=f)
            k = actor.arm.matrix_world.to_scale()[0]                       # el padre (hueso) va a escala 0,01
            o.delta_location = (0, 0.0055 * value / k, 0)                   # eje Y del hueso de la cabeza = hacia arriba
            o.keyframe_insert("delta_location", frame=f + ramp)


def apply(actor, seed=3):
    arm = actor.arm; parts = {o.name.split(".")[0]: o for o in actor.meshes}
    if "Ch01_Shirt" in parts: _stripes(parts["Ch01_Shirt"], "klunk_camiseta", STRIPE_A, STRIPE_B)
    if "Ch01_Pants" in parts: _tint(parts["Ch01_Pants"], PANTS, "klunk_pantalon", bright=0.1)
    if "Ch01_Sneakers" in parts: _tint(parts["Ch01_Sneakers"], SHOES, "klunk_zapatillas", bright=0.15)
    if "Ch01_Body" in parts: _skin(parts["Ch01_Body"], arm)
    head = next(b.name for b in arm.data.bones if b.name.split(":")[-1] == "Head")
    # se construye en coordenadas del personaje en reposo (mirando a -Y, ~1,8 m) y luego se cuelga del hueso
    old_pp = arm.data.pose_position; arm.data.pose_position = "REST"; bpy.context.view_layer.update()
    body = parts.get("Ch01_Body"); face = _face_points(body, arm) if body else []
    brows = _brows(face) if face else []
    if face: _expressions(body, arm, face)
    new = [_afro(Vector((0, 0.02, 1.705)), Vector((0.13, 0.135, 0.115)), seed)] + brows
    bpy.context.view_layer.update()
    for o in new:                                                        # colgar del hueso de la cabeza sin moverlos
        mw = arm.parent.matrix_world @ o.matrix_world if arm.parent else o.matrix_world.copy()
        o.parent = arm; o.parent_type = "BONE"; o.parent_bone = head
        bpy.context.view_layer.update(); o.matrix_world = mw
    arm.data.pose_position = old_pp; bpy.context.view_layer.update()
    actor.look_parts = new; actor.brows = brows
    return new
