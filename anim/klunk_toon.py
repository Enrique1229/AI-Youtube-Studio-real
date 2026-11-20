"""klunk_toon.py — protagonista del canal en estilo dibujo 3D (piel lisa, cara simple y expresiva) sobre el cuerpo y
las animaciones de Mixamo (episodios 12+).

    from mixamo import MixamoActor
    from klunk_toon import apply, expression, blink
    a = MixamoActor(S, ...); apply(a)
    expression(a, "sorpresa", f, 1.0); blink(a, f)

Cómo: se oculta la cabeza realista del modelo de Mixamo (modificador Mask) y se cuelga del hueso Head una cabeza
propia hecha por código: ojos grandes con párpados, cejas gruesas, nariz pequeña, boca de tubo con expresiones,
orejas y afro. Cuerpo y ropa en colores lisos y mates. Proporciones casi humanas con la cabeza algo grande.
Diseño propio (inspirado en el estilo general de las animaciones 3D de comedia, sin copiar personajes).
"""
import math, random
import bmesh, bpy
from mathutils import Vector

SKIN = (0.23, 0.12, 0.065)
STRIPE_A = (1.00, 0.40, 0.03); STRIPE_B = (0.95, 0.90, 0.80)
PANTS = (0.04, 0.07, 0.20); SHOES = (0.70, 0.03, 0.03); SOLE = (0.92, 0.92, 0.9)
HAIR = (0.018, 0.013, 0.010)

HC = Vector((0, -0.012, 1.665))      # centro de la cabeza nueva (personaje en reposo, mirando a -Y)
HR = Vector((0.098, 0.105, 0.122))   # radios de la cabeza (un 15 % mayor que la real)


def _mat(name, color, rough=0.6, spec=0.3, coat=0.0):
    m = bpy.data.materials.get(name) or bpy.data.materials.new(name); m.use_nodes = True
    b = m.node_tree.nodes["Principled BSDF"]
    b.inputs["Base Color"].default_value = (*color, 1); b.inputs["Roughness"].default_value = rough
    if "Specular IOR Level" in b.inputs: b.inputs["Specular IOR Level"].default_value = spec
    if coat and "Coat Weight" in b.inputs: b.inputs["Coat Weight"].default_value = coat
    return m


def _flat(obj, mat):
    obj.data.materials.clear(); obj.data.materials.append(mat)


def _stripes_mat():
    m = _mat("toon_camiseta", STRIPE_A, 0.7); nt = m.node_tree; b = nt.nodes["Principled BSDF"]
    tc = nt.nodes.new("ShaderNodeTexCoord"); sep = nt.nodes.new("ShaderNodeSeparateXYZ")
    mul = nt.nodes.new("ShaderNodeMath"); mul.operation = "MULTIPLY"; mul.inputs[1].default_value = 7.0
    fr = nt.nodes.new("ShaderNodeMath"); fr.operation = "FRACT"
    ramp = nt.nodes.new("ShaderNodeValToRGB"); ramp.color_ramp.interpolation = "CONSTANT"
    ramp.color_ramp.elements[0].color = (*STRIPE_A, 1); ramp.color_ramp.elements[1].position = 0.5
    ramp.color_ramp.elements[1].color = (*STRIPE_B, 1)
    nt.links.new(tc.outputs["Generated"], sep.inputs[0]); nt.links.new(sep.outputs["Y"], mul.inputs[0])
    nt.links.new(mul.outputs[0], fr.inputs[0]); nt.links.new(fr.outputs[0], ramp.inputs["Fac"])
    nt.links.new(ramp.outputs["Color"], b.inputs["Base Color"])
    return m


def _new(name, fn, loc=(0, 0, 0), scale=(1, 1, 1), rot=(0, 0, 0), mat=None, smooth=True):
    bm = bmesh.new(); fn(bm); me = bpy.data.meshes.new(name); bm.to_mesh(me); bm.free()
    if smooth:
        for p in me.polygons: p.use_smooth = True
    o = bpy.data.objects.new(name, me); bpy.context.scene.collection.objects.link(o)
    o.location = loc; o.scale = scale; o.rotation_euler = rot
    if mat: me.materials.append(mat)
    return o


def _sphere(r=1.0, u=32, v=16):
    return lambda bm: bmesh.ops.create_uvsphere(bm, u_segments=u, v_segments=v, radius=r)


def _tube(name, pts, radius, mat, radii=None):
    cu = bpy.data.curves.new(name, "CURVE"); cu.dimensions = "3D"; cu.bevel_depth = radius; cu.bevel_resolution = 3
    cu.use_fill_caps = True
    sp = cu.splines.new("NURBS"); sp.points.add(len(pts) - 1); sp.use_endpoint_u = True; sp.order_u = 3
    c = sum((Vector(p) for p in pts), Vector()) / len(pts)              # origen en el centro: escala/giro en su sitio
    for i, p in enumerate(pts):
        sp.points[i].co = (*(Vector(p) - c), 1); sp.points[i].radius = radii[i] if radii else 1.0
    o = bpy.data.objects.new(name, cu); bpy.context.scene.collection.objects.link(o); cu.materials.append(mat); o.location = c
    return o


def _hide_real_head(body, arm):
    """Máscara: oculta los vértices de la cabeza realista (se conserva el cuello hasta dentro del cuello de la camisa)."""
    inv = arm.parent.matrix_world.inverted() if arm.parent else None
    vg = body.vertex_groups.get("toon_cuerpo") or body.vertex_groups.new(name="toon_cuerpo")
    keep = []
    for v in body.data.vertices:
        p = body.matrix_world @ v.co
        if inv: p = inv @ p
        neck = (p.x ** 2 + (p.y - 0.012) ** 2) ** 0.5 < 0.058              # solo el cilindro del cuello
        if p.z < 1.50 or (p.z < 1.585 and neck): keep.append(v.index)
    vg.add(keep, 1.0, "REPLACE")
    m = body.modifiers.new("toon_sin_cabeza", "MASK"); m.vertex_group = "toon_cuerpo"
    # la máscara antes del esqueleto no importa: Mask trabaja sobre los vértices de origen
    for eye in [o for o in bpy.data.objects if o.name.startswith("Ch01_Eyelashes")]: eye.hide_render = eye.hide_viewport = True


def _head(seed):
    skin = _mat("toon_piel", SKIN, 0.55, 0.35)
    white = _mat("toon_ojo", (0.92, 0.92, 0.90), 0.25, 0.5); iris = _mat("toon_iris", (0.07, 0.035, 0.015), 0.2, 0.6)
    black = _mat("toon_pupila", (0.005, 0.004, 0.004), 0.15, 0.6); shine = _mat("toon_brillo", (1, 1, 1), 0.05, 1.0)
    hairm = _mat("toon_pelo", HAIR, 0.85, 0.2); mouthm = _mat("toon_boca", (0.06, 0.012, 0.012), 0.5)
    lipm = _mat("toon_labio", (0.16, 0.07, 0.05), 0.5)
    parts = {}
    # cráneo + mandíbula: elipsoide con barbilla algo más estrecha
    def skull(bm):
        bmesh.ops.create_uvsphere(bm, u_segments=48, v_segments=28, radius=1.0)
        for v in bm.verts:
            z = v.co.z; narrow = 1.0 - 0.12 * max(0.0, -z) ** 2           # mandíbula más estrecha abajo
            v.co.x *= narrow; v.co.y *= (1.0 - 0.10 * max(0.0, -z))
            if z < -0.55: v.co.y -= 0.06 * (-z - 0.55)                         # barbilla un poco adelantada
    parts["cabeza"] = _new("toon_cabeza", skull, HC, tuple(HR), mat=skin)
    parts["cuello"] = _new("toon_cuello", lambda bm: bmesh.ops.create_cone(bm, cap_ends=False, segments=24, radius1=0.05, radius2=0.047, depth=0.12),
                           (0, 0.012, 1.545), mat=skin)
    ex, ey, ez, er = 0.040, HC.y - HR.y * 0.80, HC.z + 0.012, 0.030      # ojos grandes, un poco separados
    parts["ojos"], parts["parpados"], parts["pupilas"] = [], [], []
    for sx in (1, -1):
        e = _new("toon_ojo", _sphere(er, 32, 16), (sx * ex, ey, ez), (1.0, 0.75, 1.12), mat=white); parts["ojos"].append(e)
        ir = _new("toon_iris", _sphere(er * 0.52, 24, 12), (sx * ex * 0.97, ey - er * 0.62, ez - er * 0.08), (1, 0.45, 1.05), mat=iris)
        pu = _new("toon_pupila", _sphere(er * 0.27, 16, 8), (sx * ex * 0.97, ey - er * 0.84, ez - er * 0.08), (1, 0.35, 1.05), mat=black)
        sh = _new("toon_brillo", _sphere(er * 0.11, 12, 6), (sx * ex * 0.97 + er * 0.2, ey - er * 0.95, ez + er * 0.18), (1, 0.5, 1), mat=shine)
        parts["pupilas"].append((ir, pu, sh))
        # párpado superior: media esfera de piel algo mayor que el ojo; rotándolo en X se cierra (parpadeo)
        def lid(bm):
            bmesh.ops.create_uvsphere(bm, u_segments=32, v_segments=16, radius=er * 1.07)
            bmesh.ops.delete(bm, geom=[v for v in bm.verts if v.co.z < er * 0.02], context="VERTS")
        L = _new("toon_parpado", lid, (sx * ex, ey, ez), (1.0, 0.8, 1.12), (math.radians(-38), 0, 0), mat=skin)
        parts["parpados"].append(L)
    # cejas gruesas (tubos) — se suben/bajan/inclinan para las expresiones
    parts["cejas"] = []
    for sx in (1, -1):
        bz = ez + er * 1.22; by = ey - 0.010
        c = _tube("toon_ceja", [(sx * 0.014, by + 0.004, bz - 0.003), (sx * 0.038, by - 0.002, bz + 0.004), (sx * 0.062, by + 0.008, bz)], 0.0062, hairm,
                  radii=[1.15, 1.0, 0.65])
        parts["cejas"].append(c)
    # nariz pequeña y redondeada
    parts["nariz"] = _new("toon_nariz", _sphere(0.017, 24, 12), (0, HC.y - HR.y * 0.98, HC.z - 0.03), (1.15, 0.9, 0.9), mat=skin)
    # boca: tubo oscuro con curva (sonrisa por defecto ligera) + labio inferior sutil
    my, mz = HC.y - HR.y * 0.90, HC.z - 0.058
    parts["boca"] = _tube("toon_boca", [(-0.030, my + 0.012, mz + 0.004), (-0.012, my + 0.001, mz - 0.002), (0.0, my, mz - 0.003),
                                        (0.012, my + 0.001, mz - 0.002), (0.030, my + 0.012, mz + 0.004)], 0.0032, mouthm)
    # orejas
    parts["orejas"] = [_new("toon_oreja", _sphere(0.026, 20, 10), (sx * HR.x * 0.98, HC.y + 0.005, HC.z - 0.005), (0.45, 0.8, 1.0), mat=skin)
                       for sx in (1, -1)]
    # afro: volumen + rizos pequeños (estilo dibujo: rizos algo más grandes y redondos)
    rnd = random.Random(seed); C = HC + Vector((0, 0.02, 0.055)); R = Vector((HR.x * 1.38, HR.y * 1.35, HR.z * 1.05))
    def afro(bm):
        core = bmesh.ops.create_uvsphere(bm, u_segments=32, v_segments=16, radius=1.0)
        for v in core["verts"]: v.co = Vector((v.co.x * R.x * 0.9, v.co.y * R.y * 0.9, v.co.z * R.z * 0.9))
        bmesh.ops.delete(bm, geom=[v for v in core["verts"] if (v.co.y < -0.025 and v.co.z < 0.015) or v.co.z < -0.075], context="VERTS")
        n = 0
        while n < 650:
            u = Vector((rnd.gauss(0, 1), rnd.gauss(0, 1), rnd.gauss(0, 1))).normalized()
            p = Vector((u.x * R.x, u.y * R.y, u.z * R.z)) * rnd.uniform(0.92, 1.02)
            if p.y < -0.04 and p.z < 0.022: continue
            if p.z < -0.09 or (p.y < -0.01 and p.z < -0.035): continue
            r = rnd.uniform(0.014, 0.022); g = bmesh.ops.create_uvsphere(bm, u_segments=10, v_segments=7, radius=r)
            bmesh.ops.translate(bm, vec=p, verts=g["verts"]); n += 1
    parts["afro"] = _new("toon_afro", afro, C, mat=hairm)
    return parts


def apply(actor, seed=4):
    arm = actor.arm; parts = {o.name.split(".")[0]: o for o in actor.meshes}
    if "Ch01_Body" in parts:
        _flat(parts["Ch01_Body"], _mat("toon_piel", SKIN, 0.55, 0.35)); _hide_real_head(parts["Ch01_Body"], arm)
    if "Ch01_Shirt" in parts: _flat(parts["Ch01_Shirt"], _stripes_mat())
    if "Ch01_Pants" in parts: _flat(parts["Ch01_Pants"], _mat("toon_pantalon", PANTS, 0.8, 0.2))
    if "Ch01_Sneakers" in parts: _flat(parts["Ch01_Sneakers"], _mat("toon_zapatillas", SHOES, 0.5, 0.4))
    head = next(b.name for b in arm.data.bones if b.name.split(":")[-1] == "Head")
    old_pp = arm.data.pose_position; arm.data.pose_position = "REST"; bpy.context.view_layer.update()
    hp = _head(seed); bpy.context.view_layer.update()
    flat = []
    for v in hp.values(): flat += (v if isinstance(v, list) else [v])
    flat = [x for t in flat for x in (t if isinstance(t, tuple) else (t,))]
    roots = [o for o in flat if o.parent is None]
    for o in roots:
        mw = arm.parent.matrix_world @ o.matrix_world if arm.parent else o.matrix_world.copy()
        o.parent = arm; o.parent_type = "BONE"; o.parent_bone = head
        bpy.context.view_layer.update(); o.matrix_world = mw
    arm.data.pose_position = old_pp; bpy.context.view_layer.update()
    actor.toon = hp
    return hp


def _key(o, path, f):
    o.keyframe_insert(path, frame=f)


def blink(actor, f, dur=4):
    """Parpadeo: los párpados bajan y suben."""
    for L in actor.toon["parpados"]:
        r0 = L.rotation_euler.x
        _key(L, "rotation_euler", f); L.rotation_euler.x = math.radians(40); _key(L, "rotation_euler", f + dur // 2)
        L.rotation_euler.x = r0; _key(L, "rotation_euler", f + dur)


def expression(actor, name, f, value=1.0, ramp=3):
    """Expresiones: 'sorpresa' (cejas arriba, ojos muy abiertos, boca en O), 'enfado' (cejas hacia dentro y abajo),
    'feliz' (sonrisa grande, ojos entornados), 'neutra'. Se anima desde el estado anterior en `ramp` fotogramas."""
    t = actor.toon; k = actor.arm.matrix_world.to_scale()[0]          # el hueso padre va a escala 0,01
    brows, lids, mouth = t["cejas"], t["parpados"], t["boca"]
    for o in brows + lids + [mouth]:
        for p in ("delta_location", "delta_rotation_euler", "delta_scale"): _key(o, p, f)
    up = {"sorpresa": 0.0055, "enfado": -0.006, "feliz": 0.004, "neutra": 0.0}[name] * value
    tilt = {"sorpresa": 0.0, "enfado": 0.35, "feliz": -0.1, "neutra": 0.0}[name] * value
    lid = {"sorpresa": -0.35, "enfado": 0.25, "feliz": 0.3, "neutra": 0.0}[name] * value
    for i, o in enumerate(brows):
        sx = 1 if i == 0 else -1
        o.delta_location = (0, up / k, 0)                                   # eje Y del hueso = arriba
        o.delta_rotation_euler = (0, 0, -sx * tilt)
    for L in lids: L.delta_rotation_euler = (lid, 0, 0)
    ms = {"sorpresa": (0.55, 1.0, 3.2), "enfado": (0.9, 1.0, 0.8), "feliz": (1.25, 1.0, 1.6), "neutra": (1, 1, 1)}[name]
    mouth.delta_scale = tuple(1 + (m - 1) * value for m in ms)
    for o in brows + lids + [mouth]:
        for p in ("delta_location", "delta_rotation_euler", "delta_scale"): _key(o, p, f + ramp)
