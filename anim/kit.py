"""kit.py — biblioteca de animación por código para comedia física por niveles (Blender).

Se usa desde un episodio (anim/episodes/epNNN.py). Funciona con Blender como módulo (`pip install bpy`, Python 3.13)
o dentro de Blender: `blender -b -P anim/run_level.py -- <episodio> <nivel> <salida>`.

Idea central: el episodio describe ACCIONES (saltar hasta x, caer al agua, celebrar…) y el kit pone los fotogramas
clave con principios de animación (anticipación, estirar y encoger, rebote) y anota cada sonido en el fotograma exacto.
"""
import json, math, os, random
import bpy
import numpy as np
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
                "pants": r.choice(PANTS), "build": r.choice(list(BUILDS)), "top": r.choice(["sudadera", "sudadera", "camiseta", "camiseta", "tirantes"]), "bottom": r.choice(["largo", "largo", "corto"]), "hat": r.choice(["ninguno", "ninguno", "ninguno", "gorra", "bombin", "casco"]),
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

    # ---------- materiales realistas (procedurales, sin texturas de terceros) ----------
    def pmat(self, name, colors, scale=8.0, rough=0.8, bump=0.3, detail=6.0, alpha=None):
        """Material con variación natural: ruido -> rampa de colores (+ relieve). colors = [(pos, (r,g,b)), ...]."""
        key = "p_" + name
        if key in self.mats: return self.mats[key]
        m = bpy.data.materials.new(key); m.use_nodes = True; nt = m.node_tree; N = nt.nodes; L = nt.links
        b = N["Principled BSDF"]; b.inputs["Roughness"].default_value = rough
        tc = N.new("ShaderNodeTexCoord"); nz = N.new("ShaderNodeTexNoise"); nz.inputs["Scale"].default_value = scale; nz.inputs["Detail"].default_value = detail
        L.new(tc.outputs["Object"], nz.inputs["Vector"])
        cr = N.new("ShaderNodeValToRGB"); el = cr.color_ramp.elements
        el[0].position, el[0].color = colors[0][0], (*colors[0][1], 1); el[1].position, el[1].color = colors[-1][0], (*colors[-1][1], 1)
        for pos, c in colors[1:-1]: e = el.new(pos); e.color = (*c, 1)
        L.new(nz.outputs["Fac"], cr.inputs["Fac"]); L.new(cr.outputs["Color"], b.inputs["Base Color"])
        if bump:
            bp = N.new("ShaderNodeBump"); bp.inputs["Strength"].default_value = bump
            L.new(nz.outputs["Fac"], bp.inputs["Height"]); L.new(bp.outputs["Normal"], b.inputs["Normal"])
        if alpha is not None: b.inputs["Alpha"].default_value = alpha
        self.mats[key] = m; return m

    def _sky(self):
        w = self.sc.world; nt = w.node_tree; bg = nt.nodes["Background"]
        try:
            sky = nt.nodes.new("ShaderNodeTexSky")
            for attr, val in (("sky_type", "NISHITA"), ("sun_disc", False), ("sun_elevation", math.radians(38)), ("sun_rotation", math.radians(200)), ("altitude", 0), ("air_density", 1.0), ("dust_density", 1.5)):
                try: setattr(sky, attr, val)
                except Exception: pass
            nt.links.new(sky.outputs["Color"], bg.inputs[0]); bg.inputs[1].default_value = 0.10
        except Exception as e: print(f"[kit] cielo físico no disponible ({e})")

    def _scatter(self, target, inst, n, seed, length=None, rotate=False):
        """Reparte copias de `inst` sobre la superficie de `target` (partículas renderizadas como objeto)."""
        ps = target.modifiers.new("disperso", "PARTICLE_SYSTEM").particle_system; st = ps.settings
        st.type = "HAIR"; st.count = n; st.hair_length = 1.0; st.render_type = "OBJECT"; st.instance_object = inst
        st.use_rotations = rotate                                    # sin rotación: el eje X del objeto sigue al pelo (hacia arriba)
        if rotate: st.rotation_mode = "NOR"; st.phase_factor_random = 2.0; st.rotation_factor_random = 0.6
        st.particle_size = 1.0; st.size_random = 0.5; ps.seed = seed; st.use_advanced_hair = True
        inst.hide_render = False; inst.location = (0, 0, -50)
        return ps

    def env_rio(self):
        if os.environ.get("STUDIO_LOOK", "real") == "real": return self.env_rio_real()
        self.env_rio_flat()

    def env_rio_real(self):
        """Parque junto a un río, aspecto realista: cielo físico, suelo de hojas y hierba, briznas en primer plano,
        árboles con corteza y copas de hojas, agua turquesa con ondas. Todo procedural (propio)."""
        self._sky()
        sun = bpy.data.objects["sun"]; sun.data.energy = 3.2; sun.data.color = (1.0, 0.90, 0.75); sun.data.angle = math.radians(2.5)
        sun.rotation_euler = (math.radians(52), 0, math.radians(-25))
        try: self.sc.view_settings.view_transform = "AgX"; self.sc.view_settings.look = "AgX - Punchy"; self.sc.view_settings.exposure = -0.3
        except Exception:
            try: self.sc.view_settings.view_transform = "Filmic"
            except Exception: pass
        ground = self.pmat("suelo", [(0.30, (0.42, 0.20, 0.06)), (0.45, (0.60, 0.33, 0.08)), (0.55, (0.30, 0.38, 0.10)), (0.70, (0.22, 0.34, 0.08))], scale=3.5, rough=0.95, bump=0.6)
        for nm, x in (("orillaL", -202.5), ("orillaR", 202.5)):
            bpy.ops.mesh.primitive_plane_add(size=1, location=(x, 0, 0)); o = bpy.context.object; o.name = nm
            o.scale = (400, 400, 1); o.location.y = 150; o.data.materials.append(ground)
            bpy.ops.object.mode_set(mode="EDIT"); bpy.ops.mesh.subdivide(number_cuts=6); bpy.ops.object.mode_set(mode="OBJECT")
            self.obj("cube", nm + "_talud", "mud", (32.5 if x > 0 else -32.5, 0, -1.5), (30, 60, 1.49), smooth=False).data.materials[0] = ground
        self.obj("cube", "lecho", "mud", (0, 0, -2.6), (2.5, 60, 1.5), smooth=False)
        self.water = self.obj("cube", "agua", "water", (0, 0, -1.75), (2.49, 60, 1.5), smooth=False)
        wm = self.pmat("agua", [(0.3, (0.05, 0.42, 0.48)), (0.7, (0.10, 0.55, 0.58))], scale=6, rough=0.05, bump=0.15)
        self.water.data.materials[0] = wm
        self.obj("cube", "muelle", "wood", (-2.6, 0, 0.06), (0.9, 0.5, 0.06), smooth=False).data.materials[0] = \
            self.pmat("madera", [(0.2, (0.30, 0.18, 0.08)), (0.8, (0.45, 0.29, 0.14))], scale=20, rough=0.8, bump=0.4, detail=3)
        # briznas de hierba: una hoja curvada instanciada miles de veces SOLO cerca de cámara (barato)
        def blade(nm, w, h):
            o = self.obj("cone", nm, "leaf", (0, 0, 0), (w, w * 0.35, h), rot=(0, math.radians(90), 0), vertices=4, smooth=False)
            for ob in bpy.context.selected_objects: ob.select_set(False)
            o.select_set(True); bpy.context.view_layer.objects.active = o
            bpy.ops.object.transform_apply(location=False, rotation=True, scale=True)
            o.data.transform(__import__("mathutils").Matrix.Translation((h, 0, 0)))   # base en el origen
            return o
        bl = blade("brizna", 0.014, 0.20)
        bl.data.materials[0] = self.pmat("hierba", [(0.2, (0.18, 0.36, 0.06)), (0.6, (0.42, 0.55, 0.12)), (0.9, (0.65, 0.58, 0.20))], scale=2, rough=0.6, bump=0)
        for nm, x0, x1, y0, y1, n in (("prado_cerca", -9.0, -2.55, -6.5, 3.0, 22000), ("prado_lejos", 2.55, 9.0, -4.0, 6.0, 12000)):
            bpy.ops.mesh.primitive_plane_add(size=1, location=((x0 + x1) / 2, (y0 + y1) / 2, 0.0)); pr = bpy.context.object; pr.name = nm
            pr.scale = (x1 - x0, y1 - y0, 1); pr.data.materials.append(ground); pr.location.z = 0.002
            self._scatter(pr, bl, n, 7 if x0 < 0 else 8)
        # franja de hierba alta delante de la cámara (desenfocada, da profundidad)
        bpy.ops.mesh.primitive_plane_add(size=1, location=(-4.4, -5.4, 0.003)); fg = bpy.context.object; fg.name = "hierba_frente"
        fg.scale = (4.0, 1.4, 1); fg.data.materials.append(ground)
        big = blade("brizna_alta", 0.022, 0.42); big.data.materials[0] = bl.data.materials[0]
        self._scatter(fg, big, 1400, 11)
        # árboles: tronco con corteza + copa de hojas (racimos de esferas cubiertos de hojas planas)
        bark = self.pmat("corteza", [(0.3, (0.18, 0.12, 0.07)), (0.7, (0.32, 0.24, 0.15))], scale=30, rough=0.9, bump=0.8, detail=8)
        leafm = self.pmat("hojas", [(0.25, (0.10, 0.26, 0.05)), (0.55, (0.22, 0.40, 0.08)), (0.85, (0.45, 0.50, 0.12))], scale=4, rough=0.7, bump=0)
        leaf = self.obj("plane", "hoja", "leaf", (0, 0, -50), (0.09, 0.06, 1), smooth=False); leaf.data.materials[0] = leafm
        random.seed(3)
        for i in range(22):
            side = random.choice((-1, 1)); x = side * random.uniform(3.3, 16); y = random.uniform(1.5, 30); h = random.uniform(3.0, 5.5)
            tr = self.obj("cylinder", f"tronco{i}", "wood", (x, y, h * 0.45), (0.14, 0.14, h * 0.45), vertices=10); tr.data.materials[0] = bark
            for j in range(4):
                c = self.obj("ico_sphere", f"copa{i}_{j}", "leaf", (x + random.uniform(-0.8, 0.8), y + random.uniform(-0.8, 0.8), h * random.uniform(0.85, 1.15)),
                             (random.uniform(0.9, 1.4),) * 3, subdivisions=2)
                c.data.materials[0] = leafm; self._scatter(c, leaf, 260, i * 10 + j, rotate=True)
        far = self.pmat("bosque", [(0.3, (0.07, 0.17, 0.04)), (0.6, (0.14, 0.28, 0.07)), (0.85, (0.25, 0.36, 0.10))], scale=1.2, rough=0.9, bump=0.4)
        for i in range(130):                                          # bosque de fondo (sin hojas sueltas: barato)
            x = random.uniform(-130, 130); y = random.uniform(32, 48) + abs(x) * 0.25; rr = random.uniform(2.5, 4.5) * (1 + abs(x) / 90)
            c = self.obj("ico_sphere", f"fondo{i}", "leaf", (x, y, rr * 1.3), (rr, rr * 0.8, rr * 1.2), subdivisions=3); c.data.materials[0] = far
        for i in range(10):                                           # piedras
            side = random.choice((-1, 1)); x = side * random.uniform(2.8, 9); y = random.uniform(-1.5, 9)
            if abs(y) < 1.2: y += 1.8
            r_ = self.obj("ico_sphere", f"piedra{i}", "rock", (x, y, 0.05), (0.28, 0.22, 0.14), subdivisions=2)
            r_.data.materials[0] = self.pmat("piedra", [(0.3, (0.35, 0.35, 0.33)), (0.7, (0.55, 0.54, 0.50))], scale=6, bump=0.5)
        # cámara baja con desenfoque (foco en el personaje: ver follow)
        self.cam.data.dof.use_dof = True; self.cam.data.dof.aperture_fstop = 2.2
        self.cam.data.lens = 45; self.cam.location = (-4.7, -6.5, 1.3)

    def env_mesa(self):
        """Encimera de cocina a escala de objetos (cerillas, juguetes): luz cálida, pared, fondo desenfocado."""
        self._sky()
        self.sc.view_settings.view_transform = "Standard"           # Standard: la llama conserva su naranja saturado
        sun = bpy.data.objects["sun"]; sun.data.energy = 0.25; sun.data.color = (1.0, 0.85, 0.7)
        self.sc.world.node_tree.nodes["Background"].inputs[1].default_value = 0.02   # interior en penumbra: la llama manda
        top = self.obj("cube", "encimera", "wood", (0, 0, -0.05), (6, 3, 0.05), smooth=False)
        top.data.materials[0] = self.pmat("encimera", [(0.3, (0.55, 0.40, 0.25)), (0.7, (0.70, 0.55, 0.36))], scale=6, rough=0.35, bump=0.1)
        wall = self.obj("cube", "pared", "white", (0, 3.2, 1.5), (8, 0.1, 3), smooth=False)
        wall.data.materials[0] = self.pmat("pared", [(0.3, (0.75, 0.72, 0.68)), (0.7, (0.85, 0.82, 0.78))], scale=3, rough=0.8, bump=0.05)
        cab = self.obj("cube", "armario", "wood", (0, 2.9, 2.2), (6, 0.35, 0.6), smooth=False)
        cab.data.materials[0] = self.pmat("armario", [(0.3, (0.25, 0.17, 0.11)), (0.7, (0.35, 0.24, 0.15))], scale=10, rough=0.5, bump=0.2)
        for i, x in enumerate((-2.5, 0, 2.5)):                       # focos cálidos bajo el armario
            li = bpy.data.objects.new(f"foco{i}", bpy.data.lights.new(f"foco{i}", "AREA")); self.sc.collection.objects.link(li)
            li.location = (x, 2.4, 1.55); li.data.energy = 35; li.data.size = 1.2; li.data.color = (1.0, 0.85, 0.65)
        self.water = None
        self.cam.data.lens = 50; self.cam.location = (0.0, -3.2, 0.55)
        self.cam.data.dof.use_dof = True; self.cam.data.dof.aperture_fstop = 1.6

    def env_rio_flat(self):
        self.obj("cube", "orillaL", "grass", (-32, 0, -1.5), (30, 60, 1.5), smooth=False)
        self.obj("cube", "orillaR", "grass", (32, 0, -1.5), (30, 60, 1.5), smooth=False)
        self.obj("cube", "lecho", "mud", (0, 0, -2.6), (2.5, 60, 1.5), smooth=False)
        self.water = self.obj("cube", "agua", "water", (0, 0, -1.75), (2.49, 60, 1.5), smooth=False)
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
    def splash(self, x, y=0, z=-0.3, n=46, big=1.0):
        """Chapuzón: corona de agua que se abre, espuma en la superficie y gotas finas."""
        self.cue("splash"); self.splashes = getattr(self, "splashes", []) + [(self.f, x, y, z)]
        rnd = random.Random(int(x * 100) + self.f); f0 = self.f; ws = -0.25
        ring = self.obj("torus", "espuma", "foam", (x, y, ws + 0.01), (0.001,) * 3, major_radius=1.0, minor_radius=0.06)
        self.key(ring, f0 - 1, scale=(0.001,) * 3); self.key(ring, f0 + 2, scale=(0.3 * big, 0.3 * big, 0.3))
        self.key(ring, f0 + 24, scale=(1.3 * big, 1.3 * big, 0.25)); self.key(ring, f0 + 40, scale=(1.6 * big, 1.6 * big, 0.001))
        for i in range(36):                                            # corona: gotas que suben en círculo
            a = i / 36 * 6.283; rr0 = 0.22 * big; sz = rnd.uniform(0.03, 0.06) * big
            d = self.obj("uv_sphere", "corona", "foam", (x, y, ws), (0.001,) * 3, segments=8, ring_count=6)
            self.key(d, f0 - 1, scale=(0.001,) * 3)
            self.key(d, f0 + 1, loc=(x + rr0 * math.cos(a), y + rr0 * math.sin(a), ws + 0.05), scale=(sz, sz, sz * 2.5))
            self.key(d, f0 + 6, loc=(x + rr0 * 1.9 * math.cos(a), y + rr0 * 1.9 * math.sin(a), ws + rnd.uniform(0.45, 0.7) * big))
            self.key(d, f0 + 14, loc=(x + rr0 * 2.8 * math.cos(a), y + rr0 * 2.8 * math.sin(a), ws), scale=(sz * 0.7,) * 3)
            self.key(d, f0 + 15, scale=(0.001,) * 3)
        for i in range(n):
            d = self.obj("uv_sphere", "gota", "foam", (x, y, z), (0.001,) * 3, segments=8, ring_count=6)
            a = rnd.uniform(0, 6.28); r = rnd.uniform(0.3, 1.2) * big; hgt = rnd.uniform(0.6, 2.0) * big; sz = rnd.uniform(0.015, 0.045) * big
            self.key(d, f0 - 1, loc=(x, y, z), scale=(0.001,) * 3); self.key(d, f0, loc=(x, y, z + 0.1), scale=(sz, sz, sz * 1.6))
            self.key(d, f0 + 7, loc=(x + r * math.cos(a) * 0.5, y + r * math.sin(a) * 0.5, z + hgt))
            self.key(d, f0 + 16, loc=(x + r * math.cos(a), y + r * math.sin(a), ws), scale=(sz * 0.6,) * 3)
            self.key(d, f0 + 17, scale=(0.001,) * 3)

    def flame(self, parent, f_on, f_off=None, size=1.0, z=0.12):
        """Llama con brillo propio y luz que parpadea, encendida en f_on (y apagada en f_off)."""
        m = self.mats.get("llama")
        if not m:
            m = bpy.data.materials.new("llama"); m.use_nodes = True; N = m.node_tree.nodes
            b = N["Principled BSDF"]; b.inputs["Base Color"].default_value = (1.0, 0.35, 0.02, 1)
            b.inputs["Emission Color"].default_value = (1.0, 0.38, 0.03, 1); b.inputs["Emission Strength"].default_value = 7.0
            self.mats["llama"] = m
        fl = self.empty("llama", (0, 0, z), parent=parent)
        core = self.mats.get("llama_nucleo")
        if not core:
            core = bpy.data.materials.new("llama_nucleo"); core.use_nodes = True; bb = core.node_tree.nodes["Principled BSDF"]
            bb.inputs["Base Color"].default_value = (1.0, 0.8, 0.3, 1); bb.inputs["Emission Color"].default_value = (1.0, 0.75, 0.25, 1)
            bb.inputs["Emission Strength"].default_value = 14.0; self.mats["llama_nucleo"] = core
        for k, (sc, zz, col) in enumerate(((1.0, 0.0, None), (0.5, -0.02, core))):
            bpy.ops.mesh.primitive_uv_sphere_add(location=(0, 0, 0.09 * size + zz), segments=16, ring_count=10)
            o = bpy.context.object; o.name = "fuego"; o.scale = (0.06 * size * sc, 0.06 * size * sc, 0.13 * size * sc); o.parent = fl
            o.data.materials.append(col or m)
            for v in o.data.vertices:                                   # forma de gota: punta arriba
                if v.co.z > 0: v.co.x *= (1 - v.co.z * 0.85); v.co.y *= (1 - v.co.z * 0.85)
        li = bpy.data.objects.new("luz_llama", bpy.data.lights.new("luz_llama", "POINT")); self.sc.collection.objects.link(li)
        li.parent = fl; li.location = (0, 0, 0.12 * size); li.data.color = (1.0, 0.6, 0.25); li.data.shadow_soft_size = 0.05
        self.key(fl, f_on - 1, scale=(0.001,) * 3); li.data.energy = 0; li.data.keyframe_insert("energy", frame=f_on - 1)
        end = f_off or (f_on + 400)
        rnd = random.Random(f_on)
        for f in range(f_on, end, 2):
            k = 1.0 if f > f_on + 3 else 1.6
            self.key(fl, f, scale=(k * rnd.uniform(0.9, 1.1), k * rnd.uniform(0.9, 1.1), k * rnd.uniform(0.85, 1.2)))
            li.data.energy = 25 * size * rnd.uniform(0.8, 1.2); li.data.keyframe_insert("energy", frame=f)
        if f_off:
            self.key(fl, f_off, scale=(0.001,) * 3); li.data.energy = 0; li.data.keyframe_insert("energy", frame=f_off)
        self.cue("ignite", f_on, vol=-4)
        return fl

    def follow(self, actor, n_frames, weight=0.75):
        """La cámara mira a un punto entre el actor y el centro de la escena."""
        for fr in range(1, n_frames + 1, 4):
            self.sc.frame_set(fr); wp = actor.root.matrix_world.translation
            hz = 0.95 if getattr(actor, "human", False) else 0.6
            self.key(self.tgt, fr, loc=(wp.x * (0.92 if hz > 0.9 else weight), 0, max(0.45, min(3.2, wp.z + hz))))   # sube con los saltos
        if self.cam.data.dof.use_dof:
            self.cam.data.dof.focus_object = self.tgt
        # la cámara acompaña al personaje en x (suave): nunca se queda diminuto al cruzar
        rig = self.empty("camara_rig", (0, 0, 0)); self.cam.parent = rig; self.cam_rig = rig
        self._rigx = {}
        for fr in range(1, n_frames + 1, 4):
            self.sc.frame_set(fr); wp = actor.root.matrix_world.translation
            rx = max(0.0, 0.9 * wp.x + 1.0); self._rigx[fr] = rx; self.key(rig, fr, loc=(rx, 0, 0))
        if os.environ.get("STUDIO_SHOTS", "1") == "1": self.auto_shots(actor, n_frames)

    def auto_shots(self, actor, n_frames):
        """Montaje dentro del nivel (como la referencia): plano general -> plano medio en la acción -> general,
        y un primer plano del chapuzón cuando lo hay. Cortes secos (interpolación constante)."""
        cam = self.cam; L0 = tuple(cam.location); lens0 = cam.data.lens
        det = self.empty("mira_detalle", (0, 0, 0))
        c2 = cam.constraints.new("TRACK_TO"); c2.target = det; c2.track_axis = "TRACK_NEGATIVE_Z"; c2.up_axis = "UP_Y"
        def put(f, loc, lens, detail=False, dloc=None):
            bpy.context.preferences.edit.keyframe_new_interpolation_type = "CONSTANT"
            cam.location = loc; cam.keyframe_insert("location", frame=f); cam.data.lens = lens; cam.data.keyframe_insert("lens", frame=f)
            c2.influence = 1.0 if detail else 0.0; c2.keyframe_insert("influence", frame=f)
            if dloc: det.location = dloc; det.keyframe_insert("location", frame=f)
        def _rz(a_, g): self.sc.frame_set(g); return a_.root.matrix_world.translation.z
        self._root_z = _rz
        def rx(f):
            self.sc.frame_set(f); return self.cam_rig.matrix_world.translation.x if getattr(self, "cam_rig", None) else 0.0
        def medium(f):
            self.sc.frame_set(f); p = actor.root.matrix_world.translation
            top = max(p.z for p in [actor.root.matrix_world.translation] + [actor.root.matrix_world.translation])
            zmax = max((self._root_z(actor, g) for g in range(f, min(n_frames, f + 40), 3)), default=p.z)   # el plano debe caber todo el salto
            return (p.x - 3.0 - rx(f), p.y - 4.4, max(1.0, min(2.6, zmax + 1.2)))
        shots = [(1, "wide")]
        if n_frames > 70: shots += [(int(n_frames * 0.38), "med"), (int(n_frames * 0.70), "wide")]
        for (fs, x, y, z) in getattr(self, "splashes", []):
            shots = [s_ for s_ in shots if not (fs - 2 <= s_[0] < fs + 20)] + [(fs - 2, ("det", x, y, z)), (fs + 20, "wide")]
        for f, kind in sorted(shots, key=lambda t: t[0]):
            if f > n_frames: continue
            if kind == "wide": put(f, L0, lens0)
            elif kind == "med": put(f, medium(f), 42)
            else:
                _, x, y, z = kind; put(f, (x - 2.4 - rx(f), y - 3.6, 1.0), 35, True, (x, y, max(z, -0.2) + 0.45))
        bpy.context.preferences.edit.keyframe_new_interpolation_type = "BEZIER"

    def ground(self, x, default=0.0):
        """Altura del suelo en x: encima del muelle 0.12, en la hierba 0; sobre el río, `default` (lo decide el nivel)."""
        if -3.5 <= x <= -1.7: return 0.12
        return 0.0 if abs(x) > 2.5 else default

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
        if lk.get("kind") == "cerilla":
            self._match(lk, x, size); self.x, self.z = x, st.ground(x) if hasattr(st, "ground") else 0.0
            self.root.location.z = self.z; return
        if lk.get("kind") == "humano":
            self._human(lk, x, size); self._hat(lk.get("hat", "ninguno"), lk.get("hat_color", "yellow"))
            self.x, self.z = x, st.ground(x); self.root.location.z = self.z; return
        color, hat, hc = lk["color"], lk["hat"], lk.get("hat_color", "yellow")
        bx, by, bz = SHAPES[lk.get("shape", "redondo")]; e = lk.get("eye", 1.0); g = lk.get("eye_gap", 0.20)
        top = 0.55 + bz * 0.92                                   # altura de la coronilla
        ey = 0.55 + bz * 0.40; fy = -by * 0.84                   # altura y profundidad de los ojos
        self.root = s.empty("pj", (x, 0, 0)); self.root.scale = (size,) * 3
        self.body = self.pivot = s.empty("cuerpo", parent=self.root)
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


    def _match(self, lk, x, size):
        """Cerilla viva: palo de madera + cabeza roja con ojos, párpados, cejas y boca. Se dobla por la mitad
        (self.body = parte alta) y puede encenderse (Stage.flame). Mide ~1 unidad: la escena la escala."""
        s = self.st; e = lk.get("eye", 1.0)
        self.root = s.empty("cerilla", (x, 0, 0)); self.root.scale = (size,) * 3
        self.pivot = s.empty("dobla", (0, 0, 0.45), parent=self.root)               # se dobla desde la mitad del palo
        s.obj("cylinder", "palo_bajo", "wood", (0, 0, 0.225), (0.045, 0.045, 0.225), parent=self.root, vertices=16)
        self.body = s.empty("cuerpo", (0, 0, 0), parent=self.pivot)
        s.obj("cylinder", "palo_alto", "wood", (0, 0, 0.22), (0.045, 0.045, 0.22), parent=self.body, vertices=16)
        s.obj("uv_sphere", "codo_palo", "wood", (0, 0, 0), (0.045, 0.045, 0.045), parent=self.pivot, segments=16, ring_count=10)   # doblez sin rotura
        H = self.head = s.empty("cabeza", (0, 0, 0.53), parent=self.body)
        s.obj("uv_sphere", "fosforo", lk.get("color", "red"), (0, 0, 0), (0.105, 0.105, 0.13), parent=H)
        ex, ey, ez, er = 0.042, -0.085, 0.02, 0.034 * e
        self.lids, self.pupils, self.arms, self.legs, self.knees, self.elbows = [], [], [], [], [], []
        self._pup = (ex, ey - er * 0.7, ez - 0.004); self._lid = (er * 1.08, er * 1.0, er * 1.08); self._lid_rest = er * 0.45
        for sx in (-1, 1):
            s.obj("uv_sphere", "ojo", "white", (ex * sx, ey, ez), (er, er * 0.7, er * 1.15), parent=H)
            self.pupils.append(s.obj("uv_sphere", "pupila", "black", (self._pup[0] * sx, self._pup[1], self._pup[2]), (er * 0.5, er * 0.2, er * 0.55), parent=H))
            lid = s.obj("uv_sphere", "parpado", lk.get("color", "red"), (ex * sx, ey - 0.003, ez + er * 0.45), (self._lid[0], self._lid[1], self._lid_rest), parent=H); self.lids.append(lid)
            s.obj("cube", "ceja", "black", (ex * sx, ey - 0.012, ez + er * 1.45), (er * 1.0, 0.008, 0.009), rot=(0, math.radians(-12 * sx), 0), parent=H, smooth=False)
        self.mouth = s.obj("uv_sphere", "boca", "black", (0, -0.098, -0.05), (0.03, 0.01, 0.008), parent=H)
        self.hat_z = 0.68; self.human = False; self.squash = 0.6

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
        r = 0.074 * wd                                                    # grosor de extremidades (humano, no palitos)
        thigh, shin = 0.40 * ht, 0.38 * ht; hip = thigh + shin + 0.08
        torso_h = 0.54 * ht; sh_z = hip + torso_h; neck = 0.09
        hz = sh_z + neck + 0.20                                           # centro de la cabeza
        # el torso gira y se encoge desde la CADERA (pivot), no desde los pies: así nunca se separa de las piernas
        self.pivot = s.empty("pelvis", (0, 0, hip), parent=self.root)
        self.body = s.empty("cuerpo", (0, 0, -hip), parent=self.pivot)
        self.knees, self.elbows = [], []
        # Esqueleto de control (empties). El cuerpo es UNA malla continua que se deforma con ellos: sin bolas ni huecos.
        for sx in (-1, 1):
            lp = s.empty("cadera", (0.105 * wd * sx, 0, hip), parent=self.root); self.legs.append(lp)
            kn = s.empty("rodilla", (0, 0, -thigh), parent=lp); self.knees.append(kn)
            s.obj("uv_sphere", "zapato", "shoe", (0, -0.07, -shin - 0.01), (0.085 * wd, 0.16, 0.062), parent=kn)
            s.obj("uv_sphere", "suela", "white", (0, -0.07, -shin - 0.045), (0.09 * wd, 0.168, 0.03), parent=kn)
        self.lids, self.pupils, self.arms = [], [], []
        ua, fa = 0.31 * ht, 0.29 * ht
        for sx in (-1, 1):
            sh = s.empty("hombro", (0.205 * wd * sx, 0, sh_z - 0.05), parent=self.body); self.arms.append(sh)
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
        chains = [[(W(B, (0, 0, d["hip"] - 0.02)), "body", 0.17 * wd, 0.115 * wd),
                   (W(B, (0, 0, d["hip"] + d["torso_h"] * 0.35)), "body", 0.155 * wd, 0.11 * wd),
                   (W(B, (0, 0, d["hip"] + d["torso_h"] * 0.72)), "body", 0.19 * wd, 0.125 * wd),
                   (W(B, (0, 0, d["sh_z"] - 0.06)), "body", 0.20 * wd, 0.11 * wd),
                   (W(B, (0, 0, d["sh_z"] + 0.02)), "body", 0.075 * wd, 0.065 * wd),
                   (W(self.head, (0, 0, -0.14)), "head", 0.062 * wd, None)]]
        for i, (lp, kn, sh, el) in enumerate(zip(self.legs, self.knees, self.arms, self.elbows)):
            sx = -1 if i == 0 else 1; gL, gK, gS, gE = f"leg{i}", f"knee{i}", f"arm{i}", f"elbow{i}"
            chains.append([(W(B, (0.04 * wd * sx, 0, d["hip"] + 0.10)), "body", r * 1.3, None),
                           (W(lp), gL, r * 1.45, None), (W(lp, (0, 0, -d["thigh"] * 0.45)), gL, r * 1.30, None),
                           (W(lp, (0, 0, -d["thigh"] * 0.86)), gL, r * 0.98, None), (W(kn), gK, r * 0.92, None),
                           (W(kn, (0, 0, -d["shin"] * 0.30)), gK, r * 1.02, None), (W(kn, (0, 0, -d["shin"] * 0.70)), gK, r * 0.78, None),
                           (W(kn, (0, 0, -d["shin"] + 0.02)), gK, r * 0.62, None)])
            chains.append([(W(B, (0.10 * wd * sx, 0, d["sh_z"] - 0.07)), "body", r * 1.0, None),
                           (W(sh), gS, r * 1.08, None), (W(sh, (0, 0, -d["ua"] * 0.45)), gS, r * 0.92, None),
                           (W(sh, (0, 0, -d["ua"] * 0.86)), gS, r * 0.76, None), (W(el), gE, r * 0.72, None),
                           (W(el, (0, 0, -d["fa"] * 0.35)), gE, r * 0.78, None), (W(el, (0, 0, -d["fa"])), gE, r * 0.55, None),
                           (W(el, (0, -0.005, -d["fa"] - 0.065)), gE, (0.045, 0.028), None)])
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
            for k, c in enumerate(ch): sv[k].radius = tuple(c[2]) if isinstance(c[2], tuple) else (c[2], c[3] or c[2])
            sv[0].use_root = True
            dg = bpy.context.evaluated_depsgraph_get()
            nm = bpy.data.meshes.new_from_object(base.evaluated_get(dg), preserve_all_data_layers=True, depsgraph=dg)
            bpy.data.objects.remove(base)
            ob = bpy.data.objects.new("cuerpo_piel", nm); s.sc.collection.objects.link(ob)
            if not ob.vertex_groups:
                for n in names: ob.vertex_groups.new(name=n)
            gi = {g.index: g.name for g in ob.vertex_groups}
            for v in nm.vertices:                                     # cada vértice: tramo más cercano y mezcla de sus dos huesos
                best = None
                for k in range(len(ch) - 1):
                    a_, b_ = ch[k][0], ch[k + 1][0]; ab = b_ - a_
                    t = max(0.0, min(1.0, (v.co - a_).dot(ab) / max(ab.length_squared, 1e-9)))
                    dist = (a_ + ab * t - v.co).length
                    if best is None or dist < best[0]: best = (dist, k, t)
                _, k, t = best
                for g in list(v.groups): ob.vertex_groups[gi[g.group]].remove([v.index])
                ga, gb = ch[k][1], ch[k + 1][1]
                if ga == gb: ob.vertex_groups[ga].add([v.index], 1.0, "REPLACE")
                else:
                    t = t * t * (3 - 2 * t)
                    ob.vertex_groups[ga].add([v.index], 1 - t, "REPLACE"); ob.vertex_groups[gb].add([v.index], t, "ADD")
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
                    if ci > 0 and z > hipz + 0.2: mi = 1 if top_style in ("camiseta", "sudadera") else 0
                elif g.startswith("leg"):
                    kz = W(self.knees[int(g[-1])]).z
                    mi = 2 if (legs_style == "largo" or (z - kz) / max(hipz - kz, 1e-3) > 0.42) else 0
                elif g.startswith("knee"):
                    mi = 2 if legs_style == "largo" else 0
                elif g.startswith("arm"):
                    mi = 1 if (top_style == "sudadera" or (top_style == "camiseta" and shz - z < d["ua"] * 0.38)) else 0
                elif g.startswith("elbow") and top_style == "sudadera":     # manga larga hasta la muñeca
                    el_ = self.elbows[int(g[-1])]; wr = W(el_, (0, 0, -d["fa"] * 0.95))
                    cen = sum((nm.vertices[k].co for k in poly.vertices), Vector()) / len(poly.vertices)
                    mi = 1 if (cen - W(el_)).length < (wr - W(el_)).length else 0
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

    def tilt(self, deg, f=None, interp="BEZIER"): self.st.key(self.pivot, f, rot=(0, math.radians(deg), 0), interp=interp)

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
        z1 = self.st.ground(x, self.z) if z is None else z
        if self.legs and sound == "boing": sound = "step"                          # los humanos dan pasos, no botes de goma
        if self.human and abs(x - self.x) > 0.05:                                  # mira hacia donde va
            tgt_yaw = 75 if x > self.x else -75
            if tgt_yaw != self.yaw: self.face(tgt_yaw, f0, turn=2)
        if self.human:
            return self._jump_human(x, z1, h, dur, sound)
        s.key(self.pivot, f0, scale=(1, 1, 1)); s.key(self.root, f0, loc=(self.x, 0, self.z))
        if not self.human: self.arms_to(10, f0)
        s.key(self.pivot, f0 + 2, scale=self._sq(1.18, 1.18, 0.78)); s.key(self.root, f0 + 2, loc=(self.x, 0, self.z))
        if not self.human: self.arms_to(-25, f0 + 2)
        if sound: s.cue(sound, f0 + 2, vol=-6)
        mid = f0 + 2 + dur // 2
        s.key(self.pivot, mid, scale=self._sq(0.88, 0.88, 1.22)); s.key(self.root, mid, loc=((self.x + x) / 2, 0, max(self.z, z1) + h))
        if not self.human: self.arms_to(95, mid)
        if self.human: self._stride(f0 + 2, mid, f0 + 2 + dur, big=h > 0.3)
        end = f0 + 2 + dur
        s.key(self.root, end, loc=(x, 0, z1)); s.key(self.pivot, end, scale=self._sq(1.25, 1.25, 0.70))
        if not self.human: self.arms_to(40, end)
        s.key(self.pivot, end + 3, scale=(1, 1, 1), interp="BACK")
        if not self.human: self.arms_to(10, end + 3)
        self.x, self.z = x, z1; s.f = end + 4

    def walk_to(self, x, steps=None, **kw):
        if self.human:
            if os.environ.get("STUDIO_MOCAP", "1") == "1" and abs(x - self.x) > 0.3:
                self.face(75 if x > self.x else -75, self.st.f, turn=3); f0 = self.st.f
                n = self.mocap("caminar", travel_to=x)
                snd = kw.get("sound", "step")
                if snd:
                    for k in range(6, n, 12): self.st.cue(snd, f0 + k, vol=-8)
                return
            return self._walk_human(x, steps, sound=kw.get("sound", "step"))
        n = steps or max(1, round(abs(x - self.x) / 0.75)); x0 = self.x
        for i in range(1, n + 1): self.hop_to(x0 + (x - x0) * i / n, h=0.07 if self.human else 0.32, dur=8 if self.human else 7, **kw)

    def _walk_human(self, x, steps=None, dur=9, sound="step"):
        """Ciclo de paso humano: contacto (piernas abiertas, cuerpo abajo) -> paso (pierna que avanza con la rodilla
        doblada, cuerpo arriba) -> contacto con la otra pierna. Avance lineal para que el pie apoyado no resbale;
        cadera que gira y se balancea, brazos al contrario que las piernas y cabeza que compensa."""
        s = self.st; x0, z0 = self.x, self.z; dist = abs(x - x0)
        if dist < 0.05: return
        n = steps or max(2, round(dist / 0.62)); step = dist / n
        L = self._dims["thigh"] + self._dims["shin"]; a = math.degrees(math.asin(min(0.9, step / 2 / L))) * 1.05
        self.face(75 if x > x0 else -75, s.f, turn=3)
        f0 = s.f; z1 = s.ground(x, z0)
        def legs(f, lead, spread, kl, kb):                      # lead = pierna adelantada (0/1)
            for i, (lg, kn) in enumerate(zip(self.legs, self.knees)):
                fw = i == lead
                s.key(lg, f, rot=(math.radians(-spread if fw else spread), 0, 0)); s.key(kn, f, rot=(math.radians(kl if fw else kb), 0, 0))
        def arms(f, lead, sw):
            for i, (sh, el) in enumerate(zip(self.arms, self.elbows)):
                sx = -1 if i == 0 else 1; fw = i != lead                # brazo contrario a la pierna adelantada
                s.key(sh, f + 1, rot=(math.radians(-sw if fw else sw * 0.8), math.radians(-7 * sx), 0))
                s.key(el, f + 2, rot=(math.radians(-28 if fw else -10), 0, 0))
        for k in range(n + 1):
            fc = f0 + k * dur; lead = k % 2; t = k / n
            last = k == n
            sp = 0.0 if last else a
            legs(fc, lead, sp, 4, 12); arms(fc, lead, 0 if last else a * 0.75)
            zc = z0 + (z1 - z0) * t
            s.key(self.root, fc, loc=(x0 + (x - x0) * t, 0, zc - (0 if last or k == 0 else 0.03 * step / 0.62)), interp="LINEAR")
            s.key(self.pivot, fc, rot=(math.radians(4 if not last else 0), math.radians(3 if lead else -3) * (not last), math.radians(6 if lead else -6) * (not last)))
            s.key(self.head, fc + 1, rot=(math.radians(-3 if not last else 0), 0, math.radians(-5 if lead else 5) * (not last)))
            if k > 0 and sound: s.cue(sound, fc, vol=-8)
            if not last:                                             # posición de paso, a mitad de camino
                fm = fc + dur // 2; sw = 1 - lead
                for i, (lg, kn) in enumerate(zip(self.legs, self.knees)):
                    swing = i == sw
                    s.key(lg, fm, rot=(math.radians(-a * 0.35 if swing else a * 0.15), 0, 0)); s.key(kn, fm, rot=(math.radians(55 if swing else 6), 0, 0))
                tm = (k + 0.5) / n
                s.key(self.root, fm, loc=(x0 + (x - x0) * tm, 0, z0 + (z1 - z0) * tm + 0.015), interp="LINEAR")
        self.x, self.z = x, z1; s.f = f0 + n * dur + 2

    def _jump_human(self, x, z1, h, dur, sound):
        """Salto humano: se agacha (anticipación), se impulsa con los brazos, encoge las piernas en el aire,
        cae doblando las rodillas y se levanta."""
        s, f0 = self.st, self.st.f
        T = self._dims["thigh"]; Sh = self._dims["shin"]
        def crouch(f, th, kn, lean, arm, zbase, xx, interp="BEZIER"):
            drop = (T + Sh) - (T * math.cos(math.radians(th)) + Sh * math.cos(math.radians(kn - th)))
            for lg in self.legs: s.key(lg, f, rot=(math.radians(-th), 0, 0), interp=interp)
            for k in self.knees: s.key(k, f, rot=(math.radians(kn), 0, 0), interp=interp)
            for i, sh in enumerate(self.arms): s.key(sh, f, rot=(math.radians(arm), math.radians(-8 * (-1 if i == 0 else 1)), 0), interp=interp)
            s.key(self.pivot, f, rot=(math.radians(lean), 0, 0), interp=interp)
            s.key(self.root, f, loc=(xx, 0, zbase - drop), interp=interp)
        x0, z0 = self.x, self.z; big = h > 0.3
        crouch(f0, 0, 0, 0, 0, z0, x0)
        crouch(f0 + 3, 32 if big else 20, 60 if big else 40, 18 if big else 10, 35, z0, x0)       # se agacha, brazos atrás
        if sound: s.cue(sound, f0 + 3, vol=-6)
        fu = f0 + 5
        crouch(fu, 5, 5, 4, -70 if big else -40, z0, x0 + (x - x0) * 0.08)                           # despega estirado
        mid = fu + dur // 2
        crouch(mid, 45 if big else 25, 80 if big else 45, 8, -110 if big else -50, max(z0, z1) + h + (0.15 if big else 0.05), (x0 + x) / 2)
        end = fu + dur
        crouch(end - 2, 20, 25, 4, -40, z1 + 0.04, x - (x - x0) * 0.04)
        crouch(end, 35 if big else 22, 65 if big else 42, 15 if big else 8, 20, z1, x)                # aterriza amortiguando
        crouch(end + 5, 0, 0, 0, 0, z1, x)
        for el in self.elbows: s.key(el, f0, rot=(math.radians(-15), 0, 0)); s.key(el, mid, rot=(math.radians(-35), 0, 0)); s.key(el, end + 5, rot=(math.radians(-12), 0, 0))
        self.x, self.z = x, z1; s.f = end

    # --- captura de movimiento real (anim/mocap.py) ---
    def mocap(self, name, frames=None, travel_to=None, root=True, start=0.0, strength=1.0, head=0.7, step=1):
        """Aplica un clip de captura real al personaje desde el fotograma actual.
        frames: cuántos fotogramas (24 fps) usar; travel_to: x final (escala el avance para llegar justo ahí y corta
        el clip cuando llega); root=False: solo la pose (la trayectoria la pone el gag); start: segundo del clip
        donde empezar. Devuelve el número de fotogramas aplicados y avanza el tiempo."""
        from mathutils import Vector, Matrix
        import mocap as MC
        s = self.st; clip = MC.Clip(name); d = self._dims
        idx = MC_frames = clip.frames_at(FPS); k0 = int(start / (clip.dt * FPS) / 1) if False else int(round(start * FPS))
        idx = idx[k0:]
        r, fw, up = clip.basis()
        # rumbo suavizado (media móvil de 0,6 s): quita el balanceo de cadera del rumbo pero lo deja en la pose
        win = max(1, int(0.3 / clip.dt)); ker = np.ones(2 * win + 1) / (2 * win + 1)
        rs = np.stack([np.convolve(np.pad(r[:, i], win, mode="edge"), ker, "valid") for i in range(3)], 1)
        rs /= np.linalg.norm(rs, axis=1, keepdims=True) + 1e-9; fs = np.cross(up, rs)
        J = lambda n_, i: clip.P[i, clip.idx[n_]]
        foot0 = min(clip.j("LeftFoot")[:, 2].min(), clip.j("RightFoot")[:, 2].min())
        sc = (d["thigh"] + d["shin"] + 0.08) / max(1e-6, J("Hips", idx[0])[2] - foot0)
        def loc(v, i):                                      # vector del mundo BVH -> marco del personaje (x der, -y adelante, z arriba)
            return Vector((float(-(v @ rs[i])), float(-(v @ fs[i])), float(v[2])))   # mirando a -y, la derecha es -x
        h0 = J("Hips", idx[0]); f0 = s.f; x0, z0 = self.x, self.z
        sign = 1 if math.sin(math.radians(self.yaw)) >= 0 else -1                      # hacia dónde mira (eje x del mundo)
        if travel_to is not None:
            dist = abs(travel_to - x0); fwd = [float((J("Hips", i) - h0) @ fs[idx[0]]) * sc for i in idx]
            tot = max(fwd) if max(fwd) > 1e-3 else 1.0
            cut = next((k for k, v in enumerate(fwd) if v >= dist), len(fwd) - 1)
            if fwd[cut] < dist * 0.97: k_scale = dist / max(fwd[cut], 1e-3)
            else: k_scale = 1.0
            idx = idx[:cut + 1]
        if frames: idx = idx[:frames]
        Z = Vector((0, 0, -1)); U = Vector((0, 0, 1))
        def lerp_q(q):                                       # intensidad (1 = como la captura)
            return Quaternion().slerp(q, strength) if strength < 1 else q
        from mathutils import Quaternion
        for k, i in enumerate(idx):
            if k % step and k != len(idx) - 1: continue
            fr = f0 + k
            sp = loc(J("Neck", i) - J("Hips", i), i).normalized(); rt = loc(J("LeftArm", i) - J("RightArm", i), i)   # eje +x local
            x_ = (rt - sp * rt.dot(sp)).normalized(); y_ = sp.cross(x_)
            Rt = Matrix((x_, y_, sp)).transposed()                                      # torso (pivote)
            qt = lerp_q(Rt.to_quaternion()); s.key(self.pivot, fr, rot=qt.to_euler())
            Rti = qt.to_matrix().inverted()
            for side, (lg, kn, sh, el) in enumerate(zip(self.legs, self.knees, self.arms, self.elbows)):
                P_ = "Right" if side == 0 else "Left"                                    # legs[0] está en -x = su lado derecho
                th = loc(J(P_ + "Leg", i) - J(P_ + "UpLeg", i), i); sh_ = loc(J(P_ + "Foot", i) - J(P_ + "Leg", i), i)
                qth = Z.rotation_difference(th); qkn = Z.rotation_difference(qth.to_matrix().inverted() @ sh_)
                s.key(lg, fr, rot=lerp_q(qth).to_euler()); s.key(kn, fr, rot=lerp_q(qkn).to_euler())
                ua = Rti @ loc(J(P_ + "ForeArm", i) - J(P_ + "Arm", i), i); fa = loc(J(P_ + "Hand", i) - J(P_ + "ForeArm", i), i)
                qua = Z.rotation_difference(ua); qfa = Z.rotation_difference(qua.to_matrix().inverted() @ (Rti @ fa))
                s.key(sh, fr, rot=lerp_q(qua).to_euler()); s.key(el, fr, rot=lerp_q(qfa).to_euler())
            nk = Rti @ loc(J("Head", i) - J("Neck", i), i)
            s.key(self.head, fr, rot=Quaternion().slerp(U.rotation_difference(nk), head).to_euler())
            if root:
                dv = J("Hips", i) - h0; fwd_ = float(dv @ fs[idx[0]]) * sc * (k_scale if travel_to is not None else 1.0)
                zz = z0 + float(dv[2]) * sc
                if travel_to is not None: zz += (s.ground(travel_to, z0) - z0) * k / max(1, len(idx) - 1)
                s.key(self.root, fr, loc=(x0 + sign * fwd_, 0, zz))
        if root:
            self.x = travel_to if travel_to is not None else x0 + sign * float((J("Hips", idx[-1]) - h0) @ fs[idx[0]]) * sc
            self.z = s.ground(self.x, z0) if travel_to is not None else z0
            s.key(self.root, f0 + len(idx) - 1, loc=(self.x, 0, self.z))
        s.f = f0 + len(idx); return len(idx)

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
        if self.human and os.environ.get("STUDIO_MOCAP", "1") == "1":
            self.mocap("pensar", frames=n, root=False, strength=0.8); return
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
        s.key(self.root, f + 16, loc=(self.x + dx, 0, depth)); s.key(self.pivot, f + 16, scale=(0.85, 0.85, 1.3)); self.arms_to(170, f + 14)
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
