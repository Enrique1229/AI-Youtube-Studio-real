"""mixamo.py — personajes y animaciones de Mixamo (FBX) dentro del kit, para episodios 9+.

    from mixamo import MixamoActor
    a = MixamoActor(S, x=-3.0, yaw=75)          # personaje + todas las animaciones de assets/mixamo/
    a.play("Victory")                            # reproduce un clip en el sitio (avanza S.f)
    a.walk_to(-1.0)                              # anda hasta x moviendo la raíz (clip de andar en bucle, en el sitio)
    a.play("Jumping", travel_to=0.5)             # clip con desplazamiento repartido por la raíz

Clips: se cargan de cada .fbx de assets/mixamo/ (nombre del archivo = nombre del clip). El primero que tenga malla
("With Skin") aporta el personaje; de los demás solo se toma la animación. Todas se ponen "en el sitio" (sin
avance horizontal de la cadera): el avance lo da la raíz, para que la cámara y los gags controlen la posición.
Transiciones con fundido (NLA). Comprobaciones: verify() exige clips con fotogramas y tiras NLA que cubran el nivel.
"""
import math, os, pathlib
import bpy

ROOT = pathlib.Path(__file__).resolve().parent.parent
FOLDER = ROOT / "assets" / "mixamo"
HIPS = 'pose.bones["mixamorig:Hips"].location'


def _fcurves(action):
    if hasattr(action, "fcurves") and len(getattr(action, "fcurves", [])): return list(action.fcurves)
    return [fc for l in getattr(action, "layers", []) for st in l.strips for cb in st.channelbags for fc in cb.fcurves]


class MixamoError(RuntimeError):
    pass


class MixamoActor:
    human = True

    def __init__(self, S, x=0.0, yaw=0.0, folder=FOLDER, character=None, scale=1.0, use=None):
        self.st = S; self.x, self.z, self.yaw = x, S.ground(x) if hasattr(S, "ground") else 0.0, yaw
        files = sorted(pathlib.Path(folder).glob("*.fbx"))
        if not files: raise MixamoError(f"no hay archivos .fbx en {folder}")
        if character: files = sorted(files, key=lambda f: f.stem != character)
        if use:                                                   # solo los clips que el nivel usa (cada FBX pesa ~55 MB)
            missing = [u for u in use if u not in {f.stem for f in files}]
            if missing: raise MixamoError(f"faltan clips en {folder}: {missing}")
            files = [f for f in files if f.stem in use]
        self.clips, self.arm, self.meshes = {}, None, []
        for f in files:
            before = set(bpy.data.objects)
            bpy.ops.import_scene.fbx(filepath=str(f))
            new = [o for o in bpy.data.objects if o not in before]
            arm = next((o for o in new if o.type == "ARMATURE"), None)
            if not arm or not arm.animation_data or not arm.animation_data.action:
                for o in new: bpy.data.objects.remove(o, do_unlink=True)
                continue
            act = arm.animation_data.action; act.name = f.stem; act.use_fake_user = True
            self.clips[f.stem] = act
            meshes = [o for o in new if o.type == "MESH"]
            if self.arm is None and meshes:
                self.arm, self.meshes = arm, meshes
            else:
                for o in new: bpy.data.objects.remove(o, do_unlink=True)
        if self.arm is None: raise MixamoError("ningún .fbx trae el personaje (descarga uno 'With Skin')")
        for act in self.clips.values(): self._in_place(act)
        self._matte()
        self.arm.animation_data.action = None
        # raíz para colocar/girar/desplazar; la cabeza (para cámara y encuadre) sigue al hueso Head
        self.root = S.empty("mixamo_raiz", (x, 0, self.z)); self.root.rotation_euler = (0, 0, math.radians(yaw)); self.root.scale = (scale,) * 3
        self.arm.parent = self.root
        self.head = S.empty("mixamo_cabeza", (0, 0, 0))
        self.head.parent = self.arm; self.head.parent_type = "BONE"; self.head.parent_bone = "mixamorig:Head"
        self.tracks = [self.arm.animation_data.nla_tracks.new() for _ in range(2)]        # dos pistas: los clips se solapan al fundirse
        for i, t in enumerate(self.tracks): t.name = f"gag{i}"
        self.strips = []

    def _in_place(self, act):
        """Quita el avance horizontal de la cadera (en Mixamo: ejes x y z locales, Y es arriba)."""
        for fc in _fcurves(act):
            if fc.data_path == HIPS and fc.array_index in (0, 2):
                v0 = fc.keyframe_points[0].co[1] if fc.keyframe_points else 0.0
                for k in fc.keyframe_points:
                    k.co[1] = v0; k.handle_left[1] = v0; k.handle_right[1] = v0

    def _matte(self):
        """Mixamo exporta materiales muy brillantes: tela y piel mates."""
        for o in self.meshes:
            for m in o.data.materials:
                if not m or not m.use_nodes: continue
                b = m.node_tree.nodes.get("Principled BSDF")
                if not b: continue
                for k, v in (("Roughness", 0.75), ("Specular IOR Level", 0.25), ("Metallic", 0.0)):
                    if k in b.inputs:
                        for l in list(b.inputs[k].links): m.node_tree.links.remove(l)
                        b.inputs[k].default_value = v

    def clip_frames(self, name):
        a = self.clips[name]; return int(a.frame_range[1] - a.frame_range[0])

    def play(self, name, frames=None, speed=1.0, blend=4, travel_to=None, repeat=1):
        """Añade el clip `name` en S.f (con fundido). frames: recorta; repeat: bucle; travel_to: x final de la raíz."""
        if name not in self.clips: raise MixamoError(f"no existe el clip '{name}'. Hay: {sorted(self.clips)}")
        S = self.st; a = self.clips[name]; f0 = S.f
        st = self.tracks[len(self.strips) % 2].strips.new(f"{name}_{f0}", int(f0), a)
        st.scale = 1.0 / speed; st.repeat = repeat
        if frames: st.frame_end = f0 + frames
        st.blend_in = st.blend_out = blend if self.strips else 0
        st.use_auto_blend = False; st.extrapolation = "HOLD_FORWARD"
        try: st.action_slot = a.slots[0]
        except Exception: pass
        n = int(st.frame_end - st.frame_start)
        if travel_to is not None:
            S.key(self.root, f0, loc=(self.x, 0, self.z), interp="LINEAR")
            z1 = S.ground(travel_to, self.z) if hasattr(S, "ground") else self.z
            S.key(self.root, f0 + n, loc=(travel_to, 0, z1), interp="LINEAR"); self.x, self.z = travel_to, z1
        self.strips.append(st); S.f = f0 + n - (blend if blend else 0)
        return n

    def face(self, deg, f=None, turn=4):
        S = self.st; f = S.f if f is None else f
        S.key(self.root, f, rot=(0, 0, math.radians(self.yaw))); self.yaw = deg
        S.key(self.root, f + turn, rot=(0, 0, math.radians(deg)))

    def walk_to(self, x, clip=None, stride=0.75):
        """Anda hasta x: clip de andar en bucle (en el sitio) + raíz desplazándose a velocidad constante."""
        clip = clip or next((c for c in self.clips if "walk" in c.lower()), None)
        if not clip: raise MixamoError("no hay clip de andar (descarga 'Walking')")
        self.face(90 if x > self.x else -90, self.st.f, turn=3)
        steps = max(1, round(abs(x - self.x) / (stride * 2)))
        return self.play(clip, repeat=steps, travel_to=x)

    def verify(self, n_frames):
        """El personaje debe tener clips con fotogramas y tiras NLA que cubran el nivel."""
        probs = []
        if not self.clips: probs.append("sin clips")
        for k, a in self.clips.items():
            if not any(len(fc.keyframe_points) > 1 for fc in _fcurves(a)): probs.append(f"clip {k} sin fotogramas")
        if not self.strips: probs.append("el personaje no tiene ninguna animación en el nivel")
        elif max(s.frame_end for s in self.strips) < n_frames * 0.6: probs.append("las animaciones no cubren el nivel")
        if probs: raise MixamoError("; ".join(probs))
