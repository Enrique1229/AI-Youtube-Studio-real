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


# (modelo, resolución, x, y, alto_m, giro_deg): reparto en primer plano, medio y fondo. La cámara del ep017 mira a +y desde y=-7.4 y la
# acción (tapa, hombre) está en x∈[-1.3, 1.5], y∈[-0.5, 2]. Se deja libre la franja central detrás de la tapa y los bordes de la acción.
PLAZA_PROPS = [
    ("fire_hydrant", "1k", -1.75, -1.35, 0.80, 25),                 # primer plano izquierdo (desenfocado, encuadra)
    ("planter_box_01", "2k", -1.95, 2.3, 0.75, 0),                  # medio
    ("potted_plant_01", "1k", 2.05, 2.1, 0.95, 40),
    ("WetFloorSign_01", "1k", -1.9, 2.0, 0.62, 28),
    ("metal_trash_can", "2k", -4.6, 8.0, 1.0, 20),            # papeleras: lejos, al fondo (no compiten con la tapa)
    ("planter_box_02", "1k", 1.95, 3.6, 0.80, -8),
    ("utility_box_01", "1k", 2.6, 5.2, 1.35, -12),                  # fondo cercano
    ("modular_street_seating", "1k", -2.7, 5.0, 0.85, 12),
    ("painted_wooden_bench", "1k", 3.1, 7.6, 0.90, -20),
    ("outdoor_table_chair_set_01", "1k", -3.1, 8.8, 1.0, 35),
    ("wooden_barrels_01", "1k", 3.9, 10.5, 0.95, 0),
    ("concrete_road_barrier", "1k", -4.4, 11.0, 0.95, 78),
    ("planter_pot_clay", "1k", -1.9, 6.4, 0.70, 0),
    ("plastic_crate_01", "1k", 1.9, 2.9, 0.34, 20),
    ("wooden_crate_01", "1k", -2.3, 3.4, 0.55, -15),
    ("trashbag", "1k", 2.8, 3.1, 0.50, 60),
    ("cardboard_box_01", "1k", 2.3, 6.1, 0.45, 32),
    ("street_lamp_01", "2k", -2.5, 3.8, 4.6, 0),
    ("street_lamp_02", "1k", 3.4, 8.6, 4.8, 180),
    ("street_lamp_02", "1k", -5.2, 14.5, 4.8, 0),
]


def _mat_simple(S, name, rgb, rough=0.6, metal=0.0):
    k = "pz_" + name
    if k in S.mats: return S.mats[k]
    m = bpy.data.materials.new(k); m.use_nodes = True; b = m.node_tree.nodes["Principled BSDF"]
    b.inputs["Base Color"].default_value = (*rgb, 1); b.inputs["Roughness"].default_value = rough; b.inputs["Metallic"].default_value = metal
    S.mats[k] = m; return m


def _prim(S, prim, name, mat, loc, scale=(1, 1, 1), rot=(0, 0, 0), parent=None, **kw):
    sm = kw.pop("smooth", True)
    o = S.obj(prim, name, "white", loc, scale, rot, parent, sm, **kw); o.data.materials[0] = mat; return o


def build_plaza(S, rot_deg=0, sun_energy=3.0, dress=True):
    """Plaza urbana realista y muy producida: cielo HDRI dresden_square, suelo de adoquín PBR hasta el horizonte, 19 piezas de atrezo
    de Poly Haven (CC0) repartidas en primer plano, medio y fondo, bordillo con calzada y paso de cebra, bolardos, charcos, hojas y palomas
    de primitivas. Sin césped ni parque. Deja solo sol, cámara y objetivo del escenario base. Reutiliza _hdri/_pbr/_model.
    Devuelve {"birds": [...]} (palomas, para animarlas)."""
    import random as _r
    for o in list(S.sc.objects):
        if o.name.startswith("sun") or o is S.cam or o is S.tgt: continue
        bpy.data.objects.remove(o, do_unlink=True)
    _hdri(S, name="dresden_square", strength=1.0, rot_deg=rot_deg)
    sun = bpy.data.objects["sun"]; sun.data.energy = sun_energy; sun.data.color = (1.0, 0.94, 0.84); sun.data.angle = math.radians(1.5)
    sun.rotation_euler = (math.radians(52), 0, math.radians(-28))
    S.sc.view_settings.view_transform = "AgX"
    try: S.sc.view_settings.look = "AgX - Base Contrast"; S.sc.view_settings.exposure = 0.0
    except Exception: pass
    S.cam.data.dof.use_dof = True; S.cam.data.dof.aperture_fstop = 1.4; S.cam.data.dof.focus_distance = 7.4; S.water = None   # profundidad: fondo y primer plano blandos
    # suelo: plano de 120 m con UV en metros (el adoquín se repite cada 1,5 m); calzada de asfalto más allá del bordillo (y > 16)
    cob = _pbr(S, "cobblestone_floor_01", scale=1.0)
    bpy.ops.mesh.primitive_plane_add(size=1, location=(0, 40, 0)); g = bpy.context.object; g.name = "plaza_suelo"
    g.scale = (160, 160, 1); g.data.materials.append(cob)
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    me = g.data; me.uv_layers.active.data.foreach_set("uv", [c for l in me.loops for c in (me.vertices[l.vertex_index].co.x / 1.5, me.vertices[l.vertex_index].co.y / 1.5)])
    asf = S.pmat("asfalto", [(0.3, (0.045, 0.045, 0.05)), (0.7, (0.10, 0.10, 0.105))], scale=45, rough=0.85, bump=0.4)
    curb_m = _mat_simple(S, "bordillo", (0.55, 0.54, 0.51), 0.8)
    bpy.ops.mesh.primitive_plane_add(size=1, location=(0, 66, 0.004)); r = bpy.context.object; r.name = "calzada"; r.scale = (160, 100, 1); r.data.materials.append(asf)
    c = _prim(S, "cube", "bordillo", curb_m, (0, 16.0, 0.08), (80, 0.18, 0.08), smooth=False)
    white = _mat_simple(S, "pintura", (0.80, 0.80, 0.78), 0.7)
    for i in range(-9, 10):                                          # paso de cebra
        _prim(S, "cube", "cebra", white, (i * 0.95, 21.0, 0.008), (0.3, 1.6, 0.003), smooth=False)
    # atrezo
    cols = {}
    for (name, res, x, y, h, rot) in PLAZA_PROPS:
        if not dress: break
        if (name, res) not in cols: cols[(name, res)] = _model(name, res)
        bpy.context.view_layer.update()
        _place_fit(S, cols[(name, res)], (x, y, 0.0), h, math.radians(rot))
    # bolardos de primitivas con banda amarilla (a ambos lados, sin cruzar el centro)
    steel = _mat_simple(S, "bolardo", (0.12, 0.13, 0.15), 0.4, 0.7); band = _mat_simple(S, "banda_amarilla", (0.95, 0.72, 0.05), 0.5)
    for x in (-3.6, -2.4, 2.6, 3.8, 5.0, -4.8):
        _prim(S, "cylinder", "bolardo", steel, (x, 12.6, 0.45), (0.07, 0.07, 0.45), vertices=20)
        _prim(S, "cylinder", "banda", band, (x, 12.6, 0.72), (0.0715, 0.0715, 0.045), vertices=20)
        _prim(S, "uv_sphere", "tapa_bolardo", steel, (x, 12.6, 0.9), (0.07, 0.07, 0.04), segments=16, ring_count=8)
    # charcos con reflejo del cielo
    wet = bpy.data.materials.new("pz_charco"); wet.use_nodes = True; wb = wet.node_tree.nodes["Principled BSDF"]
    wb.inputs["Base Color"].default_value = (0.03, 0.035, 0.04, 1); wb.inputs["Roughness"].default_value = 0.02
    for (x, y, rx, ry) in ((-1.0, 1.4, 0.55, 0.28), (0.4, 3.1, 0.9, 0.4), (-2.0, 4.6, 0.8, 0.35), (1.6, 5.6, 0.7, 0.3), (-0.3, -0.9, 0.45, 0.2)):
        o = _prim(S, "cylinder", "charco", wet, (x, y, 0.006), (rx, ry, 0.002), vertices=40)
    # hojas sueltas
    rnd = _r.Random(11)
    leaf_m = [_mat_simple(S, f"hoja{i}", c, 0.8) for i, c in enumerate(((0.45, 0.22, 0.05), (0.60, 0.33, 0.06), (0.35, 0.28, 0.07), (0.55, 0.12, 0.04)))]
    for i in range(80):
        x, y = rnd.uniform(-3.2, 3.5), rnd.uniform(-1.0, 8.0)
        if ((x + 0.55) ** 2 + y ** 2) < 1.1 ** 2: continue                 # la tapa y su marco quedan limpios
        _prim(S, "uv_sphere", "hoja", rnd.choice(leaf_m), (x, y, 0.006), (rnd.uniform(0.05, 0.09), rnd.uniform(0.03, 0.05), 0.004),
              (0, 0, rnd.uniform(0, 6.28)), segments=8, ring_count=4)
    # palomas de primitivas
    grey = _mat_simple(S, "paloma", (0.42, 0.44, 0.50), 0.8); neck = _mat_simple(S, "paloma_cuello", (0.28, 0.45, 0.42), 0.6)
    beak = _mat_simple(S, "pico", (0.85, 0.55, 0.30), 0.6); dark = _mat_simple(S, "ojo", (0.02, 0.02, 0.02), 0.3)
    birds = []
    for (x, y, yaw) in ((-1.6, 2.7, 140), (-1.15, 3.3, 200), (-0.35, 4.0, 160)):
        e = S.empty("paloma", (x, y, 0.0)); e.rotation_euler = (0, 0, math.radians(yaw))
        _prim(S, "uv_sphere", "p_cuerpo", grey, (0, 0, 0.11), (0.07, 0.12, 0.075), parent=e, segments=16, ring_count=8)
        _prim(S, "uv_sphere", "p_cuello", neck, (0, 0.10, 0.17), (0.05, 0.05, 0.05), parent=e, segments=12, ring_count=8)
        _prim(S, "uv_sphere", "p_cabeza", grey, (0, 0.14, 0.205), (0.04, 0.045, 0.04), parent=e, segments=12, ring_count=8)
        _prim(S, "cone", "p_pico", beak, (0, 0.19, 0.20), (0.012, 0.012, 0.02), (math.radians(-90), 0, 0), parent=e, vertices=8, radius1=1.0, radius2=0.0, depth=2.0)
        _prim(S, "uv_sphere", "p_cola", grey, (0, -0.15, 0.115), (0.04, 0.09, 0.012), parent=e, segments=10, ring_count=6)
        wings = [_prim(S, "uv_sphere", "p_ala", grey, (sx * 0.06, 0.0, 0.14), (0.015, 0.10, 0.06), parent=e, segments=10, ring_count=6) for sx in (-1, 1)]
        e["wings"] = [w.name for w in wings]; birds.append(e)
    return {"birds": birds, "cols": cols}
