"""env_real.py — escenario de parque realista para episodios 9+ (personaje de Mixamo).

Parte del parque con río del kit (misma distribución: orillas, río en x∈[-2.5, 2.5], muelle) y lo hace realista con
recursos CC0 de Poly Haven (assets/polyhaven/, ver LICENSES.json):
  - cielo HDRI de un parque real (luz e reflejos reales; su foto se ve al fondo),
  - suelo con textura PBR (color, relieve, rugosidad),
  - árboles, matas de hierba, roca y tronco escaneados en lugar de las bolas de código.
No modifica env_rio (los episodios 1-8 no cambian).
"""
import math, pathlib, random
import bpy

ROOT = pathlib.Path(__file__).resolve().parent.parent
PH = ROOT / "assets" / "polyhaven"


def _need(p):
    if not p.exists(): raise FileNotFoundError(f"falta {p} (descárgalo con scripts/fetch_polyhaven.py)")
    return p


def _hdri(S, name="greenwich_park", res="2k", strength=1.0, rot_deg=0):
    w = S.sc.world; nt = w.node_tree; N = nt.nodes; L = nt.links
    for n in list(N):
        if n.type not in ("OUTPUT_WORLD", "BACKGROUND"): N.remove(n)
    bg = N["Background"]; env = N.new("ShaderNodeTexEnvironment")
    env.image = bpy.data.images.load(str(_need(PH / name / f"{name}_{res}.hdr")))
    tc = N.new("ShaderNodeTexCoord"); mp = N.new("ShaderNodeMapping"); mp.inputs["Rotation"].default_value[2] = math.radians(rot_deg)
    L.new(tc.outputs["Generated"], mp.inputs["Vector"]); L.new(mp.outputs["Vector"], env.inputs["Vector"])
    L.new(env.outputs["Color"], bg.inputs[0]); bg.inputs[1].default_value = strength


def _pbr(S, name, res="2k", scale=40.0):
    key = "pbr_" + name
    if key in S.mats: return S.mats[key]
    d = PH / name; m = bpy.data.materials.new(key); m.use_nodes = True; N = m.node_tree.nodes; L = m.node_tree.links
    b = N["Principled BSDF"]; tc = N.new("ShaderNodeTexCoord"); mp = N.new("ShaderNodeMapping"); mp.inputs["Scale"].default_value = (scale, scale, scale)
    L.new(tc.outputs["UV"], mp.inputs["Vector"])
    def tex(suffix, colorspace="sRGB"):
        f = next(iter(sorted(d.glob(f"*_{suffix}_{res}.*"))), None)
        if not f: return None
        t = N.new("ShaderNodeTexImage"); t.image = bpy.data.images.load(str(f)); t.image.colorspace_settings.name = colorspace
        L.new(mp.outputs["Vector"], t.inputs["Vector"]); return t
    c = tex("diff"); r = tex("rough", "Non-Color"); n = tex("nor_gl", "Non-Color")
    if c: L.new(c.outputs["Color"], b.inputs["Base Color"])
    if r: L.new(r.outputs["Color"], b.inputs["Roughness"])
    if n:
        nm = N.new("ShaderNodeNormalMap"); L.new(n.outputs["Color"], nm.inputs["Color"]); L.new(nm.outputs["Normal"], b.inputs["Normal"])
    S.mats[key] = m; return m


def _model(name, res="1k"):
    """Importa un modelo glTF de Poly Haven una vez y devuelve sus objetos (ocultos: se usan como instancias)."""
    before = set(bpy.data.objects)
    bpy.ops.import_scene.gltf(filepath=str(_need(PH / name / f"{name}_{res}.gltf")))
    new = [o for o in bpy.data.objects if o not in before]
    col = bpy.data.collections.new("ph_" + name)
    for o in new:
        for c in list(o.users_collection): c.objects.unlink(o)
        col.objects.link(o)
    col.hide_render = False
    return col


def _place(S, col, loc, rot_z=0.0, scale=1.0):
    inst = bpy.data.objects.new(col.name + "_i", None); inst.instance_type = "COLLECTION"; inst.instance_collection = col
    inst.location = loc; inst.rotation_euler = (0, 0, rot_z); inst.scale = (scale,) * 3
    S.sc.collection.objects.link(inst); return inst


def build(S):
    S.env_rio_real()                                         # distribución del parque con río (orillas, agua, muelle, cámara)
    # quita lo "de código" que desentona con un humano realista: árboles de bolas, bosque de fondo, piedras, briznas
    for o in list(S.sc.objects):
        if o.name.startswith(("tronco", "copa", "fondo", "piedra", "deco", "hoja", "brizna", "prado", "hierba_frente")):
            bpy.data.objects.remove(o, do_unlink=True)
    _hdri(S, strength=1.0, rot_deg=40)
    sun = bpy.data.objects.get("sun")
    if sun: sun.data.energy = 2.2; sun.data.angle = math.radians(1.5)
    g = _pbr(S, "aerial_grass_rock", scale=60.0)
    for o in S.sc.objects:
        if o.name.startswith(("orillaL", "orillaR")) and o.type == "MESH": o.data.materials[0] = g
    # bancos de colecciones (se guardan fuera de la escena y se instancian)
    trees = [_model("island_tree_01"), _model("island_tree_02")]; grass = _model("grass_medium_01")
    rock = _model("boulder_01"); log = _model("dead_tree_trunk")
    rnd = random.Random(7)
    for i in range(14):                                       # árboles a ambos lados, detrás del río
        side = rnd.choice((-1, 1)); x = side * rnd.uniform(4.0, 16.0); y = rnd.uniform(3.0, 28.0)
        _place(S, rnd.choice(trees), (x, y, 0), rnd.uniform(0, 6.28), rnd.uniform(0.8, 1.2))
    for i in range(160):                                      # matas de hierba cerca de la cámara (orilla izquierda y derecha)
        x = rnd.uniform(-9, -2.7) if rnd.random() < 0.7 else rnd.uniform(2.7, 8)
        y = rnd.uniform(-6.5, 6.0)
        if -3.6 < x < -1.6 and abs(y) < 0.7: continue          # muelle libre
        _place(S, grass, (x, y, 0), rnd.uniform(0, 6.28), rnd.uniform(0.6, 1.2))
    for (x, y, s_) in ((-5.5, 2.5, 0.6), (4.2, 3.5, 0.8), (-8.0, 6.0, 1.0)): _place(S, rock, (x, y, 0), rnd.uniform(0, 6.28), s_)
    _place(S, log, (-6.5, 1.2, 0), 0.6, 1.0)
    # agua de río natural (verde oscuro, reflejos, ligera turbidez) y muelle de tablones con textura real
    wm = bpy.data.materials.new("agua_rio"); wm.use_nodes = True; wb = wm.node_tree.nodes["Principled BSDF"]
    wb.inputs["Base Color"].default_value = (0.04, 0.09, 0.07, 1); wb.inputs["Roughness"].default_value = 0.06
    wb.inputs["Transmission Weight"].default_value = 0.35; wb.inputs["IOR"].default_value = 1.33
    nz = wm.node_tree.nodes.new("ShaderNodeTexNoise"); nz.inputs["Scale"].default_value = 18
    bp = wm.node_tree.nodes.new("ShaderNodeBump"); bp.inputs["Strength"].default_value = 0.08
    wm.node_tree.links.new(nz.outputs["Fac"], bp.inputs["Height"]); wm.node_tree.links.new(bp.outputs["Normal"], wb.inputs["Normal"])
    if getattr(S, "water", None): S.water.data.materials[0] = wm
    planks = _pbr(S, "brown_planks_03", res="1k", scale=1.5)
    dock = bpy.data.objects.get("muelle")
    if dock:
        dock.data.materials[0] = planks
        bpy.context.view_layer.objects.active = dock
        for o in S.sc.objects: o.select_set(o is dock)
        bpy.ops.object.mode_set(mode="EDIT"); bpy.ops.mesh.select_all(action="SELECT"); bpy.ops.uv.cube_project(cube_size=0.6)
        bpy.ops.object.mode_set(mode="OBJECT")
    S.sc.view_settings.view_transform = "AgX"
    try: S.sc.view_settings.look = "AgX - Base Contrast"; S.sc.view_settings.exposure = 0.0
    except Exception: pass


# ------------------------------------------------------------------ plaza urbana (episodio 17+)
def _col_bounds(col):
    """(min, max) en coordenadas locales de los objetos de malla de una colección importada."""
    from mathutils import Vector
    pts = [o.matrix_world @ Vector(c) for o in col.objects if o.type == "MESH" for c in o.bound_box]
    return (Vector((min(p.x for p in pts), min(p.y for p in pts), min(p.z for p in pts))),
            Vector((max(p.x for p in pts), max(p.y for p in pts), max(p.z for p in pts))))


def _place_fit(S, col, loc, height, rot_z=0.0):
    """Instancia `col` con la base apoyada en z=loc[2] y escalada para que mida `height` m de alto (Poly Haven no siempre viene en metros).
    Devuelve (instancia, escala, (ancho_x, ancho_y))."""
    lo, hi = _col_bounds(col)
    k = height / max(1e-6, hi.z - lo.z)
    cx, cy = (lo.x + hi.x) / 2, (lo.y + hi.y) / 2
    import math as _m
    c, s_ = _m.cos(rot_z), _m.sin(rot_z)
    # el origen del modelo no tiene por qué estar en su centro: se compensa para que (loc.x, loc.y) sea el centro de la base
    off = (-(cx * c - cy * s_) * k, -(cx * s_ + cy * c) * k, -lo.z * k)
    inst = _place(S, col, (loc[0] + off[0], loc[1] + off[1], loc[2] + off[2]), rot_z, k)
    return inst, k, ((hi.x - lo.x) * k, (hi.y - lo.y) * k)


def build_plaza(S, rot_deg=0, sun_energy=3.0):
    """Plaza urbana realista: cielo HDRI dresden_square, suelo de adoquín PBR hasta el horizonte y atrezo (farola, papelera, jardinera).
    Sin césped ni parque. Deja solo sol, cámara y objetivo del escenario base. Reutiliza _hdri/_pbr/_model.
    Devuelve dict con las instancias del atrezo (para colocar o animar)."""
    for o in list(S.sc.objects):
        if o.name.startswith("sun") or o is S.cam or o is S.tgt: continue
        bpy.data.objects.remove(o, do_unlink=True)
    _hdri(S, name="dresden_square", strength=1.0, rot_deg=rot_deg)
    sun = bpy.data.objects["sun"]; sun.data.energy = sun_energy; sun.data.color = (1.0, 0.94, 0.84); sun.data.angle = math.radians(1.5)
    sun.rotation_euler = (math.radians(52), 0, math.radians(-28))
    S.sc.view_settings.view_transform = "AgX"
    try: S.sc.view_settings.look = "AgX - Base Contrast"; S.sc.view_settings.exposure = 0.0
    except Exception: pass
    S.cam.data.dof.use_dof = False; S.water = None
    # suelo: plano de 120 m con UV en metros (el adoquín se repite cada 1,5 m)
    cob = _pbr(S, "cobblestone_floor_01", scale=1.0)
    bpy.ops.mesh.primitive_plane_add(size=1, location=(0, 0, 0)); g = bpy.context.object; g.name = "plaza_suelo"
    g.scale = (120, 120, 1); g.data.materials.append(cob)
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    me = g.data; me.uv_layers.active.data.foreach_set("uv", [c for l in me.loops for c in (me.vertices[l.vertex_index].co.x / 1.5, me.vertices[l.vertex_index].co.y / 1.5)])
    props = {}
    lamp = _model("street_lamp_01", "2k"); can = _model("metal_trash_can", "2k"); plant = _model("planter_box_01", "2k")
    props["lamp"] = lamp; props["can"] = can; props["planter"] = plant
    return props
