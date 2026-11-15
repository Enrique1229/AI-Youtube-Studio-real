"""Prototipo: comedia física por niveles animada por código (Blender como módulo, render Cycles en CPU)."""
import sys, math, random, bpy
from mathutils import Vector

LEVEL = int(sys.argv[sys.argv.index("--") + 1]); OUT = sys.argv[sys.argv.index("--") + 2]
ONLY = int(sys.argv[sys.argv.index("--") + 3]) if len(sys.argv) > sys.argv.index("--") + 3 else None
FPS, N = 24, 96
bpy.ops.wm.read_factory_settings(use_empty=True)
sc = bpy.context.scene
sc.render.engine = "CYCLES"; sc.cycles.device = "CPU"; sc.cycles.samples = 10; sc.cycles.use_denoising = True
sc.cycles.max_bounces = 3; sc.render.resolution_x, sc.render.resolution_y = 432, 768; sc.render.fps = FPS
sc.frame_start, sc.frame_end = 1, N; sc.render.image_settings.file_format = "PNG"; sc.render.film_transparent = False
sc.view_settings.view_transform = "Standard"

def mat(name, rgb, rough=0.5, emit=0.0):
    m = bpy.data.materials.new(name); m.use_nodes = True
    b = m.node_tree.nodes["Principled BSDF"]; b.inputs["Base Color"].default_value = (*rgb, 1); b.inputs["Roughness"].default_value = rough
    if emit: b.inputs["Emission Color"].default_value = (*rgb, 1); b.inputs["Emission Strength"].default_value = emit
    return m
M = {"blue": mat("blue", (0.10, 0.38, 0.95), 0.35), "white": mat("white", (1, 1, 1), 0.3), "black": mat("black", (0.02, 0.02, 0.02), 0.2),
     "yellow": mat("yellow", (1.0, 0.78, 0.05), 0.4), "grass": mat("grass", (0.25, 0.62, 0.18), 0.9), "wood": mat("wood", (0.45, 0.27, 0.12), 0.7),
     "water": mat("water", (0.05, 0.45, 0.75), 0.08), "red": mat("red", (0.85, 0.12, 0.10), 0.4), "foam": mat("foam", (0.9, 0.97, 1.0), 0.3)}

def obj(prim, name, m, loc=(0, 0, 0), scale=(1, 1, 1), rot=(0, 0, 0), parent=None, smooth=True, **kw):
    getattr(bpy.ops.mesh, prim)(location=loc, rotation=rot, **kw)
    o = bpy.context.object; o.name = name; o.scale = scale; o.data.materials.append(M[m])
    if smooth:
        for p in o.data.polygons: p.use_smooth = True
    if parent: o.parent = parent
    return o
def empty(name, loc=(0, 0, 0)):
    e = bpy.data.objects.new(name, None); sc.collection.objects.link(e); e.location = loc; return e
def key(o, f, loc=None, rot=None, scale=None, interp="BEZIER"):
    bpy.context.preferences.edit.keyframe_new_interpolation_type = interp
    if loc is not None: o.location = loc; o.keyframe_insert("location", frame=f)
    if rot is not None: o.rotation_euler = rot; o.keyframe_insert("rotation_euler", frame=f)
    if scale is not None: o.scale = scale; o.keyframe_insert("scale", frame=f)

# ---------- mundo ----------
w = bpy.data.worlds.new("w"); sc.world = w; w.use_nodes = True
w.node_tree.nodes["Background"].inputs[0].default_value = (0.50, 0.75, 1.0, 1); w.node_tree.nodes["Background"].inputs[1].default_value = 1.0
sun = bpy.data.objects.new("sun", bpy.data.lights.new("sun", "SUN")); sc.collection.objects.link(sun)
sun.data.energy = 3.5; sun.data.angle = 0.3; sun.rotation_euler = (math.radians(50), 0, math.radians(-35))
obj("primitive_cube_add", "orillaL", "grass", (-32, 0, -1.5), (30, 60, 1.5), smooth=False)
obj("primitive_cube_add", "orillaR", "grass", (32, 0, -1.5), (30, 60, 1.5), smooth=False)
obj("primitive_cube_add", "agua", "water", (0, 0, -1.75), (2.5, 60, 1.5), smooth=False)
M["trunk"] = M["wood"]; M["leaf"] = mat("leaf", (0.12, 0.45, 0.16), 0.8); M["rock"] = mat("rock", (0.5, 0.5, 0.52), 0.9); M["flor"] = mat("flor", (1.0, 0.45, 0.6), 0.5)
random.seed(3)
for i in range(26):   # árboles, rocas y flores para dar profundidad
    side = random.choice((-1, 1)); x = side * random.uniform(3.2, 14); y = random.uniform(2.5, 26); h = random.uniform(1.6, 3.2)
    obj("primitive_cylinder_add", f"tronco{i}", "trunk", (x, y, h * 0.3), (0.16, 0.16, h * 0.3))
    obj("primitive_cone_add", f"copa{i}", "leaf", (x, y, h * 0.6 + h * 0.5), (h * 0.42, h * 0.42, h * 0.5))
for i in range(14):
    side = random.choice((-1, 1)); x = side * random.uniform(2.6, 9); y = random.uniform(-3.5, 9)
    if abs(y) < 1.0: y += 1.6
    obj("primitive_uv_sphere_add", f"roca{i}", "rock" if i % 2 else "flor", (x, y, 0.08), ((0.3, 0.25, 0.18) if i % 2 else (0.12, 0.12, 0.12)), segments=12, ring_count=8)
obj("primitive_cube_add", "muelle", "wood", (-2.6, 0, 0.06), (0.9, 0.5, 0.06), smooth=False)
for i, (x, y, s) in enumerate([(-6.5, 4.5, 1.6), (-4.2, 5.2, 1.1), (5.2, 4.8, 1.8), (7.0, 5.5, 1.2)]):  # colinas/árboles simples
    obj("primitive_uv_sphere_add", f"colina{i}", "grass", (x, y, 0.0), (s, s, s * 0.8))
cam = bpy.data.objects.new("cam", bpy.data.cameras.new("cam")); sc.collection.objects.link(cam); sc.camera = cam
tgt = empty("mira", (-0.5, 0, 0.6)); cam.data.lens = 44; cam.location = (-6.2, -7.6, 3.3)
tc = cam.constraints.new("TRACK_TO"); tc.target = tgt; tc.track_axis = "TRACK_NEGATIVE_Z"; tc.up_axis = "UP_Y"

# ---------- personaje (siempre el mismo modelo) ----------
root = empty("pj"); body = empty("cuerpo"); body.parent = root
obj("primitive_uv_sphere_add", "panza", "blue", (0, 0, 0.55), (0.55, 0.50, 0.58), parent=body)
for sx in (-1, 1):
    obj("primitive_uv_sphere_add", f"ojo{sx}", "white", (0.20 * sx, -0.42, 0.78), (0.15, 0.10, 0.17), parent=body)
    obj("primitive_uv_sphere_add", f"pupila{sx}", "black", (0.21 * sx, -0.51, 0.78), (0.06, 0.04, 0.07), parent=body)
    obj("primitive_uv_sphere_add", f"pie{sx}", "blue", (0.22 * sx, -0.05, 0.07), (0.17, 0.24, 0.09), parent=root)
    obj("primitive_uv_sphere_add", f"brazo{sx}", "blue", (0.56 * sx, 0, 0.55), (0.11, 0.11, 0.22), parent=body)
hat = empty("sombrero"); hat.parent = body; hat.location = (0, 0, 1.08)
obj("primitive_cylinder_add", "ala", "yellow", (0, 0, 0), (0.34, 0.34, 0.025), parent=hat)
obj("primitive_cylinder_add", "copa", "yellow", (0, 0, 0.13), (0.20, 0.20, 0.13), parent=hat)

def hop(f0, x0, x1, z=0.0, h=0.55, dur=10):
    """Salto con anticipación, estirón en el aire y aplastamiento al caer."""
    key(body, f0, scale=(1, 1, 1)); key(root, f0, loc=(x0, 0, z))
    key(body, f0 + 2, scale=(1.18, 1.18, 0.78))                                   # anticipación
    key(root, f0 + 2, loc=(x0, 0, z))
    key(body, f0 + 2 + dur // 2, scale=(0.88, 0.88, 1.22))                         # estirón
    key(root, f0 + 2 + dur // 2, loc=((x0 + x1) / 2, 0, z + h))
    key(root, f0 + 2 + dur, loc=(x1, 0, z))
    key(body, f0 + 2 + dur, scale=(1.25, 1.25, 0.70))                              # aplastamiento
    key(body, f0 + 5 + dur, scale=(1, 1, 1), interp="BACK")
    return f0 + 6 + dur

def splash(f, x, n=22):
    random.seed(7)
    for i in range(n):
        d = obj("primitive_uv_sphere_add", f"gota{i}", "foam", (x, 0, -0.3), (0.001,) * 3, segments=8, ring_count=6)
        a = random.uniform(0, 6.28); r = random.uniform(0.4, 1.5); hgt = random.uniform(1.0, 2.6); s = random.uniform(0.05, 0.13)
        key(d, f - 1, loc=(x, 0, -0.3), scale=(0.001,) * 3)
        key(d, f, loc=(x, 0, -0.2), scale=(s, s, s))
        key(d, f + 7, loc=(x + r * math.cos(a) * 0.5, r * math.sin(a) * 0.5, hgt))
        key(d, f + 16, loc=(x + r * math.cos(a), r * math.sin(a), -0.35), scale=(s * 0.6,) * 3)
        key(d, f + 17, scale=(0.001,) * 3)

if LEVEL == 1:      # camina con toda confianza… y se va al agua; solo queda el sombrero flotando
    f = 6
    for x0, x1 in [(-4.6, -3.9), (-3.9, -3.2), (-3.2, -2.5), (-2.5, -1.75)]: f = hop(f, x0, x1, z=0.12 if x1 > -3.5 else 0.0)
    key(root, f, loc=(-1.75, 0, 0.12)); key(body, f, rot=(0, 0, 0))
    key(root, f + 4, loc=(-1.2, 0, 0.5)); key(body, f + 4, rot=(0, math.radians(25), 0), scale=(0.9, 0.9, 1.15))   # paso al vacío
    key(root, f + 6, loc=(-1.1, 0, 0.5))                                                                           # se queda un instante en el aire
    key(body, f + 6, rot=(0, math.radians(-10), 0), scale=(1.1, 1.1, 0.9))
    key(root, f + 13, loc=(-1.0, 0, -1.8)); key(body, f + 13, scale=(0.85, 0.85, 1.3))                             # cae
    splash(f + 10, -1.0)
    # el sombrero se separa y flota
    hat.parent = None; key(hat, 1, loc=(-4.6, 0, 1.08))
    hx = [(-4.6, 6)]
    for fr in range(6, f + 7, 2):
        sc.frame_set(fr); p = body.matrix_world @ Vector((0, 0, 1.08)); key(hat, fr, loc=tuple(p))
    key(hat, f + 12, loc=(-1.0, 0, 0.9), rot=(0, 0, 0)); key(hat, f + 22, loc=(-1.0, 0, -0.18), rot=(0.15, 0.1, 0.6))
    for i, fr in enumerate(range(f + 30, N + 1, 8)): key(hat, fr, loc=(-1.0 + 0.05 * i, 0, -0.18 + (0.05 if i % 2 else -0.03)), rot=(0.1 * (-1) ** i, 0.08, 0.6 + 0.2 * i))
elif LEVEL == 2:    # cruza por un tablón que se comba y tambalea; llega y celebra
    plank = obj("primitive_cube_add", "tablon", "wood", (0, 0, 0.14), (2.5, 0.22, 0.04), smooth=False)
    f = 6
    xs = [-4.2, -3.3, -2.3, -1.3, -0.3, 0.7, 1.7, 2.7, 3.6]
    for i, (x0, x1) in enumerate(zip(xs, xs[1:])):
        onp = -2.4 < x1 < 2.4
        sag = -0.28 * (1 - (x1 / 2.4) ** 2) if onp else 0.0
        f0 = f; f = hop(f, x0, x1, z=(0.18 + sag) if onp else 0.0, h=0.4, dur=7)
        key(plank, f0 + 9, loc=(0, 0, 0.14 + sag * 0.9), rot=(0, math.radians(4 if i % 2 else -4), 0), interp="BACK")
        key(body, f0 + 9, rot=(0, math.radians(14 if i % 2 else -14), 0))
    key(plank, f + 4, loc=(0, 0, 0.14), rot=(0, 0, 0), interp="ELASTIC"); key(body, f, rot=(0, 0, 0))
    f = hop(f, 3.6, 3.6, h=0.9, dur=8); hop(f, 3.6, 3.6, h=0.6, dur=6)                                  # celebración
else:               # nivel 3: llega remando en una barca, tan tranquilo, y saluda con el sombrero
    boat = empty("barca", (-1.9, 0, -0.16))
    obj("primitive_uv_sphere_add", "casco", "red", (0, 0, 0), (1.05, 0.55, 0.32), parent=boat)
    obj("primitive_cube_add", "hueco", "wood", (0, 0, 0.16), (0.8, 0.4, 0.03), parent=boat, smooth=False)
    remo = obj("primitive_cube_add", "remo", "wood", (0, -0.62, 0.3), (0.05, 0.05, 0.75), rot=(0.9, 0, 0), parent=boat, smooth=False)
    root.parent = boat; root.location = (0, 0, 0.18)
    for i, fr in enumerate(range(1, N + 1, 6)):
        t = (fr - 1) / (N - 1); ease = t * t * (3 - 2 * t)
        key(boat, fr, loc=(-1.9 + 3.6 * ease, 0, -0.16 + (0.04 if i % 2 else -0.02)), rot=(0, math.radians(3 if i % 2 else -3), 0))
        key(remo, fr, rot=(0.9, math.radians(35 if i % 2 else -35), 0))
        key(body, fr, scale=(1, 1, 1.04 if i % 2 else 0.97))
    key(hat, 60, loc=(0, 0, 1.08), rot=(0, 0, 0)); key(hat, 68, loc=(0.25, -0.2, 1.45), rot=(0, math.radians(-40), 0), interp="BACK")
    key(hat, 80, loc=(0.25, -0.2, 1.45), rot=(0, math.radians(-40), 0)); key(hat, 90, loc=(0, 0, 1.08), rot=(0, 0, 0), interp="BACK")

# la cámara sigue al personaje con suavidad (mira a un punto entre él y el centro de la escena)
for fr in range(1, N + 1, 4):
    sc.frame_set(fr); wp = root.matrix_world.translation
    key(tgt, fr, loc=(wp.x * 0.75, 0, max(0.45, min(1.0, wp.z + 0.6))))
frames = [ONLY] if ONLY else range(1, N + 1)
for fr in frames:
    sc.frame_set(fr); sc.render.filepath = f"{OUT}/f{fr:04d}.png"; bpy.ops.render.render(write_still=True)
