"""kit.py — biblioteca de animación por código para comedia física por niveles (Blender).

Se usa desde un episodio (anim/episodes/epNNN.py). Funciona con Blender como módulo (`pip install bpy`, Python 3.13)
o dentro de Blender: `blender -b -P anim/run_level.py -- <episodio> <nivel> <salida>`.

Idea central: el episodio describe ACCIONES (saltar hasta x, caer al agua, celebrar…) y el kit pone los fotogramas
clave con principios de animación (anticipación, estirar y encoger, rebote) y anota cada sonido en el fotograma exacto.
"""
import json, math, os, random
import bpy
from mathutils import Vector

FPS = 24
PALETTE = {"blue": (0.10, 0.38, 0.95), "purple": (0.55, 0.20, 0.85), "orange": (1.0, 0.45, 0.08), "white": (1, 1, 1),
           "black": (0.02, 0.02, 0.02), "yellow": (1.0, 0.78, 0.05), "grass": (0.25, 0.62, 0.18), "wood": (0.45, 0.27, 0.12),
           "water": (0.05, 0.45, 0.75), "red": (0.85, 0.12, 0.10), "foam": (0.9, 0.97, 1.0), "leaf": (0.12, 0.45, 0.16),
           "rock": (0.5, 0.5, 0.52), "pink": (1.0, 0.45, 0.6), "mud": (0.36, 0.25, 0.16), "metal": (0.6, 0.62, 0.66), "gold": (1.0, 0.72, 0.1)}


class Stage:
    """Escenario + línea de tiempo. `self.f` es el fotograma actual; cada acción lo hace avanzar."""

    def __init__(self, env="rio", res=(432, 768), samples=10, engine=None):
        bpy.ops.wm.read_factory_settings(use_empty=True)
        self.sc = sc = bpy.context.scene
        self.f, self.cues, self.mats, self.actors = 1, [], {}, []
        engine = engine or os.environ.get("STUDIO_ENGINE", "CYCLES")
        sc.render.engine = engine
        if engine == "CYCLES":
            sc.cycles.device = os.environ.get("STUDIO_DEVICE", "CPU"); sc.cycles.samples = samples
            sc.cycles.use_denoising = True; sc.cycles.max_bounces = 3
        sc.render.resolution_x, sc.render.resolution_y = res
        sc.render.fps = FPS; sc.render.image_settings.file_format = "PNG"; sc.view_settings.view_transform = "Standard"
        w = bpy.data.worlds.new("w"); sc.world = w; w.use_nodes = True
        bg = w.node_tree.nodes["Background"]; bg.inputs[0].default_value = (0.50, 0.75, 1.0, 1); bg.inputs[1].default_value = 1.0
        sun = bpy.data.objects.new("sun", bpy.data.lights.new("sun", "SUN")); sc.collection.objects.link(sun)
        sun.data.energy = 3.5; sun.data.angle = 0.3; sun.rotation_euler = (math.radians(50), 0, math.radians(-35))
        self.cam = bpy.data.objects.new("cam", bpy.data.cameras.new("cam")); sc.collection.objects.link(self.cam); sc.camera = self.cam
        self.tgt = self.empty("mira", (-0.5, 0, 0.6)); self.cam.data.lens = 44; self.cam.location = (-6.2, -7.6, 3.3)
        tc = self.cam.constraints.new("TRACK_TO"); tc.target = self.tgt; tc.track_axis = "TRACK_NEGATIVE_Z"; tc.up_axis = "UP_Y"
        getattr(self, "env_" + env)()

    # ---------- utilidades ----------
    def mat(self, name, rough=0.5):
        if name not in self.mats:
            m = bpy.data.materials.new(name); m.use_nodes = True
            b = m.node_tree.nodes["Principled BSDF"]; b.inputs["Base Color"].default_value = (*PALETTE[name], 1)
            b.inputs["Roughness"].default_value = 0.08 if name == "water" else rough
            self.mats[name] = m
        return self.mats[name]

    def obj(self, prim, name, color, loc=(0, 0, 0), scale=(1, 1, 1), rot=(0, 0, 0), parent=None, smooth=True, **kw):
        getattr(bpy.ops.mesh, "primitive_" + prim + "_add")(location=loc, rotation=rot, **kw)
        o = bpy.context.object; o.name = name; o.scale = scale; o.data.materials.append(self.mat(color))
        if smooth:
            for p in o.data.polygons: p.use_smooth = True
        if parent: o.parent = parent
        return o

    def empty(self, name, loc=(0, 0, 0), parent=None):
        e = bpy.data.objects.new(name, None); self.sc.collection.objects.link(e); e.location = loc
        if parent: e.parent = parent
        return e

    def key(self, o, f=None, loc=None, rot=None, scale=None, interp="BEZIER"):
        f = self.f if f is None else f
        bpy.context.preferences.edit.keyframe_new_interpolation_type = interp
        if loc is not None: o.location = loc; o.keyframe_insert("location", frame=f)
        if rot is not None: o.rotation_euler = rot; o.keyframe_insert("rotation_euler", frame=f)
        if scale is not None: o.scale = scale; o.keyframe_insert("scale", frame=f)

    def cue(self, kind, f=None, vol=0):
        self.cues.append({"t": round(((self.f if f is None else f) - 1) / FPS, 3), "type": kind, "vol": vol})

    def wait(self, n): self.f += n

    # ---------- escenarios ----------
    def env_rio(self):
        self.obj("cube", "orillaL", "grass", (-32, 0, -1.5), (30, 60, 1.5), smooth=False)
        self.obj("cube", "orillaR", "grass", (32, 0, -1.5), (30, 60, 1.5), smooth=False)
        self.obj("cube", "lecho", "mud", (0, 0, -2.6), (2.5, 60, 1.5), smooth=False)
        self.water = self.obj("cube", "agua", "water", (0, 0, -1.75), (2.5, 60, 1.5), smooth=False)
        self.obj("cube", "muelle", "wood", (-2.6, 0, 0.06), (0.9, 0.5, 0.06), smooth=False)
        random.seed(3)
        for i in range(26):
            side = random.choice((-1, 1)); x = side * random.uniform(3.2, 14); y = random.uniform(2.5, 26); h = random.uniform(1.6, 3.2)
            self.obj("cylinder", f"tronco{i}", "wood", (x, y, h * 0.3), (0.16, 0.16, h * 0.3))
            self.obj("cone", f"copa{i}", "leaf", (x, y, h * 1.1), (h * 0.42, h * 0.42, h * 0.5))
        for i in range(14):
            side = random.choice((-1, 1)); x = side * random.uniform(2.6, 9); y = random.uniform(-3.5, 9)
            if abs(y) < 1.0: y += 1.6
            self.obj("uv_sphere", f"deco{i}", "rock" if i % 2 else "pink", (x, y, 0.08), ((0.3, 0.25, 0.18) if i % 2 else (0.12, 0.12, 0.12)), segments=12, ring_count=8)

    # ---------- efectos ----------
    def splash(self, x, y=0, z=-0.3, n=22, big=1.0):
        self.cue("splash")
        rnd = random.Random(int(x * 100) + self.f)
        for i in range(n):
            d = self.obj("uv_sphere", "gota", "foam", (x, y, z), (0.001,) * 3, segments=8, ring_count=6)
            a = rnd.uniform(0, 6.28); r = rnd.uniform(0.4, 1.5) * big; hgt = rnd.uniform(1.0, 2.6) * big; s = rnd.uniform(0.05, 0.13) * big
            self.key(d, self.f - 1, loc=(x, y, z), scale=(0.001,) * 3); self.key(d, self.f, loc=(x, y, z + 0.1), scale=(s, s, s))
            self.key(d, self.f + 7, loc=(x + r * math.cos(a) * 0.5, y + r * math.sin(a) * 0.5, z + hgt))
            self.key(d, self.f + 16, loc=(x + r * math.cos(a), y + r * math.sin(a), z - 0.05), scale=(s * 0.6,) * 3)
            self.key(d, self.f + 17, scale=(0.001,) * 3)

    def follow(self, actor, n_frames, weight=0.75):
        """La cámara mira a un punto entre el actor y el centro de la escena."""
        for fr in range(1, n_frames + 1, 4):
            self.sc.frame_set(fr); wp = actor.root.matrix_world.translation
            self.key(self.tgt, fr, loc=(wp.x * weight, 0, max(0.45, min(1.0, wp.z + 0.6))))

    def actor(self, color="blue", hat="bombin", x=0.0, size=1.0):
        a = Actor(self, color, hat, x, size); self.actors.append(a); return a

    def render(self, out, only=None):
        n = self.f + 10
        self.sc.frame_start, self.sc.frame_end = 1, n
        os.makedirs(out, exist_ok=True)
        json.dump({"frames": n, "fps": FPS, "cues": self.cues}, open(os.path.join(out, "level.json"), "w"), indent=1)
        for fr in ([only] if only else range(1, n + 1)):
            self.sc.frame_set(fr); self.sc.render.filepath = os.path.join(out, f"f{fr:04d}.png"); bpy.ops.render.render(write_still=True)
        return n


class Actor:
    """Personaje de plastilina: cuerpo, ojos con párpados, pies, brazos con hombro articulado y sombrero."""

    def __init__(self, st, color, hat, x, size):
        self.st, s = st, st
        self.root = s.empty("pj", (x, 0, 0)); self.root.scale = (size,) * 3
        self.body = s.empty("cuerpo", parent=self.root)
        s.obj("uv_sphere", "panza", color, (0, 0, 0.55), (0.55, 0.50, 0.58), parent=self.body)
        self.lids, self.pupils, self.arms = [], [], []
        for sx in (-1, 1):
            s.obj("uv_sphere", "ojo", "white", (0.20 * sx, -0.42, 0.78), (0.15, 0.10, 0.17), parent=self.body)
            self.pupils.append(s.obj("uv_sphere", "pupila", "black", (0.21 * sx, -0.51, 0.78), (0.06, 0.04, 0.07), parent=self.body))
            lid = s.obj("uv_sphere", "parpado", color, (0.20 * sx, -0.425, 0.80), (0.158, 0.108, 0.001), parent=self.body); self.lids.append(lid)
            s.obj("uv_sphere", "pie", color, (0.22 * sx, -0.05, 0.07), (0.17, 0.24, 0.09), parent=self.root)
            sh = s.empty("hombro", (0.50 * sx, 0, 0.62), parent=self.body); self.arms.append(sh)
            s.obj("uv_sphere", "brazo", color, (0.10 * sx, 0, -0.20), (0.10, 0.10, 0.24), parent=sh)
            s.obj("uv_sphere", "mano", color, (0.12 * sx, 0, -0.42), (0.12, 0.12, 0.12), parent=sh)
        self.hat = s.empty("sombrero", (0, 0, 1.08), parent=self.body)
        if hat == "bombin":
            s.obj("cylinder", "ala", "yellow", (0, 0, 0), (0.34, 0.34, 0.025), parent=self.hat)
            s.obj("cylinder", "copa", "yellow", (0, 0, 0.13), (0.20, 0.20, 0.13), parent=self.hat)
        elif hat == "corona":
            s.obj("cylinder", "aro", "gold", (0, 0, 0.05), (0.30, 0.30, 0.07), parent=self.hat, smooth=False, vertices=10)
            for i in range(5):
                a = i * 1.2566; s.obj("cone", "pico", "gold", (0.26 * math.cos(a), 0.26 * math.sin(a), 0.20), (0.07, 0.07, 0.12), parent=self.hat)
        self.x, self.z = x, 0.0

    # --- gestos ---
    def arms_to(self, deg, f=None, interp="BEZIER"):
        """0 = brazos caídos; 150 = arriba (celebrar); negativo = hacia atrás."""
        for sx, sh in zip((-1, 1), self.arms): self.st.key(sh, f, rot=(0, math.radians(-deg * sx), 0), interp=interp)

    def blink(self, f=None):
        f = self.st.f if f is None else f
        for lid in self.lids:
            self.st.key(lid, f - 1, scale=(0.158, 0.108, 0.001)); self.st.key(lid, f + 1, scale=(0.158, 0.108, 0.175))
            self.st.key(lid, f + 3, scale=(0.158, 0.108, 0.175)); self.st.key(lid, f + 5, scale=(0.158, 0.108, 0.001))

    def look(self, dx=0.0, dz=0.0, f=None):
        for sx, p in zip((-1, 1), self.pupils): self.st.key(p, f, loc=(0.21 * sx + dx, -0.51, 0.78 + dz))

    def tilt(self, deg, f=None, interp="BEZIER"): self.st.key(self.body, f, rot=(0, math.radians(deg), 0), interp=interp)

    # --- acciones (avanzan el tiempo) ---
    def hop_to(self, x, z=None, h=0.55, dur=10, sound="boing"):
        s, f0 = self.st, self.st.f
        z1 = self.z if z is None else z
        s.key(self.body, f0, scale=(1, 1, 1)); s.key(self.root, f0, loc=(self.x, 0, self.z)); self.arms_to(10, f0)
        s.key(self.body, f0 + 2, scale=(1.18, 1.18, 0.78)); s.key(self.root, f0 + 2, loc=(self.x, 0, self.z)); self.arms_to(-25, f0 + 2)
        if sound: s.cue(sound, f0 + 2, vol=-6)
        mid = f0 + 2 + dur // 2
        s.key(self.body, mid, scale=(0.88, 0.88, 1.22)); s.key(self.root, mid, loc=((self.x + x) / 2, 0, max(self.z, z1) + h)); self.arms_to(95, mid)
        end = f0 + 2 + dur
        s.key(self.root, end, loc=(x, 0, z1)); s.key(self.body, end, scale=(1.25, 1.25, 0.70)); self.arms_to(40, end)
        s.key(self.body, end + 3, scale=(1, 1, 1), interp="BACK"); self.arms_to(10, end + 3)
        self.x, self.z = x, z1; s.f = end + 4

    def walk_to(self, x, steps=None, **kw):
        n = steps or max(1, round(abs(x - self.x) / 0.75)); x0 = self.x
        for i in range(1, n + 1): self.hop_to(x0 + (x - x0) * i / n, h=0.32, dur=7, **kw)

    def cheer(self, times=2):
        self.st.cue("tada")
        for i in range(times):
            self.hop_to(self.x, h=0.8 - 0.2 * i, dur=8, sound=None); self.arms_to(155, self.st.f - 8, interp="BACK")
        self.arms_to(10)

    def think(self, n=18):
        """Se queda quieto, parpadea y mira arriba: 'está pensando'."""
        s = self.st; self.look(0.0, 0.03, s.f); self.look(0.03, 0.06, s.f + 5); self.blink(s.f + 8); self.look(0, 0, s.f + n)
        self.tilt(0, s.f); self.tilt(8, s.f + 6); self.tilt(0, s.f + n); s.f += n

    def shiver(self, n=12, deg=10):
        for i in range(n // 2): self.tilt(deg if i % 2 else -deg, self.st.f + i * 2)
        self.tilt(0, self.st.f + n); self.st.f += n

    def fall_in_water(self, dx=0.7, depth=-1.9, big=1.0):
        """Paso al vacío, instante suspendido (mira a cámara) y caída con salpicadura."""
        s = self.st; f = s.f
        s.key(self.root, f, loc=(self.x, 0, self.z)); self.tilt(0, f)
        s.key(self.root, f + 4, loc=(self.x + dx * 0.8, 0, self.z + 0.4)); self.tilt(25, f + 4); self.arms_to(120, f + 4)
        s.key(self.root, f + 9, loc=(self.x + dx, 0, self.z + 0.42)); self.tilt(-8, f + 9); self.blink(f + 5)   # suspendido
        s.cue("slide_down", f + 9)
        s.key(self.root, f + 16, loc=(self.x + dx, 0, depth)); s.key(self.body, f + 16, scale=(0.85, 0.85, 1.3)); self.arms_to(170, f + 14)
        s.f = f + 13; s.splash(self.x + dx, big=big); self.x += dx; self.z = depth; s.f = f + 22

    def drop_hat_floating(self, upto, water_z=-0.18):
        """El sombrero se suelta y queda flotando donde cayó el personaje. Llamar ANTES de fall_in_water no hace falta: úsalo después."""
        s = self.st; hat = self.hat
        mw = {}
        for fr in range(1, upto + 1, 2):
            s.sc.frame_set(fr); mw[fr] = tuple(self.body.matrix_world @ Vector((0, 0, 1.08)))
        hat.parent = None
        for fr, p in mw.items(): s.key(hat, fr, loc=p, rot=(0, 0, 0), scale=self.root.scale[:])
        x = self.x
        s.key(hat, upto + 6, loc=(x, 0, 0.8)); s.key(hat, upto + 16, loc=(x, 0, water_z), rot=(0.15, 0.1, 0.6))
        for i in range(1, 8): s.key(hat, upto + 16 + i * 8, loc=(x + 0.05 * i, 0, water_z + (0.05 if i % 2 else -0.03)), rot=(0.1 * (-1) ** i, 0.08, 0.6 + 0.2 * i))
        s.cue("pop", upto + 16, vol=-8)
