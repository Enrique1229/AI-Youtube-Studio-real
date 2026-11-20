"""klunk_look.py — aspecto propio y fijo del protagonista del canal sobre el personaje de Mixamo (episodios 11+).

    from mixamo import MixamoActor
    from klunk_look import apply
    a = MixamoActor(S, ...); apply(a)

Protagonista: hombre afroamericano con pelo afro (pelo de verdad: hebras rizadas con partículas, no una bola),
cara y ojos naturales del modelo, y ropa reconocible a primera vista en el móvil: camiseta de rayas horizontales
naranja y crema, pantalón azul marino y zapatillas rojas.
El pelo va pegado al hueso de la cabeza: sigue a cualquier animación de Mixamo sin tocar los clips.
"""
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
    nt.links.new(even.outputs[2], b.inputs["Base Color"])
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


def _hair_mats():
    shell = bpy.data.materials.get("klunk_afro_base") or bpy.data.materials.new("klunk_afro_base")
    shell.use_nodes = True; sb = shell.node_tree.nodes["Principled BSDF"]
    sb.inputs["Base Color"].default_value = (0.012, 0.009, 0.007, 1); sb.inputs["Roughness"].default_value = 0.9
    hair = bpy.data.materials.get("klunk_afro_pelo") or bpy.data.materials.new("klunk_afro_pelo")
    hair.use_nodes = True; nt = hair.node_tree
    for n in list(nt.nodes):
        if n.type != "OUTPUT_MATERIAL": nt.nodes.remove(n)
    h = nt.nodes.new("ShaderNodeBsdfHairPrincipled")
    try: h.parametrization = "MELANIN"
    except Exception: pass
    for k, v in (("Melanin", 0.95), ("Melanin Redness", 0.25), ("Roughness", 0.55), ("Radial Roughness", 0.8), ("Random Roughness", 0.3)):
        if k in h.inputs: h.inputs[k].default_value = v
    nt.links.new(h.outputs[0], nt.nodes["Material Output"].inputs["Surface"])
    return shell, hair


def _afro(C, R, seed):
    """Casquete con forma de afro (sin tapar frente ni cara) del que salen hebras cortas y muy rizadas."""
    bm = bmesh.new(); bmesh.ops.create_uvsphere(bm, u_segments=48, v_segments=32, radius=1.0)
    for v in bm.verts:
        v.co = Vector((v.co.x * R.x, v.co.y * R.y * (0.78 if v.co.y < 0 else 1.0), v.co.z * R.z))   # delante pegado a la frente
    kill = [v for v in bm.verts if (v.co.y < -0.05 and v.co.z < 0.012) or v.co.z < -0.085 or (v.co.y < 0.0 and v.co.z < -0.035)]
    bmesh.ops.delete(bm, geom=kill, context="VERTS")
    me = bpy.data.meshes.new("klunk_afro"); bm.to_mesh(me); bm.free()
    for p in me.polygons: p.use_smooth = True
    o = bpy.data.objects.new("klunk_afro", me); bpy.context.scene.collection.objects.link(o); o.location = C
    shell, hair = _hair_mats(); me.materials.append(shell); me.materials.append(hair)
    sub = o.modifiers.new("suave", "SUBSURF"); sub.levels = sub.render_levels = 1
    ps = o.modifiers.new("pelo", "PARTICLE_SYSTEM").particle_system; s = ps.settings; s.name = "klunk_afro"
    ps.seed = seed
    s.type = "HAIR"; s.count = 9000; s.hair_length = 0.045; s.use_advanced_hair = True
    s.normal_factor = 1.0; s.factor_random = 0.25; s.material_slot = "klunk_afro_pelo"
    s.child_type = "INTERPOLATED"; s.child_percent = 6; s.rendered_child_count = 14; s.child_length = 0.9; s.child_length_threshold = 0.3
    s.kink = "CURL"; s.kink_amplitude = 0.008; s.kink_frequency = 18; s.kink_shape = 0.2
    s.roughness_1 = 0.004; s.roughness_endpoint = 0.01; s.clump_factor = 0.25
    s.display_step = 3; s.render_step = 5
    s.root_radius = 1.0; s.tip_radius = 0.6; s.radius_scale = 0.0012
    return o


def apply(actor, seed=3):
    arm = actor.arm; parts = {o.name.split(".")[0]: o for o in actor.meshes}
    if "Ch01_Shirt" in parts: _stripes(parts["Ch01_Shirt"], "klunk_camiseta", STRIPE_A, STRIPE_B)
    if "Ch01_Pants" in parts: _tint(parts["Ch01_Pants"], PANTS, "klunk_pantalon", bright=0.1)
    if "Ch01_Sneakers" in parts: _tint(parts["Ch01_Sneakers"], SHOES, "klunk_zapatillas", bright=0.15)
    if "Ch01_Body" in parts: _skin(parts["Ch01_Body"], arm)
    head = next(b.name for b in arm.data.bones if b.name.split(":")[-1] == "Head")
    # se construye en coordenadas del personaje en reposo (mirando a -Y, ~1,8 m) y luego se cuelga del hueso
    old_pp = arm.data.pose_position; arm.data.pose_position = "REST"; bpy.context.view_layer.update()
    new = [_afro(Vector((0, 0.022, 1.700)), Vector((0.128, 0.13, 0.112)), seed)]
    bpy.context.view_layer.update()
    for o in new:                                                        # colgar del hueso de la cabeza sin moverlos
        mw = arm.parent.matrix_world @ o.matrix_world if arm.parent else o.matrix_world.copy()
        o.parent = arm; o.parent_type = "BONE"; o.parent_bone = head
        bpy.context.view_layer.update(); o.matrix_world = mw
        k = o.scale[0]                                                    # el hueso hereda la escala 0,01 del esqueleto:
        for psys in o.particle_systems:                                   # el pelo se mide en unidades locales
            st = psys.settings; st.hair_length /= k; st.radius_scale /= k
    arm.data.pose_position = old_pp; bpy.context.view_layer.update()
    actor.look_parts = new
    return new
