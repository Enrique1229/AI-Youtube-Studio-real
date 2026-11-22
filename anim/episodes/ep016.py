"""ep016 — Every IQ Level Rides the Merry-Go-Round (story-019, idea b20261122-3-i03). Zona de juegos de un parque (realista, humano de
Mixamo con el protagonista de dibujo de klunk_toon). Sin río ni muelle: césped, suelo de goma, cielo HDRI.

TIOVIVO: disco de 8 cuñas de colores (arcoíris, radio 1,6 m, corona de 0,95 a 1,6 m) que gira a OM0 = 2,4 rad/s; 4 barras rojas verticales
(1,95 m, con pomo blanco) en el borde, articuladas en la base (cuando el disco se desboca se abaten hacia fuera como una hélice).
CENTRO FIJO (no gira): placa-pedal amarilla y negra con 8 pilotos (rojos) y un taburete amarillo. Sobre el centro, un pescante con
BANDERÍN rojo y blanco grande y PELOTA amarilla grande con cinturón negro que giran despacio (eje en el centro).
CAUSA VISIBLE DE LA ACELERACIÓN (mejora del crítico): el taburete del centro es un PEDAL. Al sentarse, la placa se hunde 3 cm (clunk),
los pilotos pasan de rojo a verde (ding) y entonces el disco acelera con un riser; el banderín se agita con la corriente.

El humano va emparentado al disco (root.parent = disco); cada nivel calcula la posición en el mundo y la convierte a local por fotograma.
Convenio: yaw 0 = mira a cámara (-y); mira hacia (sin yaw, -cos yaw). El disco gira en sentido antihorario (visto desde arriba): la parte
cercana a cámara va de izquierda a derecha.

-380 corre alrededor del disco, intenta subirse por el borde y la barra que llega por detrás lo lanza girando como una peonza; acaba enfadado;
-70 corre junto a una barra, se cuelga de ella y sale volando horizontal como una bandera; se suelta y cae rodando por el suelo;
200 salta al disco, resbala hacia fuera y se queda pegado y plano a una barra, temblando; el banderín del centro casi no se mueve;
950 corre a la misma velocidad que el borde, salta con aterrizaje perfecto y se sienta en un banco del disco, riendo (ding y risa);
4800 mira el centro, espera el hueco entre barras, cruza, se sienta en el taburete-pedal: la placa se hunde, pilotos verdes, el disco se
desboca (arcoíris), las barras se abaten como hélice y él queda quieto y sonriente bajo el banderín (tada); el disco frena con un clunk."""
import math
import os
import bpy
import bmesh
from mathutils import Vector, Matrix, Euler
from mixamo import MixamoActor
from klunk_toon import apply as klunk, expression, blink

TITLE = "Every IQ Level Rides the Merry-Go-Round"
ONSCREEN = "Every IQ level rides the merry-go-round"
ENV = "parque"
CUSTOM_CAMERA = True
LABEL_STYLE = "big"

# ---- geometría (metros)
R_DISC, R_IN = 1.40, 0.88                  # corona del disco
TOP = 0.005                                # cara superior del disco y de la placa (el suelo está en z=0)
POST_R, POST_Z0, POST_Z1 = 1.42, 0.15, 2.05  # barras: radio, base articulada y punta
SEAT_Z = 0.46                              # cara superior del taburete y del banco (la pose Sitting Idle pide cadera a 0,55)
OM0 = 2.4 / 24.0                           # rad por fotograma (2,4 rad/s)
GALLOWS_Z = 3.5
ARM_L = 0.32                               # asa de las barras (hacia fuera, en la punta)
CAM = dict(pos=(0.0, -9.5, 5.0), tgt=(0.0, 0.0, 1.5), lens=37)


def R(d): return math.radians(d)
def D(r): return math.degrees(r)
def Rz(d): return Matrix.Rotation(R(d), 4, "Z")
def Ry(d): return Matrix.Rotation(R(d), 4, "Y")
def Rx(d): return Matrix.Rotation(R(d), 4, "X")
def Tm(v): return Matrix.Translation(Vector(v))


def sstep(t): t = max(0.0, min(1.0, t)); return t * t * (3 - 2 * t)
def eout(t): t = max(0.0, min(1.0, t)); return 1 - (1 - t) ** 2


# ------------------------------------------------------------------ giro del disco (tabla por nivel)
class CUR: al = [0.0, 0.0]; ph = 0.0


def make_alpha(n, omega):
    al = [0.0] * (n + 3)
    for f in range(1, n + 2): al[f + 1] = al[f] + omega(f)
    CUR.al = al
    return al


def A(f):
    f = int(round(f)); f = max(1, min(len(CUR.al) - 1, f)); return CUR.al[f]


def polar(r, deg, z=0.0): return Vector((r * math.cos(R(deg)), r * math.sin(R(deg)), z))


# ------------------------------------------------------------------ materiales y utilidades (como ep014)
def mmat(S, name, rgb, rough=0.5, metal=0.0, emit=None, spec=None):
    k = "m_" + name
    if k in S.mats: return S.mats[k]
    m = bpy.data.materials.new(k); m.use_nodes = True
    b = m.node_tree.nodes["Principled BSDF"]
    b.inputs["Base Color"].default_value = (*rgb, 1); b.inputs["Roughness"].default_value = rough; b.inputs["Metallic"].default_value = metal
    if spec is not None and "Specular IOR Level" in b.inputs: b.inputs["Specular IOR Level"].default_value = spec
    if emit:
        b.inputs["Emission Color"].default_value = (*emit[:3], 1); b.inputs["Emission Strength"].default_value = emit[3]
    S.mats[k] = m
    return m


def O(S, prim, name, mat, loc=(0, 0, 0), scale=(1, 1, 1), rot=(0, 0, 0), parent=None, smooth=True, **kw):
    o = S.obj(prim, name, "white", loc, scale, rot, parent, smooth, **kw); o.data.materials[0] = mat; return o


def box(S, name, mat, dims, loc, parent=None, rot=(0, 0, 0)):
    o = S.obj("cube", name, "white", loc, (dims[0] / 2, dims[1] / 2, dims[2] / 2), rot, None, False)
    o.data.materials[0] = mat
    for o2 in bpy.context.view_layer.objects: o2.select_set(False)
    bpy.context.view_layer.objects.active = o; o.select_set(True)
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    if parent: o.parent = parent
    return o


def cam_fixed(S):
    S.cam.location = CAM["pos"]; S.cam.data.lens = CAM["lens"]; S.tgt.location = CAM["tgt"]
    S.cam.keyframe_insert("location", frame=1); S.cam.data.keyframe_insert("lens", frame=1); S.tgt.keyframe_insert("location", frame=1)
    S.cam.data.dof.use_dof = False


def cam_follow(S, a, n, pos_keys, lens_keys, fixed_tgt=None):
    """Cámara de plano medio: posición y focal por claves (lineales); la mirada sigue a la cabeza (suavizada +-3 fotogramas).
    fixed_tgt = [(f, Vector)] funde hacia un punto fijo (planos finales). Mantiene el horizonte fuera del cuadro (picada >= 0,6 x semicampo)."""
    def lin(keys, f):
        if f <= keys[0][0]: return keys[0][1]
        for (f0, v0), (f1, v1) in zip(keys, keys[1:]):
            if f <= f1: t = (f - f0) / float(f1 - f0); return v0 + (v1 - v0) * t
        return keys[-1][1]
    raw = {}
    for f in range(1, n + 1):
        S.sc.frame_set(f); bpy.context.view_layer.update(); raw[f] = a.head.matrix_world.translation.copy()
    bpy.context.preferences.edit.keyframe_new_interpolation_type = "LINEAR"
    for f in list(range(1, n + 1, 2)) + [n]:
        ws = [raw[g] for g in range(max(1, f - 3), min(n, f + 3) + 1)]
        h = sum(ws, Vector((0, 0, 0))) / len(ws); tg = Vector((h.x, h.y, h.z - 0.05))
        if fixed_tgt:
            wgt = 0.0
            for (f0, v0), (f1, v1) in zip(fixed_tgt, fixed_tgt[1:] + [(10 ** 6, fixed_tgt[-1][1])]):
                pass
            k = lin([(ff, Vector((i, 0, 0))) for i, (ff, vv) in enumerate(fixed_tgt)], f)
            wgt = 0.0 if f <= fixed_tgt[0][0] else min(1.0, (f - fixed_tgt[0][0]) / float(max(1, fixed_tgt[1][0] - fixed_tgt[0][0])))
            tg = tg.lerp(fixed_tgt[1][1], sstep(wgt))
        S.cam.location = lin(pos_keys, f); S.cam.data.lens = lin(lens_keys, f); S.tgt.location = tg
        S.cam.keyframe_insert("location", frame=f); S.cam.data.keyframe_insert("lens", frame=f); S.tgt.keyframe_insert("location", frame=f)
    S.cam.data.dof.use_dof = False


def faces(a, ev, n_end, first_blink=16, every=56):
    f = first_blink
    while f < n_end - 6:
        blink(a, f); f += every
    for f, name, v in ev: expression(a, name, f, v, ramp=3)


def seg(S, a, clip, f0, f1=None, start=0, speed=1.0, blend=4, repeat=None):
    """Reproduce el clip desde f0 hasta f1 (o hasta el final); repite el clip las veces que haga falta."""
    S.f = f0
    cl = a.clips[clip]; per = max(1, int((cl.frame_range[1] - cl.frame_range[0] - start) / speed))
    if f1 is None: a.play(clip, frames=None, speed=speed, blend=blend, start=start, repeat=repeat or 1)
    else:
        n = f1 - f0 + blend
        a.play(clip, frames=n, speed=speed, blend=blend, start=start, repeat=repeat or (n // per + 2))


# ------------------------------------------------------------------ entorno
def clear_env(S):
    """Quita del parque el río, el muelle, las orillas, la hierba y los árboles cercanos: queda el cielo HDRI, la luz y árboles lejanos."""
    for o in list(S.sc.objects):
        if o.instance_type == "COLLECTION":
            if o.location.y < 14.0 or abs(o.location.x) < 12.0 and o.location.y < 22.0: bpy.data.objects.remove(o, do_unlink=True)
        elif o.name.startswith(("orilla", "lecho", "agua", "muelle", "prado", "hierba", "suelo_rio")):
            bpy.data.objects.remove(o, do_unlink=True)
    S.water = None
    import env_real
    g = env_real._pbr(S, "aerial_grass_rock", scale=60.0)
    bpy.ops.mesh.primitive_plane_add(size=1, location=(0, 40, 0)); fl = bpy.context.object; fl.name = "cesped"; fl.scale = (4000, 4000, 1)
    fl.data.materials.append(g)


def ring(S, name, mat, r0, r1, z0, z1, n=96):
    """Corona completa (sin costura): caras superior, inferior, exterior e interior."""
    vs = [(r * math.cos(R(360.0 * i / n)), r * math.sin(R(360.0 * i / n)), z) for z in (z1, z0) for r in (r0, r1) for i in range(n)]
    ix = lambda ly, rg, i: ly * 2 * n + rg * n + (i % n)
    fs = []
    for i in range(n):
        fs.append((ix(0, 0, i), ix(0, 1, i), ix(0, 1, i + 1), ix(0, 0, i + 1)))
        fs.append((ix(1, 0, i + 1), ix(1, 1, i + 1), ix(1, 1, i), ix(1, 0, i)))
        fs.append((ix(0, 1, i), ix(1, 1, i), ix(1, 1, i + 1), ix(0, 1, i + 1)))
        fs.append((ix(0, 0, i + 1), ix(1, 0, i + 1), ix(1, 0, i), ix(0, 0, i)))
    me = bpy.data.meshes.new(name); me.from_pydata(vs, [], fs); me.update()
    bm = bmesh.new(); bm.from_mesh(me); bmesh.ops.recalc_face_normals(bm, faces=bm.faces); bm.to_mesh(me); bm.free()
    o = bpy.data.objects.new(name, me); S.sc.collection.objects.link(o); me.materials.append(mat)
    return o


def wedge(S, name, mat, a0, a1, r0, r1, z0, z1, parent, n=6):
    ang = [a0 + (a1 - a0) * i / n for i in range(n + 1)]
    vs = [(r * math.cos(R(a)), r * math.sin(R(a)), z) for z in (z1, z0) for r in (r0, r1) for a in ang]
    ix = lambda ly, rg, i: ly * 2 * (n + 1) + rg * (n + 1) + i
    fs = []
    for i in range(n):
        fs.append((ix(0, 0, i), ix(0, 1, i), ix(0, 1, i + 1), ix(0, 0, i + 1)))
        fs.append((ix(1, 0, i + 1), ix(1, 1, i + 1), ix(1, 1, i), ix(1, 0, i)))
        fs.append((ix(0, 1, i), ix(1, 1, i), ix(1, 1, i + 1), ix(0, 1, i + 1)))
        fs.append((ix(0, 0, i + 1), ix(1, 0, i + 1), ix(1, 0, i), ix(0, 0, i)))
    fs.append((ix(0, 0, 0), ix(1, 0, 0), ix(1, 1, 0), ix(0, 1, 0)))
    fs.append((ix(0, 1, n), ix(1, 1, n), ix(1, 0, n), ix(0, 0, n)))
    me = bpy.data.meshes.new(name); me.from_pydata(vs, [], fs); me.update()
    bm = bmesh.new(); bm.from_mesh(me); bmesh.ops.recalc_face_normals(bm, faces=bm.faces); bm.to_mesh(me); bm.free()
    o = bpy.data.objects.new(name, me); S.sc.collection.objects.link(o); me.materials.append(mat); o.parent = parent
    return o


RAINBOW = [(0.95, 0.06, 0.07), (1.0, 0.42, 0.02), (1.0, 0.82, 0.0), (0.15, 0.75, 0.15), (0.0, 0.72, 0.85), (0.08, 0.28, 0.95),
           (0.48, 0.12, 0.85), (0.95, 0.18, 0.62)]


class W: pass


def build_set(S, ph, bench=None, n_frames=200):
    """Zona de juegos + tiovivo. ph = ángulo (grados, en el disco) de la barra 0. bench = ángulo local del banco (o None)."""
    w = W(); clear_env(S)
    mat = mmat(S, "goma", (0.40, 0.22, 0.15), rough=0.95)
    ring(S, "suelo_goma", mat, R_IN - 0.02, 3.3, -0.01, 0.003, 96)             # suelo de goma con un hueco central (para la placa-pedal)
    ring(S, "foso", mmat(S, "foso", (0.015, 0.015, 0.018), rough=0.9), R_DISC - 0.02, R_DISC + 0.14, -0.01, 0.0045, 96)
    O(S, "cylinder", "fondo_hueco", mmat(S, "foso", (0.015, 0.015, 0.018), rough=0.9), (0, 0, -0.07), (R_IN, R_IN, 0.005), vertices=64, smooth=False)
    # disco: 8 cuñas de colores sobre un empty que gira
    w.disc = S.empty("disco", (0, 0, 0))
    for i, c in enumerate(RAINBOW):
        wedge(S, f"cuna{i}", mmat(S, f"cuna{i}", c, rough=0.35, spec=0.5), i * 45.0, (i + 1) * 45.0, R_IN + 0.02, R_DISC, -0.04, TOP, w.disc)
    # centro FIJO: placa-pedal amarilla y negra, 8 pilotos (rojos / verdes), taburete amarillo
    w.centro = S.empty("centro_fijo", (0, 0, 0))
    black = mmat(S, "placa_negra", (0.02, 0.02, 0.025), rough=0.6); yel = mmat(S, "placa_amarilla", (1.0, 0.72, 0.0), rough=0.5)
    O(S, "cylinder", "placa_n", black, (0, 0, -0.01), (R_IN - 0.03, R_IN - 0.03, 0.0075), parent=w.centro, vertices=64, smooth=False)
    O(S, "cylinder", "placa_a", yel, (0, 0, -0.0095), (R_IN - 0.15, R_IN - 0.15, 0.0149 - 0.0), parent=w.centro, vertices=64, smooth=False)
    O(S, "cylinder", "taburete", mmat(S, "taburete", (1.0, 0.55, 0.0), rough=0.4), (0, 0, SEAT_Z / 2), (0.24, 0.24, SEAT_Z / 2), parent=w.centro, vertices=32)
    O(S, "cylinder", "taburete_tapa", mmat(S, "taburete_tapa", (1.0, 0.82, 0.1), rough=0.35), (0, 0, SEAT_Z + 0.008), (0.27, 0.27, 0.01), parent=w.centro, vertices=32)
    red = mmat(S, "piloto_rojo", (0.9, 0.02, 0.02), emit=(1.0, 0.03, 0.02, 3.0)); grn = mmat(S, "piloto_verde", (0.05, 0.9, 0.1), emit=(0.1, 1.0, 0.15, 4.0))
    w.red, w.grn = [], []
    for i in range(8):
        p = polar(R_IN - 0.09, i * 45.0 + 22.5, 0.012)
        w.red.append(O(S, "uv_sphere", f"piloto_r{i}", red, p, (0.065, 0.065, 0.04), parent=w.centro, segments=12, ring_count=8))
        g_ = O(S, "uv_sphere", f"piloto_v{i}", grn, p, (0.075, 0.075, 0.045), parent=w.centro, segments=12, ring_count=8)
        g_.scale = (0, 0, 0); w.grn.append(g_)
    # barras (4): base articulada en el borde, tubo rojo, pomo blanco
    rodm = mmat(S, "barra_roja", (0.95, 0.03, 0.03), rough=0.3, spec=0.6); wh = mmat(S, "pomo_blanco", (0.97, 0.97, 0.95), rough=0.3)
    w.hinges = []
    w.pivots = []
    for k in range(4):
        pv = S.empty(f"barra_pivote{k}", (0, 0, 0), w.disc); pv.rotation_euler = (0, 0, R(ph + 90.0 * k)); w.pivots.append(pv)
        hg = S.empty(f"barra_bisagra{k}", (POST_R, 0, POST_Z0), pv)
        L = POST_Z1 - POST_Z0
        O(S, "cylinder", f"barra{k}", rodm, (0, 0, L / 2), (0.045, 0.045, L / 2), parent=hg, vertices=16)
        O(S, "uv_sphere", f"pomo{k}", wh, (0, 0, L + 0.03), (0.085, 0.085, 0.085), parent=hg, segments=14, ring_count=10)
        O(S, "cylinder", f"asa{k}", rodm, (ARM_L / 2, 0, L - 0.03), (0.04, 0.04, ARM_L / 2), (0, R(90), 0), hg, vertices=16)      # asa horizontal hacia fuera: de ella se cuelga
        O(S, "uv_sphere", f"asa_pomo{k}", wh, (ARM_L, 0, L - 0.03), (0.07, 0.07, 0.07), parent=hg, segments=12, ring_count=8)
        O(S, "cylinder", f"agarre{k}", wh, (0, 0, L * 0.55), (0.052, 0.052, 0.09), parent=hg, vertices=16)
        box(S, f"base_barra{k}", mmat(S, "base_barra", (0.25, 0.25, 0.28), rough=0.4, metal=0.6), (0.14, 0.14, 0.12), (POST_R, 0, 0.07), pv)
        w.hinges.append(hg)
    w.ph = ph
    # banco (solo si el nivel lo pide)
    if bench is not None:
        bp = S.empty("banco_pivote", (0, 0, 0), w.disc); bp.rotation_euler = (0, 0, R(bench)); w.bench = bp
        box(S, "banco", mmat(S, "banco", (0.1, 0.35, 0.95), rough=0.45), (0.42, 0.56, SEAT_Z - TOP), (1.05, 0, TOP + (SEAT_Z - TOP) / 2), bp)
    # pescante fijo detrás del disco con el banderín y la pelota en el eje del centro
    metal = mmat(S, "pescante", (0.30, 0.31, 0.34), rough=0.35, metal=0.7)
    O(S, "cylinder", "pescante_poste", metal, (0, 3.7, GALLOWS_Z / 2), (0.08, 0.08, GALLOWS_Z / 2), vertices=20)
    O(S, "cylinder", "pescante_brazo", metal, (0, 3.7 / 2, GALLOWS_Z), (0.05, 0.05, 3.7 / 2), (R(90), 0, 0), vertices=16)
    w.spin = S.empty("husillo", (0, 0, GALLOWS_Z))
    O(S, "cylinder", "husillo_vastago", metal, (0, 0, -0.5), (0.025, 0.025, 0.5), parent=w.spin, vertices=12)
    O(S, "cylinder", "banderin_asta", metal, (0.5, 0, -0.14), (0.02, 0.02, 0.5), (0, R(90), 0), w.spin, vertices=12)
    w.flag = S.empty("banderin_bisagra", (0.05, 0, -0.14), w.spin)
    box(S, "banderin_rojo", mmat(S, "banderin_rojo", (1.0, 0.04, 0.04), rough=0.55), (1.05, 0.015, 0.34), (0.55, 0, -0.19), w.flag)
    box(S, "banderin_franja", mmat(S, "banderin_blanca", (1.0, 1.0, 1.0), rough=0.55), (1.05, 0.018, 0.10), (0.55, 0, -0.19), w.flag)
    O(S, "cylinder", "pelota_asta", metal, (-0.34, 0, -0.80), (0.02, 0.02, 0.34), (0, R(90), 0), w.spin, vertices=12)
    O(S, "uv_sphere", "pelota", mmat(S, "pelota_amarilla", (1.0, 0.88, 0.0), rough=0.3, spec=0.6), (-0.70, 0, -0.80), (0.32, 0.32, 0.32), parent=w.spin,
      segments=24, ring_count=16)
    O(S, "cylinder", "pelota_cinturon", mmat(S, "pelota_negra", (0.02, 0.02, 0.03), rough=0.4), (-0.70, 0, -0.80), (0.327, 0.327, 0.05), parent=w.spin, vertices=32)
    O(S, "cylinder", "pelota_cinturon2", mmat(S, "pelota_negra", (0.02, 0.02, 0.03), rough=0.4), (-0.70, 0, -0.80), (0.327, 0.05, 0.327), (R(90), 0, 0), w.spin, vertices=32)
    # movimiento continuo: disco (por fotograma), husillo lento, banderín que se agita
    for f in range(1, n_frames + 1): S.key(w.disc, f, rot=(0, 0, A(f)), interp="LINEAR")
    S.key(w.spin, 1, rot=(0, 0, 0.0), interp="LINEAR"); S.key(w.spin, n_frames, rot=(0, 0, 0.014 * (n_frames - 1)), interp="LINEAR")
    # motion blur: el arcoíris del final se funde de verdad
    S.sc.render.use_motion_blur = True; S.sc.render.motion_blur_shutter = 0.4
    return w


def flutter(S, w, n, f_gust=None, amp=7.0, gust=28.0):
    for f in range(1, n + 1):
        g = 0.0 if f_gust is None else sstep((f - f_gust) / 20.0)
        S.key(w.flag, f, rot=(R((amp + gust * g) * math.sin(0.55 * f) + 4 * g), 0, 0), interp="LINEAR")


def tilt_posts(S, w, f0, f1, deg=62.0):
    """Las barras se abaten hacia fuera como una hélice entre f0 y f1 (y se recogen a partir de f2 si se pide)."""
    for hg in w.hinges:
        S.key(hg, f0, rot=(0, 0, 0), interp="BEZIER"); S.key(hg, f1, rot=(0, R(deg), 0), interp="BEZIER")


# ------------------------------------------------------------------ colocación del humano (emparentado al disco)
PREV = {}


def key_root(S, a, f, M):
    """M = matriz del MUNDO deseada para la raíz; se convierte al marco local del disco (emparentado) y se keya lineal."""
    Lm = Rz(D(A(f))).inverted() @ M
    e = Lm.to_euler("XYZ", PREV.get(id(a), Euler((0, 0, 0))))
    PREV[id(a)] = e
    S.key(a.root, f, loc=tuple(Lm.to_translation()), rot=(e.x, e.y, e.z), interp="LINEAR")


def Mw(pos, yaw=0.0, pitch=0.0, roll=0.0): return Tm(pos) @ Rz(yaw) @ Rx(pitch) @ Ry(roll)


def blend_m(M0, M1, t):
    t = sstep(t); q0, q1 = M0.to_quaternion(), M1.to_quaternion(); q = q0.slerp(q1, t)
    return Tm(M0.to_translation().lerp(M1.to_translation(), t)) @ q.to_matrix().to_4x4()


def pin_feet(S, a, f0, f1, floor, off=0.02):
    """Pie más bajo (tobillo y punta) a floor(f)+off en cada fotograma: pisa el suelo o el disco sin hundirse ni flotar."""
    for f in range(f0, f1 + 1):
        S.sc.frame_set(f); bpy.context.view_layer.update()
        zs = [(a.arm.matrix_world @ a.arm.pose.bones[a.pfx + b].tail).z for b in ("LeftToeBase", "RightToeBase", "LeftFoot", "RightFoot")]
        d = floor(f) + off - min(zs)
        loc = a.root.location.copy(); rot = a.root.rotation_euler.copy()
        S.key(a.root, f, loc=(loc.x, loc.y, loc.z + d), rot=(rot.x, rot.y, rot.z), interp="LINEAR")


def new_actor(S, w, uses, x=0.0):
    a = MixamoActor(S, x=x, yaw=0, use=uses); klunk(a)
    a.root.parent = w.disc
    PREV.pop(id(a), None)
    return a


def bone_w(a, bone, frac=0.0):
    pb = a.arm.pose.bones[a.pfx + bone]
    return a.arm.matrix_world @ (pb.head + (pb.tail - pb.head) * frac)


def hand_local(S, a, f):
    """Punto de agarre (media de las dos palmas) en el marco de la raíz; no depende de dónde esté la raíz."""
    S.sc.frame_set(f); bpy.context.view_layer.update()
    p = (bone_w(a, "LeftHand", 0.6) + bone_w(a, "RightHand", 0.6)) * 0.5
    return a.root.matrix_world.inverted() @ p


# ------------------------------------------------------------------ auditorías
FINGERS = ("Thumb", "Index", "Middle", "Ring", "Pinky")


def solids_hit(p, r, f, tilted=False, bench=None, ball=True):
    """Nombres de los sólidos que contiene el punto p (mundo) con holgura r. Gira con el disco: se pasa al marco del disco."""
    out = []
    al = D(A(f)); q = Rz(-al) @ p
    if not tilted:
        for k in range(4):
            u = Rz(-(CUR.ph + 90.0 * k)) @ q
            if POST_R - 0.045 - r < u.x < POST_R + 0.045 + r and abs(u.y) < 0.045 + r and POST_Z0 - r < u.z < POST_Z1 + 0.1 + r: out.append(f"barra{k}")
        if POST_R - 0.02 < u.x < POST_R + ARM_L + 0.06 + r and abs(u.y) < 0.045 + r and POST_Z1 - 0.03 - 0.05 - r < u.z < POST_Z1 - 0.03 + 0.05 + r: out.append(f"asa{k}")
    if bench is not None:
        u = Rz(-bench) @ q
        if 1.05 - 0.21 - r < u.x < 1.05 + 0.21 + r and abs(u.y) < 0.28 + r and TOP - r < u.z < SEAT_Z + r: out.append("banco")
    if math.hypot(p.x, p.y) < 0.24 + r and p.z < SEAT_Z + 0.02 + r: out.append("taburete")
    if math.hypot(p.x, p.y - 3.7) < 0.08 + r and p.z < GALLOWS_Z + r: out.append("pescante")
    if ball:
        s = 0.014 * (f - 1); c = Vector((-0.70 * math.cos(s), -0.70 * math.sin(s), GALLOWS_Z - 0.80))
        if (p - c).length < 0.32 + r: out.append("pelota")
    return out


def audit(S, a, tag, f0, f1, step=1, tilted=lambda f: False, bench=None, ignore=(), contact=None):
    """Cuerpo (huesos con grosor) contra barras, banco, taburete, pescante y pelota. contact = {(hueso o '*', sólido): (f0, f1)} roces
    permitidos (la mano que agarra, el golpe del gag): se cuentan aparte."""
    if os.environ.get("EP016_NOAUDIT"): return {}
    bad, ok = {}, {}
    for f in range(f0, f1 + 1, step):
        S.sc.frame_set(f); bpy.context.view_layer.update()
        for pb in a.arm.pose.bones:
            n = pb.name.split(":")[-1]
            if any(k in n for k in FINGERS) or n in ignore: continue
            r = 0.12 if n in ("Head", "Spine", "Spine1", "Spine2", "Hips", "Neck") else 0.045
            if "Foot" in n or "Toe" in n: r = 0.02
            for fr in (0.0, 0.5, 1.0):
                p = a.arm.matrix_world @ (pb.head + (pb.tail - pb.head) * fr)
                for sn in solids_hit(p, r, f, tilted(f), bench):
                    cf = (contact or {}).get((n, sn)) or (contact or {}).get(("*", sn))
                    tgt = ok if cf and cf[0] <= f <= cf[1] else bad
                    tgt.setdefault((n, sn), []).append(f)
                    if os.environ.get("EP016_DEBUG") and tgt is bad:
                        rt = a.root.matrix_world.translation; fo = bone_w(a, "RightFoot"); tb = bone_w(a, "RightToeBase"); te = bone_w(a, "RightToe_End")
                        print(f"DEBUG {tag} f{f} {n} fr{fr} en {sn}: p=({p.x:.2f},{p.y:.2f},{p.z:.2f}) r={r} raiz=({rt.x:.2f},{rt.y:.2f},{rt.z:.2f}) pie=({fo.x:.2f},{fo.y:.2f},{fo.z:.2f}) puntaBase=({tb.x:.2f},{tb.y:.2f},{tb.z:.2f}) puntaFin=({te.x:.2f},{te.y:.2f},{te.z:.2f}) loc=({a.root.location.x:.2f},{a.root.location.y:.2f}) par={a.root.parent.name if a.root.parent else None}")
    msg = "limpia (nada atraviesa nada)" if not bad else "; ".join(f"{k[0]} dentro de {k[1]}: f{v[0]}-{v[-1]} ({len(v)})" for k, v in bad.items())
    if ok: msg += " | roces permitidos: " + ", ".join(f"{k[0]}/{k[1]}" for k in ok)
    print(f"AUDITORIA {tag}: {msg}")
    return bad


def audit_feet(S, a, tag, f0, f1, floor, step=1):
    """Pie más bajo (tobillo y punta) respecto a la superficie floor(f): debe quedar a ~0,02 (z≈0 ±3 cm) y nunca bajo -0,03."""
    if os.environ.get("EP016_NOAUDIT"): return
    lo, hi, zmin = 9.0, -9.0, 9.0
    for f in range(f0, f1 + 1, step):
        S.sc.frame_set(f); bpy.context.view_layer.update()
        zs = min((a.arm.matrix_world @ a.arm.pose.bones[a.pfx + b].tail).z for b in ("LeftToeBase", "RightToeBase", "LeftFoot", "RightFoot"))
        lo = min(lo, zs - floor(f)); hi = max(hi, zs - floor(f)); zmin = min(zmin, zs)
    print(f"AUDITORIA pies {tag}: sobre la superficie entre {lo:+.3f} y {hi:+.3f} m (objetivo +0.02); z mundo mínima {zmin:+.3f} (límite -0.03)")


def audit_min(S, a, tag, f0, f1, step=2):
    """Altura mínima de cualquier hueso (cuerpo tumbado): no puede hundirse bajo el suelo."""
    if os.environ.get("EP016_NOAUDIT"): return
    lo = 9.0
    for f in range(f0, f1 + 1, step):
        S.sc.frame_set(f); bpy.context.view_layer.update()
        for pb in a.arm.pose.bones:
            n = pb.name.split(":")[-1]
            if any(k in n for k in FINGERS): continue
            for fr in (0.0, 1.0): lo = min(lo, (a.arm.matrix_world @ (pb.head + (pb.tail - pb.head) * fr)).z)
    print(f"AUDITORIA hueso más bajo {tag}: z {lo:+.3f} m")


def collect_pts(S, a, f0, f1):
    """Puntos de los huesos (mundo, con su grosor) por fotograma: se evalúan una vez y sirven para probar muchas fases de las barras."""
    pts = {}
    for f in range(f0, f1 + 1):
        S.sc.frame_set(f); bpy.context.view_layer.update(); L = []
        for pb in a.arm.pose.bones:
            n = pb.name.split(":")[-1]
            if any(k in n for k in FINGERS): continue
            r = 0.12 if n in ("Head", "Spine", "Spine1", "Spine2", "Hips", "Neck") else 0.045
            if "Foot" in n or "Toe" in n: r = 0.02
            for fr in (0.0, 0.5, 1.0): L.append((n, r, a.arm.matrix_world @ (pb.head + (pb.tail - pb.head) * fr)))
        pts[f] = L
    return pts


def tune_phase(w, pts, cands, margin=0.05):
    """Elige la fase de las barras (grados) con menos cruces con el cuerpo (y con holgura extra); recoloca los pivotes de las barras."""
    best = None
    for ph in cands:
        CUR.ph = ph
        bad = sum(1 for f, L in pts.items() for (n, r, p) in L if any(x.startswith(("barra", "asa")) for x in solids_hit(p, r, f)))
        bad2 = sum(1 for f, L in pts.items() for (n, r, p) in L if any(x.startswith(("barra", "asa")) for x in solids_hit(p, r + margin, f)))
        key = (bad, bad2)
        if best is None or key < best[0]: best = (key, ph)
    CUR.ph = best[1]
    for k, pv in enumerate(w.pivots): pv.rotation_euler = (0, 0, R(CUR.ph + 90.0 * k))
    print(f"FASE barras elegida {CUR.ph:.0f} grados (cruces {best[0][0]}, con holgura {best[0][1]})")
    return best[1]


def audit_parent(S, a, tag, f0, f1, check, f_from=0):
    """La raíz emparentada al disco debe acabar donde el nivel la quiere en el MUNDO: check(f) -> Vector mundo; imprime el error máximo."""
    if os.environ.get("EP016_NOAUDIT"): return
    worst = 0.0
    for f in range(f0, f1 + 1, 2):
        if f > f_from - 8 and f < f_from: continue
        S.sc.frame_set(f); bpy.context.view_layer.update()
        d = a.root.matrix_world.translation - check(f); d.z = 0.0
        worst = max(worst, d.length)
    print(f"AUDITORIA emparentado {tag}: error máximo (en planta) raíz mundo vs ruta prevista {worst:.4f} m (disco girado {D(A(f1)):.0f} grados)")


# ------------------------------------------------------------------ nivel -380
def l1(S):
    """-380: ya corriendo en círculo junto al disco (fotograma 1); intenta subir por el borde y la barra que llega por detrás lo lanza
    girando como una peonza (whoosh); acaba de pie y enfadado, mirando a cámara."""
    N = 112; f_h = 26; th_h = -100.0; wr = 1.9 / 24.0
    th0 = th_h - D(wr * (f_h - 1)); make_alpha(N + 24, lambda f: OM0)
    CUR.ph = th_h - D(A(f_h))
    w = build_set(S, CUR.ph, None, N + 12); cam_fixed(S); flutter(S, w, N + 12)
    a = new_actor(S, w, ["Running", "Angry"])
    r_h = 1.60
    pos_h = polar(r_h, th_h); t_hat = Vector((-math.sin(R(th_h)), math.cos(R(th_h)), 0)); n_hat = Vector((math.cos(R(th_h)), math.sin(R(th_h)), 0))
    dirv = (0.5 * t_hat + 0.85 * n_hat).normalized(); v0, tau, Ts = 0.09, 8.0, 24.0
    yaw_h = th_h + 180.0
    def path(f):
        if f <= f_h:
            u = (f - 1) / float(f_h - 1); th = th0 + D(wr * (f - 1)); r = 1.90 - (1.90 - r_h) * sstep((f - (f_h - 9)) / 9.0)
            return polar(r, th), th + 180.0
        t = f - f_h
        return pos_h + dirv * (v0 * tau * (1 - math.exp(-t / tau))), yaw_h + (1440.0 - yaw_h) * sstep(t / Ts) * 1.0 if t < Ts else 1440.0
    seg(S, a, "Running", 1, f_h + 20, speed=0.95, blend=0)
    seg(S, a, "Angry", f_h + 20, None, blend=6)
    for f in range(1, N + 12):
        p, yaw = path(f); key_root(S, a, f, Mw(p, yaw))
    f_end = N + 11
    pin_feet(S, a, 1, f_end, lambda f: 0.0)
    for f in (1, 25, 49, 73): S.cue("whoosh", f, vol=-17)
    S.cue("huh", f_h - 8, vol=-7); S.cue("hit", f_h, vol=-3); S.cue("whoosh", f_h + 2, vol=-4); S.cue("oof", f_h + 3, vol=-6)
    S.cue("hmm", f_h + 36, vol=-5); S.cue("wahwah", f_h + 46, vol=-8)
    S.f = N
    a.verify(S.f)
    faces(a, [(1, "enfado", 0.5), (f_h - 8, "sorpresa", 1.0), (f_h + 12, "sorpresa", 0.6), (f_h + 26, "enfado", 1.0)], N, first_blink=12, every=40)
    contact = {("*", "barra0"): (f_h - 7, f_h + 4)}
    audit(S, a, "nivel -380", 1, N, contact=contact); audit_feet(S, a, "nivel -380", 1, N, lambda f: 0.0)
    audit_parent(S, a, "nivel -380", 1, N, lambda f: path(f)[0])
    cam_follow(S, a, N + 10, [(1, Vector((0, -6.4, 3.5)))], [(1, 50.0), (f_h + 18, 50.0), (f_h + 34, 85.0)])
    return a


# ------------------------------------------------------------------ nivel -70
def l2(S):
    """-70: corre pegado a una barra, se cuelga de su asa y sale volando horizontal como una bandera (Climbing A Rope); se suelta y
    cae rodando sobre el suelo (Falling Back Death)."""
    N = 124; f_g = 24; ang_g, ang_r = -80.0, 95.0; r_run = 1.92
    f_r = f_g + int(round((ang_r - ang_g) / D(OM0)))
    make_alpha(N + 24, lambda f: OM0)
    th0 = ang_g - D(A(f_g))                                                # agarra la asa a la derecha y la suelta atrás, a la izquierda
    CUR.ph = th0                                                           # la barra 0 está siempre a su lado
    w = build_set(S, CUR.ph, None, N + 12); cam_fixed(S); flutter(S, w, N + 12)
    a = new_actor(S, w, ["Running", "Climbing A Rope", "Falling Back Death"])
    grip_z = POST_Z1 - 0.03
    seg(S, a, "Running", 1, f_g + 2, speed=1.15, blend=0)
    seg(S, a, "Climbing A Rope", f_g - 2, f_r + 2, speed=1.0, blend=5)
    seg(S, a, "Falling Back Death", f_r, None, start=18, speed=1.0, blend=5)
    pin_run = lambda: pin_feet(S, a, 1, f_g - 5, lambda f: 0.0)
    def run_m(f): th = th0 + D(A(f)); return Mw(polar(r_run, th), th + 180.0)
    def swing(f):
        t = f - f_g; k = eout(t / 8.0)
        th_ = 28.0 + 37.0 * k + 3.0 * math.sin(0.9 * t) * k; ph_ = 8.0 + 82.0 * k
        return th_, ph_
    h_cache = {}
    def hang_m(f):
        th_, ph_ = swing(f)
        if f not in h_cache: h_cache[f] = hand_local(S, a, f)
        al = th0 + D(A(f))
        G = polar(POST_R + ARM_L, al, grip_z)
        Rm = Rz(al) @ Rz(-ph_) @ Ry(-th_) @ Rz(-90.0)                      # de cara a la barra: la cabeza queda hacia fuera, lejos del poste
        return Tm(G) @ Rm @ Tm(-h_cache[f])
    Ms = {}
    for f in range(1, f_r + 1):
        if f < f_g - 2: Ms[f] = run_m(f)
        elif f <= f_g + 3: Ms[f] = blend_m(run_m(f), hang_m(f), (f - (f_g - 2)) / 5.0)
        else: Ms[f] = hang_m(f)
    Mr = Ms[f_r]; Mp = Ms[f_r - 1]
    G_r = Mr @ h_cache[f_r]; G_p = Mp @ h_cache[f_r - 1]
    vel = (G_r - G_p); vel.z = 0.0; vel *= 0.5
    down = (Mr.to_3x3() @ Vector((0, 0, -1))); down.z = 0.0
    yaw_l = 10.0                                                           # tumbado a lo largo de y: lejos de las barras y dentro de cuadro
    z0 = grip_z - 0.12; g = 9.8 / 576.0
    t_fall = math.sqrt(2 * z0 / g); f_L = int(f_r + t_fall + 1)
    pos0 = G_r.copy(); pos0.z = 0
    def fly(f):
        t = f - f_r
        if f <= f_L: return pos0 + vel * (t * 0.93), max(0.0, z0 - 0.5 * g * t * t)
        tl = f - f_L; vL = vel * 0.8
        return pos0 + vel * (f_L - f_r) * 0.93 + vL * (9.0 * (1 - math.exp(-tl / 9.0))), 0.0
    f_roll = 26; f_bl = 6
    for f in range(1, f_r + 1): key_root(S, a, f, Ms[f])
    pin_run()
    for f in range(f_r + 1, N + 12):
        p, zz = fly(f); p = Vector((p.x, p.y, zz))
        spin = 0.0 if f <= f_L else 360.0 * eout((f - f_L) / float(f_roll))
        Ml = Mw(p, yaw_l + spin)
        if f < f_r + f_bl:                                                  # el cuerpo sigue girando como en el agarre y se tumba
            t = f - f_r
            Mh = Tm(Vector((vel.x * t * 0.93, vel.y * t * 0.93, -0.5 * g * t * t))) @ Mr
            Ml = blend_m(Mh, Ml, t / float(f_bl))
        key_root(S, a, f, Ml)
    f_end = N + 11
    S.cue("whoosh", 1, vol=-10); S.cue("huh", f_g - 4, vol=-7); S.cue("creak", f_g + 1, vol=-8); S.cue("whoosh", f_g + 6, vol=-5)
    S.cue("pop", f_r, vol=-8); S.cue("hit", f_L, vol=-2); S.cue("oof", f_L + 1, vol=-5); S.cue("whoosh", f_L + 3, vol=-12)
    S.cue("wahwah", f_L + 36, vol=-8)
    S.f = N
    a.verify(S.f)
    faces(a, [(1, "enfado", 0.4), (f_g - 6, "sorpresa", 0.7), (f_r - 6, "sorpresa", 1.0), (f_L + 2, "enfado", 0.7), (f_L + 30, "neutra", 1.0)], N, first_blink=10, every=34)
    hands = ("LeftHand", "RightHand", "LeftForeArm", "RightForeArm")
    audit(S, a, "nivel -70 (carrera y agarre)", 1, f_g + 3, ignore=hands, contact={("*", "asa0"): (f_g - 3, f_g + 3), ("*", "barra0"): (f_g - 3, f_g + 3)})
    audit(S, a, "nivel -70 (bandera, manos en la asa)", f_g + 4, f_r, ignore=hands + ("LeftArm", "RightArm", "LeftShoulder", "RightShoulder"))
    audit(S, a, "nivel -70 (caída)", f_r + 2, N)
    audit_feet(S, a, "nivel -70 (carrera)", 1, f_g - 5, lambda f: 0.0)
    audit_min(S, a, "nivel -70 (caída y reposo)", f_L, N)
    audit_parent(S, a, "nivel -70", 1, N, lambda f: (Ms[f] if f <= f_r else Mw(Vector((fly(f)[0].x, fly(f)[0].y, fly(f)[1])), 0)).to_translation(), f_from=f_r + f_bl + 1)
    cam_follow(S, a, N + 10, [(1, Vector((-2.5, -7.5, 4.2)))], [(1, 50.0), (f_L, 50.0), (f_L + 14, 75.0)])
    return a


# ------------------------------------------------------------------ nivel 200
def l3(S):
    """200: salta al disco (Jumping), resbala hacia el borde y se queda pegado y plano a una barra (Climbing Up Wall), temblando;
    el banderín del centro sigue casi quieto."""
    N = 124; f_c = 8; sp = 1.2
    f_t = f_c + int(round((25 - 19) / sp)); f_L = f_c + int(round((46 - 19) / sp))      # despegue y aterrizaje
    f_w = f_L + 8
    make_alpha(N + 24, lambda f: OM0)
    r_l, r_w = 0.98, POST_R - 0.38
    S0 = Vector((-1.75, -0.95, 0.0)); yaw0 = 90.0
    best = None                                                                            # aterrizaje: el ángulo que deja el salto lejos de las otras barras
    for aL in range(-176, -100, 2):
        TL = polar(r_l, aL + 30.0); phc = aL - D(A(f_L)); md = 999.0
        for f in range(1, f_L):
            p_ = S0 if f <= f_t - 1 else S0.lerp(TL, sstep((f - (f_t - 1)) / float(f_L - f_t + 1)))
            if 1.0 < math.hypot(p_.x, p_.y) < 1.95:
                an = D(math.atan2(p_.y, p_.x))
                for k in range(4): md = min(md, abs(((an - (phc + D(A(f)) + 90.0 * k) + 180.0) % 360.0) - 180.0))
        if best is None or md > best[0] + 1.0 or (abs(md - best[0]) <= 1.0 and abs(aL + 160) < abs(best[1] + 160)): best = (md, aL)
    ang_L = float(best[1]); print(f"L3 aterrizaje elegido: barra 0 en {ang_L:.0f} grados al caer; separación mínima de las demás barras durante el salto {best[0]:.0f} grados")
    CUR.ph = ang_L - D(A(f_L))
    w = build_set(S, CUR.ph, None, N + 12); cam_fixed(S); flutter(S, w, N + 12, amp=2.5)
    a = new_actor(S, w, ["Looking Around", "Jumping", "Climbing Up Wall"])
    seg(S, a, "Looking Around", 1, f_c + 2, speed=1.0, blend=0)
    seg(S, a, "Jumping", f_c, f_L + 8, start=19, speed=sp, blend=5)
    seg(S, a, "Climbing Up Wall", f_w - 2, None, start=0, speed=0.05, blend=6)
    def loc_target(f): return polar(r_l, CUR.ph + 30.0 + D(A(f)), 0.0)
    T_L = loc_target(f_L)
    def arc(f):
        if f <= f_t: return 0.0
        if f >= f_L: return 0.0
        u = (f - f_t) / float(f_L - f_t); return 0.78 * 4 * u * (1 - u)
    def path(f):
        if f <= f_t - 1: return S0.copy(), yaw0
        if f < f_L:
            u = sstep((f - (f_t - 1)) / float(f_L - f_t + 1)); p = S0.lerp(loc_target(f_L), u)
            return p, yaw0 + (D(math.atan2(T_L.x - S0.x, -(T_L.y - S0.y))) - yaw0) * 0.0
        t = f - f_L; u = min(1.0, t / 8.0)
        rr = r_l + (r_w - r_l) * u * u; al = CUR.ph + D(A(f))                # derrapa hacia fuera y hacia atrás (30 grados) hasta la barra
        p = polar(rr, al + 30.0 * (1 - sstep(u)), 0.0)
        return p, al + 90.0 + 25.0 * (1 - sstep(u))                        # mira hacia fuera (a la barra)
    tre = {}
    for f in range(1, N + 12):
        p, yaw = path(f)
        if f >= f_w:                                                       # temblor del cuerpo pegado a la barra
            tt = f - f_w; yaw += 2.5 * math.sin(tt * 2.1) * (1 - 0.3 * min(1, tt / 30.0)); p = p + Vector((0.012 * math.sin(tt * 2.9), 0.012 * math.cos(tt * 2.3), 0))
        key_root(S, a, f, Mw(p, yaw, pitch=1.2 * math.sin(f * 2.4) if f >= f_w else 0.0))
    f_end = N + 11
    pin_feet(S, a, 1, f_end, lambda f: arc(f) + (TOP if f >= f_L - 1 else 0.0))
    S.cue("whoosh", 1, vol=-14); S.cue("huh", f_c - 2, vol=-8); S.cue("boing", f_t, vol=-9); S.cue("hit", f_L, vol=-6); S.cue("whoosh", f_L + 2, vol=-9)
    S.cue("clunk", f_w, vol=-6); S.cue("creak", f_w + 8, vol=-7); S.cue("huh", f_w + 20, vol=-9); S.cue("hmm", f_w + 44, vol=-7)
    S.cue("wahwah", f_w + 62, vol=-9)
    S.f = N
    a.verify(S.f)
    faces(a, [(1, "neutra", 1.0), (f_c - 2, "enfado", 0.6), (f_t, "sorpresa", 0.6), (f_L + 2, "sorpresa", 1.0), (f_w + 6, "sorpresa", 0.8), (f_w + 50, "enfado", 0.5)],
          N, first_blink=10, every=30)
    fl = lambda f: arc(f) + (TOP if f >= f_L - 1 else 0.0)
    audit(S, a, "nivel 200", 1, N, ignore=("LeftHand", "RightHand", "LeftForeArm", "RightForeArm", "LeftToeBase", "RightToeBase", "LeftFoot", "RightFoot"),
          contact={("*", "barra0"): (f_w - 4, N)})
    audit_feet(S, a, "nivel 200 (suelo y disco, sin el aire)", 1, f_c, lambda f: 0.0)
    audit_feet(S, a, "nivel 200 (sobre el disco)", f_L + 2, N, lambda f: TOP)
    audit_parent(S, a, "nivel 200", f_L + 2, N, lambda f: Vector((path(f)[0].x + 0.0, path(f)[0].y, 0)))
    cam_follow(S, a, N + 10, [(1, Vector((3.2, -6.0, 3.4)))], [(1, 50.0), (N - 40, 50.0), (N - 20, 80.0)])
    return a


# ------------------------------------------------------------------ nivel 950
def l4(S):
    """950: corre a la misma velocidad que el borde del disco (Running), salta con aterrizaje perfecto (Jumping) y se sienta en un banco
    del disco (Sitting Idle) riendo: ding y risa."""
    N = 120; sp = 1.3; f_c = 18
    f_t = f_c + int(round((25 - 19) / sp)); f_L = f_c + int(round((45 - 19) / sp)); f_s = f_L + 3
    make_alpha(N + 24, lambda f: OM0)
    bb = -55.0 + 0.0                                                        # banco: ángulo local al final del salto (se ajusta con la fase)
    CUR.ph = -125.0 - D(A(f_L))
    bench_ang = CUR.ph + 22.0
    w = build_set(S, CUR.ph, bench_ang, N + 12); cam_fixed(S); flutter(S, w, N + 12, amp=7.0)
    a = new_actor(S, w, ["Running", "Jumping", "Sitting Idle"])
    d_loc = Vector((-math.sin(R(bench_ang)), math.cos(R(bench_ang)), 0.0))        # tangente antihoraria: hacia donde mira sentado
    B = polar(1.05, bench_ang); F = B + d_loc * 0.68
    gam = bench_ang + D(math.atan2(0.68, 1.05))                                    # ángulo local del punto de aterrizaje F
    yaw_loc = bench_ang + 180.0
    r_run = 1.74
    def loc_to_w(v, f): return Rz(D(A(f))) @ v
    def path(f):
        if f < f_t:
            return loc_to_w(polar(r_run, gam - 14.0), f), gam - 14.0 + D(A(f)) + 180.0
        if f < f_L:
            u = (f - f_t) / float(f_L - f_t); lv = polar(r_run, gam - 14.0).lerp(F, sstep(u))
            return loc_to_w(lv, f), D(A(f)) + 180.0 + (yaw_loc - (gam - 14.0 + 180.0)) * sstep(u) + (gam - 14.0)
        t = f - f_L
        u = sstep((t - 3) / 12.0); lv = F.lerp(B, u)                           # se sienta de espaldas al banco
        return loc_to_w(lv, f), D(A(f)) + yaw_loc
    def arc(f):
        if f <= f_t or f >= f_L: return 0.0
        u = (f - f_t) / float(f_L - f_t); return 0.50 * 4 * u * (1 - u)
    seg(S, a, "Running", 1, f_t + 2, speed=1.15, blend=0)
    seg(S, a, "Jumping", f_c, f_L + 5, start=19, speed=sp, blend=5)
    seg(S, a, "Sitting Idle", f_s, None, start=0, speed=1.0, blend=10)
    for f in range(1, N + 12):
        p, yaw = path(f)
        if f > f_L + 18: yaw += 2.0 * math.sin((f - f_L) * 1.7)               # la risa lo sacude
        key_root(S, a, f, Mw(p, yaw))
    f_end = N + 11
    pin_feet(S, a, 1, f_end, lambda f: arc(f) + (TOP if f >= f_L - 2 else 0.0))
    S.cue("whoosh", 1, vol=-12); S.cue("boing", f_t, vol=-10); S.cue("pop", f_L, vol=-6); S.cue("bell", f_L + 2, vol=-8)
    S.cue("laugh", f_L + 22, vol=-6); S.cue("sigh", f_L + 60, vol=-12)
    S.f = N
    a.verify(S.f)
    faces(a, [(1, "enfado", 0.4), (f_t, "sorpresa", 0.5), (f_L + 2, "feliz", 1.0), (f_L + 40, "feliz", 1.0), (f_L + 70, "neutra", 0.5)], N, first_blink=14, every=44)
    audit(S, a, "nivel 950", 1, N, bench=bench_ang, contact={("Hips", "banco"): (f_L, N), ("*", "banco"): (f_L + 8, N)})
    audit_feet(S, a, "nivel 950 (carrera y disco)", 1, f_c, lambda f: 0.0)
    audit_feet(S, a, "nivel 950 (sobre el disco)", f_L + 2, N, lambda f: TOP)
    audit_parent(S, a, "nivel 950", f_L + 4, N, lambda f: path(f)[0])
    cam_follow(S, a, N + 10, [(1, Vector((-3.2, -6.0, 3.2)))], [(1, 50.0), (f_L + 30, 50.0), (f_L + 46, 85.0)])
    return a


# ------------------------------------------------------------------ nivel 4800
def l5(S):
    """4800: mira el centro (Looking Around), espera el hueco entre barras, cruza (Walking Left Turn) y se sienta (Sitting Idle) en el
    taburete-pedal del centro; la placa se hunde, los pilotos pasan a verde, el disco se desboca (arcoíris), las barras se abaten como
    una hélice y él queda quieto y sonriente bajo el banderín (tada, yay). El disco frena con un clunk."""
    f_look = 20
    yF = -0.68; spd = 0.085; g_in, r0, r1 = -40.0, 2.3, 1.05                       # entra en radial (en el marco del disco no hay barras que lo golpeen)
    OMS = 0.7 * OM0                                                                # mientras espera, el disco gira algo más despacio que en los otros niveles
    P1 = polar(r1, g_in); F = Vector((0.0, yF, 0.0)); yaw_in = g_in + 270.0                                       # de cara al centro (rumbo radial hacia dentro)
    n1 = int((r0 - r1) / spd); n2 = int(0.7 / spd) + 1
    # espera el hueco: elige cuándo echa a andar (f_walk) y la fase de las barras para cruzar el borde entre dos barras con holgura
    def route(f, fw):
        if f <= fw: return polar(r0, g_in), yaw_in
        if f <= fw + n1: return polar(r0 - (r0 - r1) * (f - fw) / float(n1), g_in), yaw_in
        u = min(1.0, (f - fw - n1) / float(n2)); return polar(r1 + (-yF - r1) * u, g_in + (-90.0 - g_in) * u), yaw_in + 40.0 * sstep(u)    # radial y luego arco hasta F: no apunta al taburete
    def slack(fw, ph):
        sl = 99.0
        for f in range(fw, fw + n1 + n2 + 1):
            p_, _y = route(f, fw); r = math.hypot(p_.x, p_.y); an = D(math.atan2(p_.y, p_.x))
            if R_IN + 0.05 < r < POST_R + 0.45:
                for k in range(4): sl = min(sl, abs(((an - (ph + D(OMS * (f - 1)) + 90.0 * k) + 180.0) % 360.0) - 180.0) * math.pi / 180.0 * max(r, 1.0) - 0.45)
        return sl
    bs = max(((slack(fw, ph), -fw, ph) for fw in range(30, 50) for ph in range(0, 90, 2)))
    f_walk, ph0 = -bs[1], float(bs[2])
    print(f"L5 espera el hueco: echa a andar en f{f_walk}, fase de barras {ph0:.0f} grados, holgura {bs[0]:+.2f} m")
    f_arr = f_walk + n1 + n2                                                       # llega a F
    f_turn = f_arr + 10; f_sit0 = f_turn + 2; f_sit = f_sit0 + 12                  # gira, se sienta
    f_press = f_sit + 2; f_go = f_press + 12; f_peak = f_go + 28; f_brake = f_peak + 40
    N = f_brake + 28
    om = lambda f: OMS if f < f_go else (OMS + (0.78 - OMS) * sstep((f - f_go) / 28.0) if f < f_brake else
                                         (0.78 + (OMS - 0.78) * sstep((f - f_brake) / 14.0)))
    make_alpha(N + 24, om)
    f_x = f_walk + int((r0 - POST_R) / spd)
    CUR.ph = ph0
    w = build_set(S, CUR.ph, None, N + 12); cam_fixed(S)
    flutter(S, w, N + 12, f_gust=f_go, amp=2.5, gust=30.0)
    tilt_posts(S, w, f_go + 10, f_peak + 6, 62.0)
    for f_, v_ in ((1, 0.4), (f_go, 0.4), (f_peak, 0.6), (f_brake, 0.6), (f_brake + 14, 0.4)):           # el giro se funde en un arcoíris
        S.sc.render.motion_blur_shutter = v_; S.sc.render.keyframe_insert("motion_blur_shutter", frame=f_)
    a = new_actor(S, w, ["Looking Around", "Walking Left Turn", "Sitting Idle"])
    seg(S, a, "Looking Around", 1, f_walk + 2, speed=1.0, blend=0)
    seg(S, a, "Walking Left Turn", f_walk, f_arr + 2, speed=1.3, blend=5, repeat=4)
    seg(S, a, "Looking Around", f_arr, f_sit0 + 2, start=40, speed=1.0, blend=5)
    seg(S, a, "Sitting Idle", f_sit0, None, start=0, speed=1.0, blend=10)
    sink = 0.03
    def path(f):
        if f <= f_arr: return route(f, f_walk)
        if f <= f_turn: return F.copy(), yaw_in + 40.0 + (360.0 - yaw_in - 40.0) * sstep((f - f_arr) / float(f_turn - f_arr))
        u = sstep((f - f_sit0) / float(f_sit - f_sit0))
        z = -sink * sstep((f - f_press) / 3.0)
        return Vector((0.0, yF * (1 - u), z)), 360.0
    def surf(f):
        r = math.hypot(*path(f)[0].xy)
        return TOP if r < R_DISC - 0.05 else 0.0
    for f in range(1, N + 12):
        p, yaw = path(f); key_root(S, a, f, Mw(p, yaw))
    f_end = N + 11
    # la placa-pedal (y el taburete y los pilotos) se hunde 3 cm al sentarse; los pilotos pasan a verde
    for f, z in ((f_press - 1, 0.0), (f_press + 3, -sink), (f_brake + 6, -sink), (f_brake + 10, 0.0)): S.key(w.centro, f, loc=(0, 0, z), interp="BEZIER")
    for L_ in w.red:
        S.key(L_, 1, scale=L_.scale[:], interp="CONSTANT"); S.key(L_, f_press + 3, scale=L_.scale[:], interp="CONSTANT"); S.key(L_, f_press + 4, scale=(0, 0, 0), interp="CONSTANT")
        S.key(L_, f_brake + 8, scale=(0, 0, 0), interp="CONSTANT"); S.key(L_, f_brake + 9, scale=(0.065, 0.065, 0.04), interp="CONSTANT")
    for G_ in w.grn:
        S.key(G_, 1, scale=(0, 0, 0), interp="CONSTANT"); S.key(G_, f_press + 3, scale=(0, 0, 0), interp="CONSTANT"); S.key(G_, f_press + 4, scale=(0.075, 0.075, 0.045), interp="CONSTANT")
        S.key(G_, f_brake + 8, scale=(0.075, 0.075, 0.045), interp="CONSTANT"); S.key(G_, f_brake + 9, scale=(0, 0, 0), interp="CONSTANT")
    pin_feet(S, a, 1, f_arr + 8, surf)
    pin_feet(S, a, f_arr + 9, f_end, lambda f: -sink * sstep((f - f_press) / 3.0) + TOP if f < f_brake + 6 else TOP)
    tune_phase(w, collect_pts(S, a, 1, f_arr + 4), [ph0 + d for d in range(-6, 7, 2)])
    S.cue("whoosh", 1, vol=-15); S.cue("whoosh", 25, vol=-15); S.cue("hmm", f_look, vol=-7); S.cue("pop", f_x - 6, vol=-9)
    S.cue("sigh", f_sit0 + 4, vol=-10); S.cue("clunk", f_press, vol=-2); S.cue("bell", f_press + 3, vol=-3)
    S.cue("riser", f_go - 6, vol=-4); S.cue("whoosh", f_go + 6, vol=-5); S.cue("tada", f_peak, vol=-3); S.cue("yay", f_peak + 4, vol=-4)
    S.cue("pop", f_peak + 14, vol=-8); S.cue("pop", f_peak + 18, vol=-8); S.cue("pop", f_peak + 21, vol=-8)
    S.cue("clunk", f_brake + 12, vol=-3); S.cue("hmm", f_brake + 22, vol=-8)
    S.f = N
    a.verify(S.f)
    faces(a, [(1, "neutra", 1.0), (f_look - 3, "sorpresa", 0.6), (f_look + 6, "feliz", 0.5), (f_x + 8, "neutra", 1.0), (f_sit, "neutra", 1.0), (f_press, "sorpresa", 0.6),
              (f_go - 4, "feliz", 1.0)], N, first_blink=24, every=48)
    audit(S, a, "nivel 4800", 1, N, tilted=lambda f: f >= f_go + 14, contact={("*", "taburete"): (f_sit - 6, N), ("Hips", "taburete"): (f_sit - 6, N)})
    audit_feet(S, a, "nivel 4800 (hierba y disco)", 1, f_arr + 8, surf)
    audit_feet(S, a, "nivel 4800 (placa)", f_arr + 9, N, lambda f: -sink * sstep((f - f_press) / 3.0) + TOP if f < f_brake + 6 else TOP)
    audit_parent(S, a, "nivel 4800", 1, N, lambda f: Vector((path(f)[0].x, path(f)[0].y, path(f)[0].z)))
    cam_follow(S, a, N + 10, [(1, Vector((0, -7.2, 3.8))), (f_peak, Vector((0, -7.2, 3.8))), (f_peak + 22, Vector((0, -3.6, 2.0)))],
               [(1, 50.0), (f_peak, 55.0), (f_peak + 22, 30.0)], fixed_tgt=[(f_peak, None), (f_peak + 22, Vector((0, 0, 1.0)))])
    return a


LEVELS = [(-380, l1), (-70, l2), (200, l3), (950, l4), (4800, l5)]
