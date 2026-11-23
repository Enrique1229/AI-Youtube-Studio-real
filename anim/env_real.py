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
    ("WetFloorSign_01", "1k", -2.4, 3.6, 0.62, 28),
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


# ------------------------------------------------------------------ azotea urbana (episodio 19)
# (modelo, resolución, x, y, alto_m, giro_deg). La cámara del ep019 mira a +y desde y≈-7 con un cuadro de ~3 m de ancho centrado en la acción
# (x∈[-1.5, 2.5], y∈[-0.5, 3]); el atrezo se reparte a los lados, al medio y al fondo (nada delante, nada en el 15 % inferior).
ROOFTOP_PROPS = [
    ("exterior_aircon_unit", "1k", -3.0, 2.9, 0.93, 12),            # medio izquierda
    ("exterior_aircon_unit", "1k", 6.3, 5.2, 0.93, 100),            # fondo derecha
    ("modular_airduct_rectangular_01", "1k", 1.0, 7.9, 1.0, 0),     # conducto largo al fondo
    ("modular_industrial_pipes_01", "1k", -3.6, 6.4, 1.95, 8),      # tuberías verticales al fondo
    ("plastic_crate_01", "1k", -2.15, 1.5, 0.26, 24),
    ("plastic_crate_01", "1k", -2.2, 1.55, 0.26, -10),              # segunda caja apilada (z se corrige abajo)
    ("barrel_03", "1k", -2.7, 4.6, 0.93, 0),
    ("barrel_03", "1k", 4.9, 3.6, 0.93, 40),
    ("cardboard_box_01", "1k", -2.35, 0.55, 0.34, 32),
    ("metal_toolbox", "1k", -3.15, 2.0, 0.35, -25),
    ("ladder_sectioned_01", "1k", 3.6, 8.6, 2.13, 90),              # escalera apoyada junto a la caseta
    ("potted_plant_01", "1k", -4.0, 3.4, 1.0, 20),
    ("planter_pot_clay", "1k", 0.9, 5.6, 0.24, 0),
    ("planter_pot_clay", "1k", 1.2, 5.75, 0.20, 40),
    ("outdoor_table_chair_set_01", "1k", 5.2, 1.9, 0.86, 15),
]


def build_rooftop(S, rot_deg=90, sun_energy=3.0, tank=(3.0, 1.8), focus=7.2):
    """Azotea urbana muy producida: HDRI rooftop_day, suelo de hormigón desgastado PBR (losa finita con parapeto y barandilla), 15 piezas de
    atrezo de Poly Haven (CC0) en primer plano, medio y fondo, depósito de agua de madera de primitivas (con escalera de peldaños en su cara
    -x, para trepar), caseta de acceso, antenas, tendedero con sábanas, charcos, hojas, sumidero y parches de brea; profundidad por DOF.
    Reutiliza _hdri/_pbr/_model. Devuelve {"sheets": [empties de bisagra de las sábanas], "tank": (cx, cy, R, z0, z1), "rungs": [z...], "tank_x_face": x}."""
    import random as _r
    for o in list(S.sc.objects):
        if o.name.startswith("sun") or o is S.cam or o is S.tgt: continue
        bpy.data.objects.remove(o, do_unlink=True)
    _hdri(S, name="rooftop_day", strength=1.0, rot_deg=rot_deg)
    # el HDRI es un aparcamiento nublado: la luz y los reflejos son suyos, pero a la cámara se le muestra un cielo azul de día (cúpula que solo
    # existe para los rayos de cámara), un skyline de edificios lejanos (primitivas) y el vacío de la calle bajo el parapeto
    sk = bpy.data.materials.new("az_cielo"); sk.use_nodes = True; nt = sk.node_tree; N_, L_ = nt.nodes, nt.links
    for n_ in list(N_): N_.remove(n_)
    out = N_.new("ShaderNodeOutputMaterial"); mix = N_.new("ShaderNodeMixShader"); tr = N_.new("ShaderNodeBsdfTransparent"); em = N_.new("ShaderNodeEmission")
    tc = N_.new("ShaderNodeTexCoord"); sp = N_.new("ShaderNodeSeparateXYZ"); L_.new(tc.outputs["Object"], sp.inputs[0])
    gz = N_.new("ShaderNodeMapRange"); gz.inputs[1].default_value = 0.0; gz.inputs[2].default_value = 0.30; L_.new(sp.outputs["Z"], gz.inputs[0])
    rp = N_.new("ShaderNodeValToRGB"); rp.color_ramp.elements[0].color = (0.62, 0.80, 1.0, 1); rp.color_ramp.elements[1].color = (0.10, 0.38, 0.95, 1); L_.new(gz.outputs[0], rp.inputs[0])
    nz = N_.new("ShaderNodeTexNoise"); nz.inputs["Scale"].default_value = 3.5; nz.inputs["Detail"].default_value = 5.0; L_.new(tc.outputs["Object"], nz.inputs["Vector"])
    cr = N_.new("ShaderNodeValToRGB"); cr.color_ramp.elements[0].position = 0.52; cr.color_ramp.elements[1].position = 0.68; L_.new(nz.outputs["Fac"], cr.inputs[0])
    cm = N_.new("ShaderNodeMix"); cm.data_type = "RGBA"; cm.inputs[7].default_value = (1, 1, 1, 1); L_.new(cr.outputs["Color"], cm.inputs[0]); L_.new(rp.outputs["Color"], cm.inputs[6])
    L_.new(cm.outputs[2], em.inputs["Color"]); em.inputs["Strength"].default_value = 0.9
    mk = N_.new("ShaderNodeMapRange"); mk.inputs[1].default_value = -0.01; mk.inputs[2].default_value = 0.0; L_.new(sp.outputs["Z"], mk.inputs[0])
    lp = N_.new("ShaderNodeLightPath"); ml = N_.new("ShaderNodeMath"); ml.operation = "MULTIPLY"; L_.new(mk.outputs[0], ml.inputs[0]); L_.new(lp.outputs["Is Camera Ray"], ml.inputs[1])
    L_.new(ml.outputs[0], mix.inputs[0]); L_.new(tr.outputs[0], mix.inputs[1]); L_.new(em.outputs[0], mix.inputs[2]); L_.new(mix.outputs[0], out.inputs[0])
    dome = _prim(S, "uv_sphere", "cielo", sk, (0, 0, 0), (1500, 1500, 1500), segments=48, ring_count=24, smooth=True)
    rnd0 = _r.Random(5)
    for k in range(40):                                                       # skyline lejano (copas entre 4 y 11 m sobre la azotea: el cielo queda libre)
        x = -330 + k * 16.0 + rnd0.uniform(-5, 5); y = rnd0.uniform(130, 230); w = rnd0.uniform(14, 30); dpt = rnd0.uniform(14, 28); top = rnd0.uniform(3.0, 9.0)
        c = rnd0.uniform(0.20, 0.30); hz = _mat_simple(S, f"edif{k % 5}", (c * 0.92, c * 0.97, min(1.0, c * 1.10)), 0.9)
        _prim(S, "cube", "edificio", hz, (x, y, (top - 15.0) / 2), (w / 2, dpt / 2, (top + 15.0) / 2), smooth=False)
        if rnd0.random() < 0.5: _prim(S, "cylinder", "edificio_antena", hz, (x + w * 0.2, y, top + 1.5), (0.15, 0.15, 1.5), vertices=6)
    _prim(S, "cube", "calle_lejos", _mat_simple(S, "calle_lejos", (0.30, 0.32, 0.34), 0.9), (0, 600, -15.2), (1500, 1200, 0.2), smooth=False)
    sun = bpy.data.objects["sun"]; sun.data.energy = sun_energy; sun.data.color = (1.0, 0.95, 0.86); sun.data.angle = math.radians(2.0)
    sun.rotation_euler = (math.radians(48), 0, math.radians(-30))
    S.sc.view_settings.view_transform = "AgX"
    try: S.sc.view_settings.look = "AgX - Base Contrast"; S.sc.view_settings.exposure = 0.0
    except Exception: pass
    S.cam.data.dof.use_dof = True; S.cam.data.dof.aperture_fstop = 2.2; S.cam.data.dof.focus_distance = focus; S.water = None; S.cam.data.clip_end = 4000
    # ---- suelo: losa de 18 x 19 m con UV en metros (la textura se repite cada 2 m)
    conc = _pbr(S, "concrete_floor_worn_001", res="1k", scale=1.0)
    bpy.ops.mesh.primitive_plane_add(size=1, location=(0, 0.25, 0)); g = bpy.context.object; g.name = "azotea_suelo"
    g.scale = (18, 19, 1); g.data.materials.append(conc)
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    me = g.data; me.uv_layers.active.data.foreach_set("uv", [c for l in me.loops for c in (me.vertices[l.vertex_index].co.x / 2.0, me.vertices[l.vertex_index].co.y / 2.0)])
    # ---- parapeto de obra al fondo y a los lados, con albardilla y barandilla de tubo encima
    wall_m = _pbr(S, "beige_wall_001", res="2k", scale=2.0); cap_m = _mat_simple(S, "albardilla", (0.62, 0.60, 0.56), 0.8)
    steel = _mat_simple(S, "barandilla", (0.42, 0.45, 0.48), 0.4, 0.8); dark = _mat_simple(S, "brea", (0.11, 0.11, 0.115), 0.9)
    _prim(S, "cube", "parapeto", wall_m, (0, 9.35, 0.45), (9.0, 0.17, 0.45), smooth=False)
    _prim(S, "cube", "albardilla", cap_m, (0, 9.35, 0.92), (9.0, 0.24, 0.035), smooth=False)
    for sx in (-1, 1):
        _prim(S, "cube", "parapeto_l", wall_m, (sx * 8.85, 0.25, 0.45), (0.17, 9.35, 0.45), smooth=False)
        _prim(S, "cube", "albardilla_l", cap_m, (sx * 8.85, 0.25, 0.92), (0.24, 9.35, 0.035), smooth=False)
    for i in range(-7, 8):                                               # postes y tubos de la barandilla (fondo)
        _prim(S, "cylinder", "poste", steel, (i * 1.2, 9.35, 1.22), (0.022, 0.022, 0.30), vertices=10)
    for z in (1.12, 1.50):
        _prim(S, "cylinder", "tubo", steel, (0, 9.35, z), (0.018, 0.018, 9.0), (0, math.radians(90), 0), vertices=10)
    _prim(S, "cube", "bordillo_fondo", cap_m, (0, 9.0, 0.04), (9.0, 0.12, 0.04), smooth=False)       # rodapié de hormigón
    # ---- caseta de acceso a la escalera (fondo izquierdo-centro) con puerta metálica
    shed_m = _pbr(S, "beige_wall_001", res="2k", scale=1.5)
    _prim(S, "cube", "caseta", shed_m, (-4.6, 8.3, 1.25), (1.5, 0.95, 1.25), smooth=False)
    _prim(S, "cube", "caseta_techo", cap_m, (-4.6, 8.3, 2.53), (1.62, 1.06, 0.045), smooth=False)
    _prim(S, "cube", "caseta_puerta", _mat_simple(S, "puerta", (0.18, 0.30, 0.34), 0.5, 0.5), (-4.6, 7.34, 0.95), (0.42, 0.03, 0.95), smooth=False)
    _prim(S, "cube", "caseta_marco", steel, (-4.6, 7.33, 0.95), (0.47, 0.025, 1.0), smooth=False)
    _prim(S, "uv_sphere", "caseta_pomo", steel, (-4.35, 7.30, 0.95), (0.03, 0.03, 0.03), segments=10, ring_count=6)
    # ---- depósito de agua de madera de primitivas (el del nivel 120): cuerpo, aros, tapa cónica, plinto y escalera de peldaños en la cara -x
    tx, ty = tank; TR, TZ0, TZ1 = 1.0, 0.25, 3.1
    planks = _pbr(S, "brown_planks_03", res="1k", scale=3.0); rust = _mat_simple(S, "aro_oxido", (0.14, 0.10, 0.08), 0.6, 0.8)
    _prim(S, "cylinder", "tank_plinto", cap_m, (tx, ty, TZ0 / 2), (TR + 0.07, TR + 0.07, TZ0 / 2), vertices=48)
    body = _prim(S, "cylinder", "tank_cuerpo", planks, (tx, ty, (TZ0 + TZ1) / 2), (TR, TR, (TZ1 - TZ0) / 2), vertices=48)
    for z in (0.55, 1.15, 1.75, 2.35, 2.9): _prim(S, "cylinder", "tank_aro", rust, (tx, ty, z), (TR + 0.025, TR + 0.025, 0.035), vertices=48)
    _prim(S, "cone", "tank_tapa", planks, (tx, ty, TZ1 + 0.28), (TR + 0.08, TR + 0.08, 0.28), vertices=48, radius1=1.0, radius2=0.0, depth=2.0)
    rails_y = (ty - 0.24, ty + 0.24); rungs = []
    for ry in rails_y:
        xf = tx - math.sqrt(TR ** 2 - (ry - ty) ** 2) - 0.06
        _prim(S, "cylinder", "tank_larguero", steel, (xf, ry, (0.4 + TZ1 - 0.05) / 2), (0.02, 0.02, (TZ1 - 0.05 - 0.4) / 2), vertices=10)
    z = 0.55
    while z < TZ1 - 0.1:
        xf = tx - math.sqrt(TR ** 2 - 0.24 ** 2) - 0.06
        _prim(S, "cylinder", "tank_peldano", steel, (xf, ty, z), (0.016, 0.016, 0.24), (math.radians(90), 0, 0), vertices=8); rungs.append(z); z += 0.30
    for k in range(4):                                                    # soportes de la escalera
        for ry in rails_y:
            xf = tx - math.sqrt(TR ** 2 - (ry - ty) ** 2) - 0.06
            _prim(S, "cylinder", "tank_soporte", steel, (xf + 0.03, ry, 0.7 + k * 0.8), (0.012, 0.012, 0.03), (0, math.radians(90), 0), vertices=6)
    # ---- tendedero con dos sábanas (bisagras animables) y pinzas
    pole_m = _mat_simple(S, "poste_tendedero", (0.30, 0.30, 0.33), 0.5, 0.7)
    LY, LZ = 3.7, 2.5
    for x in (-3.6, 1.6): _prim(S, "cylinder", "poste_tend", pole_m, (x, LY, LZ / 2 + 0.05), (0.03, 0.03, LZ / 2 + 0.05), vertices=10)
    _prim(S, "cylinder", "cuerda", _mat_simple(S, "cuerda", (0.85, 0.85, 0.8), 0.7), (-1.0, LY, LZ), (0.006, 0.006, 2.6), (0, math.radians(90), 0), vertices=6)
    sheets = []
    for x, w_, col in ((-2.4, 1.15, (0.93, 0.93, 0.90)), (-0.9, 1.0, (0.62, 0.78, 0.92))):
        hg = S.empty("sabana_bisagra", (x, LY, LZ)); sm = _mat_simple(S, f"sabana{int(x*10)}", col, 0.9)
        _prim(S, "cube", "sabana", sm, (0, 0, -0.62), (w_ / 2, 0.012, 0.62), parent=hg, smooth=False)
        _prim(S, "cube", "sabana_franja", _mat_simple(S, "franja_sab", (0.85, 0.30, 0.25), 0.9), (0, -0.002, -0.12), (w_ / 2 + 0.001, 0.0125, 0.045), parent=hg, smooth=False)
        for sx in (-0.4, 0.4): _prim(S, "cube", "pinza", _mat_simple(S, "pinza", (0.9, 0.7, 0.1), 0.6), (sx * w_, 0, -0.03), (0.02, 0.02, 0.04), parent=hg, smooth=False)
        sheets.append(hg)
    # ---- antenas de televisión (mástil + varillas) y chimeneas de ventilación
    for (x, y, h, yaw) in ((-5.2, 7.8, 3.4, 20), (4.2, 8.0, 2.8, -35), (7.0, 3.0, 3.1, 70)):
        e = S.empty("antena", (x, y, 0.0)); e.rotation_euler = (0, 0, math.radians(yaw))
        _prim(S, "cylinder", "mastil", steel, (0, 0, h / 2), (0.022, 0.022, h / 2), parent=e, vertices=8)
        _prim(S, "cylinder", "antena_base", cap_m, (0, 0, 0.06), (0.16, 0.16, 0.06), parent=e, vertices=14)
        _prim(S, "cylinder", "antena_eje", steel, (0.0, 0, h - 0.5), (0.012, 0.012, 0.5), (math.radians(90), 0, 0), parent=e, vertices=6)
        for i in range(6):
            _prim(S, "cylinder", "antena_vara", steel, (0, -0.42 + i * 0.17, h - 0.5), (0.008, 0.008, 0.30 - 0.03 * i), (0, math.radians(90), 0), parent=e, vertices=6)
    for (x, y, h) in ((3.2, 7.0, 1.0), (-5.6, 3.6, 0.7)):                # respiraderos
        _prim(S, "cylinder", "respiradero", steel, (x, y, h / 2), (0.11, 0.11, h / 2), vertices=16)
        _prim(S, "cone", "respiradero_tapa", steel, (x, y, h + 0.07), (0.20, 0.20, 0.07), vertices=16, radius1=1.0, radius2=0.0, depth=2.0)
    # ---- atrezo escaneado (instancias de modelos CC0)
    cols = {}
    for i, (name, res, x, y, h, rot) in enumerate(ROOFTOP_PROPS):
        if (name, res) not in cols: cols[(name, res)] = _model(name, res)
        bpy.context.view_layer.update()
        z0 = 0.26 if (name == "plastic_crate_01" and i > 0 and ROOFTOP_PROPS[i - 1][0] == "plastic_crate_01") else 0.0
        _place_fit(S, cols[(name, res)], (x, y, z0), h, math.radians(rot))
    # ---- detalles pequeños: parches de brea, sumidero, charcos, hojas, grietas de pintura
    for (x, y, rx, ry, rz) in ((-1.5, 2.3, 0.7, 0.4, 10), (1.3, 3.2, 0.6, 0.35, -20), (0.2, 5.0, 1.0, 0.45, 5), (-3.2, 0.8, 0.5, 0.3, 40)):
        _prim(S, "cylinder", "brea", dark, (x, y, 0.003), (rx, ry, 0.0015), (0, 0, math.radians(rz)), vertices=28)
    _prim(S, "cylinder", "sumidero", _mat_simple(S, "sumidero", (0.10, 0.10, 0.11), 0.5, 0.8), (-0.35, 6.3, 0.012), (0.17, 0.17, 0.012), vertices=24)
    for i in range(4): _prim(S, "cube", "sumidero_reja", steel, (-0.35, 6.3, 0.026), (0.15, 0.012, 0.004), (0, 0, math.radians(i * 45)), smooth=False)
    wet = bpy.data.materials.new("az_charco"); wet.use_nodes = True; wb = wet.node_tree.nodes["Principled BSDF"]
    wb.inputs["Base Color"].default_value = (0.03, 0.035, 0.04, 1); wb.inputs["Roughness"].default_value = 0.02
    for (x, y, rx, ry) in ((-0.6, 2.8, 0.55, 0.25), (1.0, 4.2, 0.8, 0.30), (-1.6, 5.8, 0.7, 0.25), (0.35, 0.6, 0.3, 0.15)):
        _prim(S, "cylinder", "charco", wet, (x, y, 0.005), (rx, ry, 0.002), vertices=36)
    rnd = _r.Random(19); leaf_m = [_mat_simple(S, f"az_hoja{i}", c, 0.8) for i, c in enumerate(((0.45, 0.22, 0.05), (0.60, 0.33, 0.06), (0.35, 0.28, 0.07)))]
    for i in range(60):
        x, y = rnd.uniform(-4.0, 4.5), rnd.uniform(-0.3, 8.0)
        if math.hypot(x - tx, y - ty) < 1.3: continue
        _prim(S, "uv_sphere", "hoja", rnd.choice(leaf_m), (x, y, 0.005), (rnd.uniform(0.04, 0.08), rnd.uniform(0.025, 0.045), 0.003), (0, 0, rnd.uniform(0, 6.28)), segments=8, ring_count=4)
    for (x, y) in ((-2.0, 3.3), (2.0, 6.0)):                              # cables sueltos y trozos de cinta de aviso
        _prim(S, "cylinder", "cable", _mat_simple(S, "cable", (0.02, 0.02, 0.02), 0.6), (x, y, 0.012), (0.012, 0.012, 0.9), (math.radians(90), 0, math.radians(rnd.uniform(0, 180))), vertices=6)
    return {"sheets": sheets, "tank": (tx, ty, TR, TZ0, TZ1), "rungs": rungs, "tank_x_face": tx - TR - 0.06, "tank_body": body}
