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
           "rock": (0.5, 0.5, 0.52), "pink": (1.0, 0.45, 0.6), "mud": (0.36, 0.25, 0.16), "metal": (0.6, 0.62, 0.66), "gold": (1.0, 0.72, 0.1),
           "green": (0.20, 0.72, 0.30), "teal": (0.05, 0.65, 0.62), "lime": (0.62, 0.85, 0.12), "coral": (1.0, 0.42, 0.36), "cream": (0.98, 0.90, 0.70),
           "brown": (0.50, 0.30, 0.16), "gray": (0.55, 0.57, 0.62), "navy": (0.10, 0.16, 0.45),
           # humanos: tonos de piel, pelo y ropa
           "skin1": (1.0, 0.82, 0.68), "skin2": (0.95, 0.70, 0.52), "skin3": (0.80, 0.55, 0.38), "skin4": (0.60, 0.38, 0.24), "skin5": (0.42, 0.26, 0.16), "skin6": (0.28, 0.17, 0.11),
           "hair_black": (0.03, 0.03, 0.04), "hair_brown": (0.26, 0.14, 0.07), "hair_blond": (0.93, 0.74, 0.30), "hair_red": (0.70, 0.25, 0.08), "hair_gray": (0.70, 0.70, 0.72),
           "denim": (0.16, 0.28, 0.55), "khaki": (0.70, 0.60, 0.40), "shoe": (0.10, 0.10, 0.12), "mouth": (0.35, 0.05, 0.08), "lips": (0.62, 0.22, 0.20), "olive": (0.35, 0.40, 0.16), "maroon": (0.42, 0.08, 0.12)}

# Reparto: cada episodio usa UN personaje (el mismo en todos sus niveles) y episodios distintos usan personajes distintos.
SHAPES = {"redondo": (0.55, 0.50, 0.58), "alto": (0.44, 0.42, 0.74), "ancho": (0.68, 0.56, 0.50), "pera": (0.50, 0.48, 0.66), "mini": (0.46, 0.44, 0.48)}
BODY_COLORS = ["blue", "purple", "orange", "green", "teal", "coral", "lime", "pink", "red", "cream", "brown", "gray"]
HATS = ["bombin", "gorra", "casco", "cono", "lazo", "antena", "copa", "ninguno"]
HAT_COLORS = ["yellow", "red", "white", "navy", "gold", "pink", "green"]


SKINS = ["skin1", "skin2", "skin3", "skin4", "skin5", "skin6"]
HAIRS = ["corto", "corto", "rizado", "afro", "mono", "coletas", "flequillo", "calvo", "largo"]
HAIR_COLORS = ["hair_black", "hair_black", "hair_brown", "hair_brown", "hair_blond", "hair_red", "hair_gray"]
SHIRTS = ["red", "blue", "green", "orange", "purple", "teal", "white", "yellow", "coral", "navy", "pink", "lime"]
PANTS = ["denim", "navy", "brown", "black", "olive", "maroon"]
BUILDS = {"normal": (1.0, 1.0), "alto": (0.95, 1.10), "bajo": (1.05, 0.90), "fuerte": (1.30, 1.0), "flaco": (0.85, 1.04)}


def look_for(seed, kind="humano"):
    """Aspecto reproducible a partir del id del episodio. Por defecto, un HUMANO de plastilina (decisión del usuario)."""
    r = random.Random(str(seed))
    if kind == "humano":
        shirt = r.choice(SHIRTS)
        return {"kind": "humano", "skin": r.choice(SKINS), "hair": r.choice(HAIRS), "hair_color": r.choice(HAIR_COLORS), "shirt": shirt,
                "pants": r.choice(PANTS), "build": r.choice(list(BUILDS)), "top": r.choice(["camiseta", "camiseta", "tirantes", "sin"]), "bottom": r.choice(["corto", "corto", "largo"]), "hat": r.choice(["ninguno", "ninguno", "ninguno", "gorra", "bombin", "casco"]),
                "hat_color": r.choice([c for c in HAT_COLORS if c != shirt]), "eye": r.choice([0.9, 1.0, 1.15]), "glasses": r.random() < 0.2, "color": shirt}
    color = r.choice(BODY_COLORS); hc = r.choice([c for c in HAT_COLORS if c != color])
    return {"shape": r.choice(list(SHAPES)), "color": color, "hat": r.choice(HATS), "hat_color": hc,
            "eye": r.choice([0.85, 1.0, 1.2]), "eye_gap": r.choice([0.17, 0.20, 0.24]), "cheeks": r.random() < 0.4, "tail": r.random() < 0.3}


class Stage:
    """Escenario + línea de tiempo. `self.f` es el fotograma actual; cada acción lo hace avanzar."""

    def __init__(self, env="rio", res=(432, 768), samples=10, engine=None):
        bpy.ops.wm.read_factory_settings(use_empty=True)
        self.sc = sc = bpy.context.scene
        self.f, self.cues, self.mats, self.actors = 1, [], {}, []
        engine = engine or os.environ.get("STUDIO_ENGINE", "CYCLES")
        sc.render.engine = engine
        res = tuple(int(v) for v in os.environ["STUDIO_RES"].split("x")) if os.environ.get("STUDIO_RES") else res
        samples = int(os.environ.get("STUDIO_SAMPLES", samples))
        if engine == "CYCLES":
            dev = os.environ.get("STUDIO_DEVICE", "CPU")
            if dev == "GPU":   # activa la tarjeta (OptiX y, si no, CUDA); si falla, sigue en CPU y lo dice
                try:
                    prefs = bpy.context.preferences.addons["cycles"].preferences
                    for kind in ("OPTIX", "CUDA"):
                        try:
                            prefs.compute_device_type = kind; prefs.get_devices()
                            gpus = [d for d in prefs.devices if d.type == kind]
                            if gpus:
                                for d in prefs.devices: d.use = d.type == kind
                                print(f"[kit] GPU {kind}: {[d.name for d in gpus]}"); break
                        except Exception: pass
                    else:
                        dev = "CPU"; print("[kit] no se encontró GPU compatible: render en CPU")
                except Exception as e:
                    dev = "CPU"; print(f"[kit] GPU no disponible ({e}): render en CPU")
            sc.cycles.device = dev; sc.cycles.samples = samples
            if dev == "GPU":
                try: sc.cycles.denoiser = "OPTIX"                              # eliminación de ruido en la propia tarjeta
                except Exception: pass
            sc.cycles.use_denoising = True; sc.cycles.max_bounces = 3
        if engine.startswith("BLENDER_EEVEE"):    # motor rápido en GPU (sin probar en esta máquina: no tiene GPU)
            try:
                sc.eevee.taa_render_samples = max(8, samples)
                for attr, val in (("use_shadows", True), ("use_raytracing", True), ("use_gtao", True)):
                    if hasattr(sc.eevee, attr): setattr(sc.eevee, attr, val)
            except Exception as e: print(f"[kit] ajustes EEVEE no aplicados: {e}")
            print(f"[kit] motor {engine}")
        sc.render.resolution_x, sc.render.resolution_y = res
        sc.render.fps = FPS; sc.render.image_settings.file_format = "PNG"; sc.view_settings.view_transform = "Standard"
        w = bpy.data.worlds.new("w"); sc.world = w; w.use_nodes = True
        bg = w.node_tree.nodes["Background"]; bg.inputs[0].default_value = (0.50, 0.75, 1.0, 1); bg.inputs[1].default_value = 0.85
        sun = bpy.data.objects.new("sun", bpy.data.lights.new("sun", "SUN")); sc.collection.objects.link(sun)
        sun.data.energy = 3.0; sun.data.angle = 0.3; sun.rotation_euler = (math.radians(50), 0, math.radians(-35))
        self.cam = bpy.data.objects.new("cam", bpy.data.cameras.new("cam")); sc.collection.objects.link(self.cam); sc.camera = self.cam
        self.tgt = self.empty("mira", (-0.5, 0, 0.9)); self.cam.data.lens = 72; self.cam.location = (-5.8, -7.2, 2.7)
        tc = self.cam.constraints.new("TRACK_TO"); tc.target = self.tgt; tc.track_axis = "TRACK_NEGATIVE_Z"; tc.up_axis = "UP_Y"
        getattr(self, "env_" + env)()

    # ---------- utilidades ----------
    def mat(self, name, rough=0.5):
        if name not in self.mats:
            m = bpy.data.materials.new(name); m.use_nodes = True
            b = m.node_tree.nodes["Principled BSDF"]; b.inputs["Base Color"].default_value = (*PALETTE[name], 1)
            b.inputs["Roughness"].default_value = 0.08 if name == "water" else (0.95 if name.startswith(("hair", "skin")) else rough)
            if "Specular IOR Level" in b.inputs and name.startswith(("hair", "skin", "shoe")): b.inputs["Specular IOR Level"].default_value = 0.15
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
            hz = 0.95 if getattr(actor, "human", False) else 0.6
            self.key(self.tgt, fr, loc=(wp.x * (0.92 if hz > 0.9 else weight), 0, max(0.45, min(1.35, wp.z + hz))))

    def actor(self, color=None, hat=None, x=0.0, size=1.0, look=None):
        """Sin argumentos usa el aspecto del episodio (S.look). `color`/`hat` lo fuerzan (p. ej. un secundario)."""
        lk = dict(look or getattr(self, "look", None) or look_for("ep001"))
        if color: lk["color"] = color
        if hat: lk["hat"] = hat
        a = Actor(self, lk, x, size); self.actors.append(a); return a

    def render(self, out, only=None):
        n = self.f + 10
        self.sc.frame_start, self.sc.frame_end = 1, n
        os.makedirs(out, exist_ok=True)
        json.dump({"frames": n, "fps": FPS, "cues": self.cues}, open(os.path.join(out, "level.json"), "w"), indent=1)
        if only:
            self.sc.frame_set(only); self.sc.render.filepath = os.path.join(out, f"f{only:04d}.png"); bpy.ops.render.render(write_still=True)
            return n
        # Todo el nivel en UNA llamada: Blender prepara la escena una vez y la reutiliza (mucho más rápido, sobre todo con GPU)
        self.sc.render.use_persistent_data = True
        self.sc.render.filepath = os.path.join(out, "f####")
        bpy.ops.render.render(animation=True)
        return n


class Actor:
    """Personaje de plastilina: cuerpo, ojos con párpados, pies, brazos con hombro articulado y sombrero."""

    def __init__(self, st, lk, x, size):
        self.st, s = st, st
        self.legs, self.has_hat = [], lk.get("hat", "ninguno") != "ninguno"
        self.human, self.squash, self.knees, self.elbows, self.yaw, self._stepn = False, 1.0, [], [], 0.0, 0
        self._lid_rest = 0.001
        if lk.get("kind") == "humano":
            self._human(lk, x, size); self._hat(lk.get("hat", "ninguno"), lk.get("hat_color", "yellow")); self.x, self.z = x, 0.0; return
        color, hat, hc = lk["color"], lk["hat"], lk.get("hat_color", "yellow")
        bx, by, bz = SHAPES[lk.get("shape", "redondo")]; e = lk.get("eye", 1.0); g = lk.get("eye_gap", 0.20)
        top = 0.55 + bz * 0.92                                   # altura de la coronilla
        ey = 0.55 + bz * 0.40; fy = -by * 0.84                   # altura y profundidad de los ojos
        self.root = s.empty("pj", (x, 0, 0)); self.root.scale = (size,) * 3
        self.body = s.empty("cuerpo", parent=self.root)
        s.obj("uv_sphere", "panza", color, (0, 0, 0.55), (bx, by, bz), parent=self.body)
        self.lids, self.pupils, self.arms = [], [], []
        self._pup = (g + 0.01, fy - 0.09 * e, ey)
        self._lid = (0.158 * e, 0.108 * e, 0.175 * e)
        for sx in (-1, 1):
            s.obj("uv_sphere", "ojo", "white", (g * sx, fy, ey), (0.15 * e, 0.10 * e, 0.17 * e), parent=self.body)
            self.pupils.append(s.obj("uv_sphere", "pupila", "black", (self._pup[0] * sx, self._pup[1], ey), (0.06 * e, 0.04 * e, 0.07 * e), parent=self.body))
            lid = s.obj("uv_sphere", "parpado", color, (g * sx, fy - 0.005, ey + 0.02), (self._lid[0], self._lid[1], 0.001), parent=self.body); self.lids.append(lid)
            s.obj("uv_sphere", "pie", color, (0.22 * sx, -0.05, 0.07), (0.17, 0.24, 0.09), parent=self.root)
            sh = s.empty("hombro", ((bx - 0.05) * sx, 0, 0.62), parent=self.body); self.arms.append(sh)
            s.obj("uv_sphere", "brazo", color, (0.10 * sx, 0, -0.20), (0.10, 0.10, 0.24), parent=sh)
            s.obj("uv_sphere", "mano", color, (0.12 * sx, 0, -0.42), (0.12, 0.12, 0.12), parent=sh)
            if lk.get("cheeks"): s.obj("uv_sphere", "moflete", "pink", ((g + 0.16) * sx, fy + 0.06, ey - 0.20), (0.07, 0.03, 0.05), parent=self.body)
        if lk.get("tail"): s.obj("uv_sphere", "cola", color, (0, by * 0.95, 0.35), (0.12, 0.16, 0.12), parent=self.body)
        self.hat_z = top
        self._hat(hat, hc)
        self.x, self.z = x, 0.0


    def _hat(self, hat, hc):
        s = self.st
        self.hat = s.empty("sombrero", (0, 0, self.hat_z), parent=self.body)
        if getattr(self, "human", False): self.hat.scale = (0.62, 0.62, 0.62)
        H = self.hat
        if hat == "bombin":
            s.obj("cylinder", "ala", hc, (0, 0, 0), (0.34, 0.34, 0.025), parent=H); s.obj("cylinder", "copa", hc, (0, 0, 0.13), (0.20, 0.20, 0.13), parent=H)
        elif hat == "copa":
            s.obj("cylinder", "ala", "black", (0, 0, 0), (0.34, 0.34, 0.025), parent=H); s.obj("cylinder", "copa", "black", (0, 0, 0.26), (0.19, 0.19, 0.26), parent=H)
            s.obj("cylinder", "cinta", hc, (0, 0, 0.07), (0.195, 0.195, 0.04), parent=H)
        elif hat == "gorra":
            s.obj("uv_sphere", "casquete", hc, (0, 0, -0.02), (0.30, 0.30, 0.20), parent=H); s.obj("cylinder", "visera", hc, (0, -0.30, 0.0), (0.22, 0.20, 0.02), parent=H)
        elif hat == "casco":
            s.obj("uv_sphere", "casco", hc, (0, 0, -0.06), (0.40, 0.40, 0.28), parent=H); s.obj("cylinder", "borde", hc, (0, 0, -0.04), (0.44, 0.44, 0.03), parent=H)
        elif hat == "cono":
            s.obj("cone", "cono", hc, (0, 0, 0.22), (0.22, 0.22, 0.28), parent=H); s.obj("uv_sphere", "pompon", "white", (0, 0, 0.50), (0.06, 0.06, 0.06), parent=H)
        elif hat == "lazo":
            for sx in (-1, 1): s.obj("cone", "lazo", hc, (0.14 * sx, 0, 0.05), (0.12, 0.05, 0.14), rot=(0, math.radians(90 * sx), 0), parent=H)
            s.obj("uv_sphere", "nudo", hc, (0, 0, 0.05), (0.06, 0.06, 0.06), parent=H)
        elif hat == "antena":
            s.obj("cylinder", "varilla", "gray", (0, 0, 0.16), (0.02, 0.02, 0.18), parent=H); s.obj("uv_sphere", "bola", hc, (0, 0, 0.38), (0.08, 0.08, 0.08), parent=H)
        elif hat == "corona":
            s.obj("cylinder", "aro", "gold", (0, 0, 0.05), (0.30, 0.30, 0.07), parent=H, smooth=False, vertices=10)
            for i in range(5):
                a = i * 1.2566; s.obj("cone", "pico", "gold", (0.26 * math.cos(a), 0.26 * math.sin(a), 0.20), (0.07, 0.07, 0.12), parent=H)

    def _human(self, lk, x, size):
        """Humano larguirucho de dibujo animado: extremidades largas con codos y rodillas, cabeza proporcionada,
        ojos grandes con párpado a media altura, cejas gruesas, labios y pelo con textura. Mide ~1,8 unidades."""
        s = self.st; skin, shirt, pants = lk["skin"], lk["shirt"], lk["pants"]
        wd, ht = BUILDS[lk.get("build", "normal")]; e = lk.get("eye", 1.0); hc = lk["hair_color"]
        top_style = lk.get("top", "camiseta"); legs_style = lk.get("bottom", "corto")
        self.human, self.squash, self.yaw, self._stepn = True, 0.3, -30.0, 0
        self.root = s.empty("pj", (x, 0, 0)); self.root.scale = (size,) * 3; self.root.rotation_euler = (0, 0, math.radians(self.yaw))
        self.body = s.empty("cuerpo", parent=self.root)
        r = 0.052 * wd                                                    # grosor de extremidades
        thigh, shin = 0.43 * ht, 0.42 * ht; hip = thigh + shin + 0.07
        torso_h = 0.50 * ht; sh_z = hip + torso_h; neck = 0.10
        hz = sh_z + neck + 0.20                                           # centro de la cabeza
        self.knees, self.elbows = [], []
        # Esqueleto de control (empties). El cuerpo es UNA malla continua que se deforma con ellos: sin bolas ni huecos.
        for sx in (-1, 1):
            lp = s.empty("cadera", (0.085 * wd * sx, 0, hip), parent=self.root); self.legs.append(lp)
            kn = s.empty("rodilla", (0, 0, -thigh), parent=lp); self.knees.append(kn)
            s.obj("uv_sphere", "zapato", "shoe", (0, -0.07, -shin - 0.02), (0.078 * wd, 0.15, 0.058), parent=kn)
        self.lids, self.pupils, self.arms = [], [], []
        ua, fa = 0.31 * ht, 0.29 * ht
        for sx in (-1, 1):
            sh = s.empty("hombro", (0.165 * wd * sx, 0, sh_z - 0.04), parent=self.body); self.arms.append(sh)
            el = s.empty("codo", (0, 0, -ua), parent=sh); el.rotation_euler = (math.radians(-12), 0, 0); self.elbows.append(el)
        self._dims = dict(r=r, thigh=thigh, shin=shin, hip=hip, torso_h=torso_h, sh_z=sh_z, neck=neck, ua=ua, fa=fa, wd=wd)
        H = self.head = s.empty("cabeza", (0, 0, hz), parent=self.body)
        s.obj("uv_sphere", "craneo", skin, (0, 0, 0), (0.175, 0.185, 0.21), parent=H)
        s.obj("uv_sphere", "mandibula", skin, (0, -0.03, -0.10), (0.135, 0.14, 0.12), parent=H)
        for sx in (-1, 1): s.obj("uv_sphere", "oreja", skin, (0.175 * sx, 0.02, -0.01), (0.03, 0.045, 0.06), parent=H)
        # ojos grandes que sobresalen; párpado superior a media altura (mirada de aburrido) que también sirve para parpadear
        ex, ey, ez, er = 0.082, -0.15, 0.04, 0.085 * e
        self._pup = (ex + 0.002, ey - er * 0.78, ez - 0.012); self._lid = (er * 1.08, er * 1.0, er * 1.08); self._lid_rest = er * 0.55
        for sx in (-1, 1):
            s.obj("uv_sphere", "ojo", "white", (ex * sx, ey, ez), (er, er * 0.75, er * 1.1), parent=H)
            self.pupils.append(s.obj("uv_sphere", "pupila", "black", (self._pup[0] * sx, self._pup[1], self._pup[2]), (er * 0.55, er * 0.2, er * 0.6), parent=H))
            lid = s.obj("uv_sphere", "parpado", skin, (ex * sx, ey - 0.004, ez + er * 0.45), (self._lid[0], self._lid[1], self._lid_rest), parent=H); self.lids.append(lid)
            s.obj("uv_sphere", "ceja", hc, (ex * sx, ey - 0.02, ez + er * 1.25), (er * 1.05, 0.02, 0.022), rot=(0, math.radians(-10 * sx), 0), parent=H)
        s.obj("uv_sphere", "nariz", skin, (0, -0.205, -0.045), (0.032, 0.045, 0.05), parent=H)
        s.obj("uv_sphere", "labios", "lips", (0, -0.175, -0.125), (0.065, 0.03, 0.026), parent=H)
        if lk.get("glasses"):
            for sx in (-1, 1): s.obj("torus", "gafa", "black", (ex * sx, ey - er * 0.8, ez), (1, 1, 1), rot=(math.radians(90), 0, 0), parent=H, major_radius=er * 1.15, minor_radius=0.008)
        # pelo: rizos = muchas bolitas sobre el cráneo; otros estilos, volúmenes lisos
        hair = lk.get("hair", "corto"); rnd = random.Random(str(lk))
        top = 0.21
        def curls(n, rad, zmin, scale_r=1.0, back=0.0):
            for i in range(n):
                th = rnd.uniform(0, 2 * math.pi); ph = rnd.uniform(0, math.acos(zmin))
                px, py, pz = math.sin(ph) * math.cos(th), math.sin(ph) * math.sin(th), math.cos(ph)
                if py < -0.55 and pz < 0.75: continue                          # despeja la frente
                rr = rnd.uniform(rad * 0.8, rad * 1.2)
                s.obj("uv_sphere", "rizo", hc, (0.18 * px * scale_r, 0.19 * py * scale_r + back, 0.205 * pz * scale_r + 0.01), (rr,) * 3, parent=H, segments=10, ring_count=8)
        if hair in ("corto", "afro", "rizado"):
            s.obj("uv_sphere", "base_pelo", hc, (0, 0.02, 0.03), (0.178, 0.185, 0.20), parent=H)
            curls(70 if hair == "afro" else 46, 0.05 if hair == "afro" else 0.04, 0.05, scale_r=1.12 if hair == "afro" else 1.0); top = 0.30 if hair == "afro" else 0.25
        elif hair in ("flequillo", "largo", "coletas", "mono"):
            s.obj("uv_sphere", "pelo", hc, (0, 0.03, 0.05), (0.19, 0.195, 0.205), parent=H); top = 0.25
            if hair == "flequillo": s.obj("uv_sphere", "flequillo", hc, (0.03, -0.15, 0.13), (0.15, 0.06, 0.06), rot=(0, 0.25, 0), parent=H)
            if hair == "largo": s.obj("uv_sphere", "melena", hc, (0, 0.10, -0.12), (0.19, 0.11, 0.24), parent=H)
            if hair == "coletas":
                for sx in (-1, 1): s.obj("uv_sphere", "coleta", hc, (0.20 * sx, 0.05, -0.06), (0.055, 0.055, 0.12), parent=H)
            if hair == "mono": s.obj("uv_sphere", "mono", hc, (0, 0.04, 0.24), (0.08, 0.08, 0.075), parent=H); top = 0.31
        self.hat_z = hz + top - 0.03
        self._skin_body(skin, shirt, pants, top_style, legs_style)

    def _skin_body(self, skin, shirt, pants, top_style, legs_style):
        """Cuerpo continuo: esqueleto de puntos -> modificador Skin + suavizado -> malla única con pesos -> armadura
        cuyos huesos siguen a los empties de control. Ropa por zonas (camiseta, tirantes, sin camiseta; corto o largo)."""
        s = self.st; d = self._dims; r = d["r"]; wd = d["wd"]
        bpy.context.view_layer.update()
        W = lambda emp, loc=(0, 0, 0): emp.matrix_world @ Vector(loc)
        B = self.body
        # Cadenas separadas (torso, brazos, piernas) que nacen DENTRO del torso: sin nudos de varias ramas, que el
        # modificador Skin convierte en pinchos. Lo que queda dentro del torso no se ve.
        chains = [[(W(B, (0, 0, d["hip"] + 0.03)), "body", 0.135 * wd, 0.10 * wd),
                   (W(B, (0, 0, d["hip"] + d["torso_h"] * 0.40)), "body", 0.135 * wd, 0.095 * wd),
                   (W(B, (0, 0, d["hip"] + d["torso_h"] * 0.78)), "body", 0.15 * wd, 0.10 * wd),
                   (W(B, (0, 0, d["sh_z"] - 0.03)), "body", 0.115 * wd, 0.08 * wd),
                   (W(B, (0, 0, d["sh_z"] + 0.03)), "body", 0.048 * wd, None),
                   (W(self.head, (0, 0, -0.14)), "head", 0.05 * wd, None)]]
        for i, (lp, kn, sh, el) in enumerate(zip(self.legs, self.knees, self.arms, self.elbows)):
            sx = -1 if i == 0 else 1; gL, gK, gS, gE = f"leg{i}", f"knee{i}", f"arm{i}", f"elbow{i}"
            chains.append([(W(B, (0.03 * wd * sx, 0, d["hip"] + 0.11)), "body", r * 1.2, None),
                           (W(lp), gL, r * 1.30, None), (W(lp, (0, 0, -d["thigh"] * 0.5)), gL, r * 1.18, None),
                           (W(lp, (0, 0, -d["thigh"] * 0.86)), gL, r * 1.08, None), (W(kn), gK, r * 1.04, None),
                           (W(kn, (0, 0, -d["shin"] * 0.5)), gK, r * 0.98, None), (W(kn, (0, 0, -d["shin"] + 0.02)), gK, r * 0.80, None)])
            chains.append([(W(B, (0.07 * wd * sx, 0, d["sh_z"] - 0.06)), "body", r * 1.05, None),
                           (W(sh), gS, r * 1.10, None), (W(sh, (0, 0, -d["ua"] * 0.5)), gS, r * 0.98, None),
                           (W(sh, (0, 0, -d["ua"] * 0.86)), gS, r * 0.90, None), (W(el), gE, r * 0.88, None),
                           (W(el, (0, 0, -d["fa"] * 0.6)), gE, r * 0.80, None), (W(el, (0, 0, -d["fa"])), gE, r * 0.68, None),
                           (W(el, (0, -0.005, -d["fa"] - 0.075)), gE, 0.050, None)])
        names = ["body", "head"] + [f"{k}{i}" for i in range(2) for k in ("leg", "knee", "arm", "elbow")]
        hipz = W(B, (0, 0, d["hip"])).z; shz = W(B, (0, 0, d["sh_z"])).z
        self.skin_parts = []
        for ci, ch in enumerate(chains):
            pts = [tuple(c[0]) for c in ch]; edges = [(k, k + 1) for k in range(len(ch) - 1)]
            me = bpy.data.meshes.new("esqueleto"); me.from_pydata(pts, edges, [])
            base = bpy.data.objects.new("esqueleto", me); s.sc.collection.objects.link(base)
            for n in names: base.vertex_groups.new(name=n)
            for k, c in enumerate(ch): base.vertex_groups[c[1]].add([k], 1.0, "REPLACE")
            base.modifiers.new("Skin", "SKIN"); sub = base.modifiers.new("Sub", "SUBSURF"); sub.levels = 2; sub.render_levels = 2
            sv = me.skin_vertices[0].data
            for k, c in enumerate(ch): sv[k].radius = (c[2], c[3] or c[2])
            sv[0].use_root = True
            dg = bpy.context.evaluated_depsgraph_get()
            nm = bpy.data.meshes.new_from_object(base.evaluated_get(dg), preserve_all_data_layers=True, depsgraph=dg)
            bpy.data.objects.remove(base)
            ob = bpy.data.objects.new("cuerpo_piel", nm); s.sc.collection.objects.link(ob)
            if not ob.vertex_groups:
                for n in names: ob.vertex_groups.new(name=n)
            gi = {g.index: g.name for g in ob.vertex_groups}
            for v in nm.vertices:                                     # vértices sin hueso: al del punto del esqueleto más cercano
                if not v.groups or sum(g.weight for g in v.groups) < 0.5:
                    near = min(ch, key=lambda c: (c[0] - v.co).length)
                    ob.vertex_groups[near[1]].add([v.index], 1.0, "REPLACE")
            for m in (skin, shirt, pants): nm.materials.append(s.mat(m))
            for poly in nm.polygons:
                poly.use_smooth = True
                vs = [nm.vertices[k] for k in poly.vertices]; z = sum(v.co.z for v in vs) / len(vs)
                cnt = {}
                for v in vs:
                    best = max(v.groups, key=lambda g: g.weight, default=None); g = gi[best.group] if best else "body"; cnt[g] = cnt.get(g, 0) + 1
                g = max(cnt, key=cnt.get); mi = 0
                if g == "body":
                    if ci == 0 or z > hipz + 0.2: mi = 2 if z < hipz + 0.09 else (0 if top_style == "sin" else 1)
                    else: mi = 2                                          # raíz de la pierna: dentro del pantalón
                    if ci > 0 and z > hipz + 0.2: mi = 0 if top_style != "camiseta" else 1
                elif g.startswith("leg"):
                    kz = W(self.knees[int(g[-1])]).z
                    mi = 2 if (legs_style == "largo" or (z - kz) / max(hipz - kz, 1e-3) > 0.42) else 0
                elif g.startswith("knee"):
                    mi = 2 if legs_style == "largo" else 0
                elif g.startswith("arm"):
                    mi = 1 if (top_style == "camiseta" and shz - z < d["ua"] * 0.38) else 0
                poly.material_index = mi
            self.skin_parts.append(ob)
        # armadura: un hueso por empty de control; cada hueso copia el movimiento de su empty (Child Of)
        ctrl = {"body": B, "head": self.head}
        for i in range(2): ctrl.update({f"leg{i}": self.legs[i], f"knee{i}": self.knees[i], f"arm{i}": self.arms[i], f"elbow{i}": self.elbows[i]})
        ad = bpy.data.armatures.new("rig"); rig = bpy.data.objects.new("rig", ad); s.sc.collection.objects.link(rig)
        prev = bpy.context.view_layer.objects.active
        bpy.context.view_layer.objects.active = rig; rig.select_set(True)
        bpy.ops.object.mode_set(mode="EDIT")
        for n, emp in ctrl.items():
            b = ad.edit_bones.new(n); hpos = emp.matrix_world.translation; b.head = hpos; b.tail = hpos + Vector((0, 0, 0.1))
        bpy.ops.object.mode_set(mode="OBJECT"); rig.select_set(False); bpy.context.view_layer.objects.active = prev
        for n, emp in ctrl.items():
            c = rig.pose.bones[n].constraints.new("CHILD_OF"); c.target = emp; c.inverse_matrix = emp.matrix_world.inverted()
        for ob in self.skin_parts:
            mod = ob.modifiers.new("Armature", "ARMATURE"); mod.object = rig
        rig.hide_render = True; self.rig = rig

    def hold_stick(self, name, color, length, world_dir, side=1, above=0.3, blade=True, free=False):
        """Pone un palo (remo, escoba, caña) en la mano: sigue al antebrazo y apunta hacia `world_dir` en la pose actual."""
        s = self.st; s.sc.frame_set(s.f); bpy.context.view_layer.update()
        el = self.elbows[side]; fa = self._dims["fa"]
        grip = s.empty("agarre", (0, -0.005, -fa - 0.07), parent=el); bpy.context.view_layer.update()
        M = grip.matrix_world.to_3x3().normalized()
        d = (M.inverted() @ Vector(world_dir)).normalized()
        if free:  # solo sigue la POSICIÓN de la mano; el ángulo se anima aparte con aim_stick (no atraviesa nada al mover el brazo)
            st = s.empty(name, (0, 0, 0)); c = st.constraints.new("COPY_LOCATION"); c.target = grip
            st.rotation_euler = Vector(world_dir).normalized().to_track_quat("Z", "Y").to_euler()
        else:
            st = s.empty(name, (0, 0, 0), parent=grip); st.rotation_euler = d.to_track_quat("Z", "Y").to_euler()
        s.obj("cylinder", name + "_palo", color, (0, 0, length / 2 - above), (0.02, 0.02, length / 2), parent=st, vertices=12)
        if blade: s.obj("cube", name + "_pala", color, (0, 0, length - above - 0.12), (0.09, 0.015, 0.16), parent=st, smooth=False)
        return st

    def aim_stick(self, st, f, world_dir, interp="BEZIER"):
        """Orienta (en coordenadas del mundo) un palo creado con hold_stick(free=True) en el fotograma f."""
        self.st.key(st, f, rot=tuple(Vector(world_dir).normalized().to_track_quat("Z", "Y").to_euler()), interp=interp)

    def sit(self, f=None, knee=20, lean=0):
        """Postura sentada: muslos al frente, rodillas algo dobladas. Devuelve la altura de la cadera sobre los pies."""
        f = self.st.f if f is None else f
        for lg in self.legs: self.st.key(lg, f, rot=(math.radians(-88), 0, 0))
        for kn in self.knees: self.st.key(kn, f, rot=(math.radians(knee), 0, 0))
        self.tilt(lean, f)
        return self._dims["hip"]

    # --- gestos ---
    def arms_to(self, deg, f=None, interp="BEZIER"):
        """0 = brazos caídos; 150 = arriba (celebrar); negativo = hacia atrás."""
        for sx, sh in zip((-1, 1), self.arms): self.st.key(sh, f, rot=(0, math.radians(-deg * sx), 0), interp=interp)

    def blink(self, f=None):
        f = self.st.f if f is None else f
        for lid in self.lids:
            lx, ly, lz = self._lid
            rz = self._lid_rest
            self.st.key(lid, f - 1, scale=(lx, ly, rz)); self.st.key(lid, f + 1, scale=(lx, ly, lz))
            self.st.key(lid, f + 3, scale=(lx, ly, lz)); self.st.key(lid, f + 5, scale=(lx, ly, rz))

    def look(self, dx=0.0, dz=0.0, f=None):
        px, py, pz = self._pup
        for sx, p in zip((-1, 1), self.pupils): self.st.key(p, f, loc=(px * sx + dx, py, pz + dz))

    def tilt(self, deg, f=None, interp="BEZIER"): self.st.key(self.body, f, rot=(0, math.radians(deg), 0), interp=interp)

    def face(self, deg, f=None, turn=3):
        """Gira el cuerpo: 0 = de frente (eje -y); -30 = hacia la cámara; +55 = de perfil caminando hacia +x."""
        f = self.st.f if f is None else f
        self.st.key(self.root, f, rot=(0, 0, math.radians(self.yaw))); self.yaw = deg
        self.st.key(self.root, f + turn, rot=(0, 0, math.radians(deg)))

    def _sq(self, a, b, c):
        k = self.squash; return (1 + (a - 1) * k, 1 + (b - 1) * k, 1 + (c - 1) * k)

    def _stride(self, f0, mid, end, big):
        """Zancada: muslos adelante/atrás, rodilla de la pierna trasera doblada, brazos al contrario."""
        s = self.st; sgn = 1 if self._stepn % 2 else -1; self._stepn += 1; a = 38 if big else 26
        for i, (lg, kn) in enumerate(zip(self.legs, self.knees)):
            d = sgn if i else -sgn
            s.key(lg, f0, rot=(0, 0, 0)); s.key(lg, mid, rot=(math.radians(-a * d), 0, 0)); s.key(lg, end, rot=(0, 0, 0))
            s.key(kn, f0, rot=(0, 0, 0)); s.key(kn, mid, rot=(math.radians(55 if d < 0 else 10), 0, 0)); s.key(kn, end, rot=(0, 0, 0))
        for i, sh in enumerate(self.arms):
            d = sgn if i else -sgn; sx = -1 if i == 0 else 1
            s.key(sh, f0, rot=(0, math.radians(-8 * sx), 0)); s.key(sh, mid, rot=(math.radians(a * 0.9 * d), math.radians(-14 * sx), 0)); s.key(sh, end, rot=(0, math.radians(-8 * sx), 0))

    # --- acciones (avanzan el tiempo) ---
    def hop_to(self, x, z=None, h=0.55, dur=10, sound="boing"):
        s, f0 = self.st, self.st.f
        z1 = self.z if z is None else z
        if self.legs and sound == "boing": sound = "step"                          # los humanos dan pasos, no botes de goma
        if self.human and abs(x - self.x) > 0.05:                                  # mira hacia donde va
            tgt_yaw = 55 if x > self.x else -60
            if tgt_yaw != self.yaw: self.face(tgt_yaw, f0, turn=2)
        s.key(self.body, f0, scale=(1, 1, 1)); s.key(self.root, f0, loc=(self.x, 0, self.z))
        if not self.human: self.arms_to(10, f0)
        s.key(self.body, f0 + 2, scale=self._sq(1.18, 1.18, 0.78)); s.key(self.root, f0 + 2, loc=(self.x, 0, self.z))
        if not self.human: self.arms_to(-25, f0 + 2)
        if sound: s.cue(sound, f0 + 2, vol=-6)
        mid = f0 + 2 + dur // 2
        s.key(self.body, mid, scale=self._sq(0.88, 0.88, 1.22)); s.key(self.root, mid, loc=((self.x + x) / 2, 0, max(self.z, z1) + h))
        if not self.human: self.arms_to(95, mid)
        if self.human: self._stride(f0 + 2, mid, f0 + 2 + dur, big=h > 0.3)
        end = f0 + 2 + dur
        s.key(self.root, end, loc=(x, 0, z1)); s.key(self.body, end, scale=self._sq(1.25, 1.25, 0.70))
        if not self.human: self.arms_to(40, end)
        s.key(self.body, end + 3, scale=(1, 1, 1), interp="BACK")
        if not self.human: self.arms_to(10, end + 3)
        self.x, self.z = x, z1; s.f = end + 4

    def walk_to(self, x, steps=None, **kw):
        n = steps or max(1, round(abs(x - self.x) / 0.75)); x0 = self.x
        for i in range(1, n + 1): self.hop_to(x0 + (x - x0) * i / n, h=0.07 if self.human else 0.32, dur=8 if self.human else 7, **kw)

    def cheer(self, times=2):
        if self.human: self.face(-30)
        self.st.cue("tada")
        for i in range(times):
            self.hop_to(self.x, h=0.8 - 0.2 * i, dur=8, sound=None); self.arms_to(155, self.st.f - 8, interp="BACK")
        self.arms_to(10)

    def think(self, n=18):
        """Se queda quieto, parpadea y mira arriba: 'está pensando'."""
        s = self.st
        if self.human and self.yaw != -30: self.face(-30, turn=4)
        self.look(0.0, 0.03, s.f); self.look(0.03, 0.06, s.f + 5); self.blink(s.f + 8); self.look(0, 0, s.f + n)
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
        if not self.has_hat: return
        mw = {}
        for fr in range(1, upto + 1, 2):
            s.sc.frame_set(fr); mw[fr] = tuple(self.body.matrix_world @ Vector((0, 0, self.hat_z)))
        hat.parent = None
        for fr, p in mw.items(): s.key(hat, fr, loc=p, rot=(0, 0, 0), scale=self.root.scale[:])
        x = self.x
        s.key(hat, upto + 6, loc=(x, 0, 0.8)); s.key(hat, upto + 16, loc=(x, 0, water_z), rot=(0.15, 0.1, 0.6))
        for i in range(1, 8): s.key(hat, upto + 16 + i * 8, loc=(x + 0.05 * i, 0, water_z + (0.05 if i % 2 else -0.03)), rot=(0.1 * (-1) ** i, 0.08, 0.6 + 0.2 * i))
        s.cue("pop", upto + 16, vol=-8)
