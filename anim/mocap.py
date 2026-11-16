"""mocap.py — captura de movimiento real (CMU Graphics Lab Motion Capture Database, sin restricciones de uso)
aplicada a los personajes del kit.

Cómo funciona (adaptación por direcciones, robusta a proporciones distintas):
  1. Lee el BVH y calcula la posición en el mundo de cada articulación en cada fotograma (cinemática directa).
  2. Pasa todo al marco del personaje (derecha, adelante, arriba) usando la orientación media de su cadera.
  3. Para cada segmento (muslo, espinilla, brazo, antebrazo, torso, cuello) calcula la rotación que lleva el
     segmento de reposo de nuestro personaje a la dirección grabada, en el espacio de su padre.
  4. El desplazamiento de la cadera se escala a la altura de nuestro personaje.

Clips en anim/mocap/*.bvh (ver anim/mocap/CLIPS.md). Uso desde un episodio:  a.mocap("caminar", frames=40)
"""
import math, os, re
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
CLIPS = {  # nombre: (archivo, fotograma inicial y final en el BVH a 120 fps; None = todo)
    "caminar": ("08_01.bvh", 40, None),
    "correr": ("02_03.bvh", 0, None),
    "saltar": ("16_05.bvh", 0, None),
    "saltar_alto": ("13_11.bvh", 0, None),
    "remar": ("79_95.bvh", 0, None),
    "contento": ("79_69.bvh", 0, None),
    "pensar": ("77_01.bvh", 120, None),             # mirar alrededor, pensativo
    "mirar": ("77_01.bvh", 0, None),
    "saludar": ("13_26.bvh", 0, 900),
    "empujar": ("81_05.bvh", 0, None),
}


def _euler(order, angles):
    """Matriz de rotación a partir de los canales del BVH (grados, en el orden de los canales)."""
    M = np.eye(3)
    for ax, a in zip(order, np.radians(angles)):
        c, s = math.cos(a), math.sin(a)
        R = {"X": np.array([[1, 0, 0], [0, c, -s], [0, s, c]]), "Y": np.array([[c, 0, s], [0, 1, 0], [-s, 0, c]]),
             "Z": np.array([[c, -s, 0], [s, c, 0], [0, 0, 1]])}[ax]
        M = M @ R
    return M


def load_bvh(path):
    txt = open(path).read(); head, motion = txt.split("MOTION")
    joints, stack, cur = [], [], None
    for line in head.splitlines():
        t = line.split()
        if not t: continue
        if t[0] in ("ROOT", "JOINT"):
            cur = {"name": t[1], "parent": stack[-1] if stack else None, "chan": []}; joints.append(cur)
        elif t[0] == "End":
            cur = {"name": joints[-1]["name"] + "_end", "parent": stack[-1], "chan": [], "end": True}; joints.append(cur)
        elif t[0] == "{": stack.append(len(joints) - 1)
        elif t[0] == "}": stack.pop()
        elif t[0] == "OFFSET": cur["off"] = np.array([float(v) for v in t[1:4]])
        elif t[0] == "CHANNELS": cur["chan"] = t[2:]
    lines = motion.strip().splitlines()
    dt = float(lines[1].split(":")[1]); data = np.array([[float(v) for v in l.split()] for l in lines[2:] if l.strip()])
    return joints, data, dt


def world_positions(joints, data):
    """Posiciones (F, J, 3) en Z arriba (x derecha, y = -z del BVH, z = y del BVH)."""
    F = len(data); J = len(joints); P = np.zeros((F, J, 3)); R = np.zeros((F, J, 3, 3))
    for f in range(F):
        k = 0
        for j, jt in enumerate(joints):
            loc = jt["off"].copy(); rot = []
            for ch in jt["chan"]:
                v = data[f, k]; k += 1
                if ch.endswith("position"): loc["XYZ".index(ch[0])] = v
                else: rot.append((ch[0], v))
            Rl = _euler([a for a, _ in rot], [v for _, v in rot]) if rot else np.eye(3)
            p = jt["parent"]
            if p is None: R[f, j] = Rl; P[f, j] = loc
            else: R[f, j] = R[f, p] @ Rl; P[f, j] = P[f, p] + R[f, p] @ jt["off"]
    conv = np.array([[1, 0, 0], [0, 0, -1], [0, 1, 0]])        # Y arriba -> Z arriba (rotación propia)
    return P @ conv.T


class Clip:
    def __init__(self, name):
        fn, a, b = CLIPS[name]
        joints, data, dt = load_bvh(os.path.join(HERE, "mocap", fn))
        data = data[a:b]
        self.dt = dt; self.idx = {j["name"]: i for i, j in enumerate(joints)}
        self.P = world_positions(joints, data)
        self.n = len(self.P)

    def j(self, name): return self.P[:, self.idx[name]]

    def frames_at(self, fps):
        """Índices del BVH para muestrear a `fps`."""
        step = 1.0 / (fps * self.dt); return [int(round(i * step)) for i in range(int(self.n / step))]

    def basis(self):
        """Marco del personaje por fotograma: derecha, adelante, arriba (a partir de las caderas)."""
        r = self.j("RightUpLeg") - self.j("LeftUpLeg"); r[:, 2] = 0
        r /= np.linalg.norm(r, axis=1, keepdims=True) + 1e-9
        up = np.tile([0, 0, 1.0], (len(r), 1)); fw = np.cross(up, r)
        return r, fw, up
