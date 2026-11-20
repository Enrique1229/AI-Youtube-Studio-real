"""ep012 — Mini-historia (POV): "The bench has other plans". Parque con sol a plomo, humano de Mixamo con protagonista de dibujo.
Un hombre sudando corre a un banco y se derrumba; el banco parpadea UNA vez (únicos ojos), se levanta y trota hacia el único árbol
con sombra (visible desde el plano 1); el hombre corre tras él, el banco se sienta antes y lo deja de culo al sol; luego se desliza
un palmo y le hace sitio. ~11 s, corte cada 1-2 s, cámara keyeada CONSTANT entre planos. Sin niveles ni rótulo de IQ (un solo "nivel")."""
import math
import random
import bpy
from mathutils import Vector
from mixamo import MixamoActor
from klunk_toon import apply as klunk, expression, blink

TITLE = "The Bench That Walked Away"
ONSCREEN = "POV: The bench has other plans"
CAPTION = ONSCREEN          # render_episode: con CAPTION no hay rótulo de IQ; anim_build lo pone arriba en caja blanca todo el vídeo
SPEED = 1.0                 # historia de ~11 s: sin aceleración
ENV = "parque"
CUSTOM_CAMERA = True

# ---- geometría (metros). Cámara mirando hacia +y; árbol al fondo.
BX, BY0 = -7.5, 2.2                 # banco de partida
BY1 = 10.6                          # banco bajo el árbol
TREE = (-7.0, 12.0)
SH_C, SH_R = (-7.0, 11.4), (2.6, 2.2)    # disco de sombra (centro, semiejes): su borde cercano está en y = 9.2
LANE_X = -9.1                       # carril del hombre al perseguir
Y_STOP = 8.6                        # donde frena (aún al sol)
SIT_DY = 0.0                        # desfase y de la raíz del hombre sentado respecto al banco (se ajusta mirando fotogramas)
SIT_DZ = 0.0
LIFT = 0.21                         # altura del banco "de pie"
SLIDE = 0.50                        # deslizamiento final (x): se corre para dejar sitio

# ---- tiempos (fotogramas, 24 fps)
F_SIT = 27                          # el hombre se derrumba en el banco
F_EYES = 58                         # ojos del banco (parpadeo único)
F_RISE = 79                         # el banco se levanta
F_HOP = 100                         # el hombre salta del banco
F_B0, F_B1 = 111, 149               # el banco corre hacia el árbol
F_M0, F_M1 = 108, 152               # el hombre corre
F_FALL = 153                        # empieza Falling Back Death
K_IMPACT = 22                       # fotogramas desde F_FALL hasta el golpe
F_IMP = F_FALL + K_IMPACT
F_SLIDE = F_IMP + 20
F_HOP2 = F_IMP + 30
F_END = F_IMP + 78


def R(d): return math.radians(d)


def sstep(t): t = max(0.0, min(1.0, t)); return t * t * (3 - 2 * t)


# ------------------------------------------------------------------ materiales y utilidades
def mmat(S, name, rgb, rough=0.5, metal=0.0, emit=None, alpha=None):
    k = "m_" + name
    if k in S.mats: return S.mats[k]
    m = bpy.data.materials.new(k); m.use_nodes = True
    b = m.node_tree.nodes["Principled BSDF"]
    b.inputs["Base Color"].default_value = (*rgb, 1); b.inputs["Roughness"].default_value = rough; b.inputs["Metallic"].default_value = metal
    if emit:
        b.inputs["Emission Color"].default_value = (*emit[:3], 1); b.inputs["Emission Strength"].default_value = emit[3]
    if alpha is not None: b.inputs["Alpha"].default_value = alpha
    S.mats[k] = m
    return m


def wood_mat(S):
    """Madera real (Poly Haven brown_planks_03), coordenadas de objeto: veta a tamaño real."""
    if "bench_wood" in S.mats: return S.mats["bench_wood"]
    import env_real
    base = env_real._pbr(S, "brown_planks_03", res="1k", scale=1.0)
    m = base.copy(); m.name = "bench_wood"; nt = m.node_tree
    tc = next(n for n in nt.nodes if n.type == "TEX_COORD"); mp = next(n for n in nt.nodes if n.type == "MAPPING")
    for l in list(nt.links):
        if l.from_node is tc: nt.links.remove(l)
    nt.links.new(tc.outputs["Object"], mp.inputs["Vector"])
    mp.inputs["Scale"].default_value = (1.2, 1.2, 1.2)
    S.mats["bench_wood"] = m
    return m


def box(S, name, mat, dims, loc, parent=None, rot=(0, 0, 0)):
    o = S.obj("cube", name, "white", loc, (dims[0] / 2, dims[1] / 2, dims[2] / 2), rot, None, False)
    o.data.materials[0] = mat
    for o2 in bpy.context.view_layer.objects: o2.select_set(False)
    bpy.context.view_layer.objects.active = o; o.select_set(True)
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    if parent: o.parent = parent
    return o


def O(S, prim, name, mat, loc=(0, 0, 0), scale=(1, 1, 1), rot=(0, 0, 0), parent=None, smooth=True, **kw):
    o = S.obj(prim, name, "white", loc, scale, rot, parent, smooth, **kw); o.data.materials[0] = mat; return o


def bone_pos(S, a, bone, f, frac=0.0):
    S.sc.frame_set(f); bpy.context.view_layer.update()
    pb = a.arm.pose.bones[a.pfx + bone]
    return a.arm.matrix_world @ (pb.head + (pb.tail - pb.head) * frac)


def head_pos(S, a, f):
    S.sc.frame_set(f); bpy.context.view_layer.update()
    return a.head.matrix_world.translation.copy()


def place(S, a, f, x, y, z=0.0, yaw=0.0, interp="BEZIER"):
    S.key(a.root, f, loc=(x, y, z), rot=(0, 0, R(yaw)), interp=interp)


def foot_z(S, a, f):
    """Altura mundial del punto más bajo de los pies (pie y puntera) en el fotograma f."""
    S.sc.frame_set(f); bpy.context.view_layer.update()
    return min((a.arm.matrix_world @ a.arm.pose.bones[a.pfx + b].head).z for b in ("LeftFoot", "RightFoot", "LeftToeBase", "RightToeBase"))


def ground_feet(S, a, f0, f1, rest=0.015):
    """Pies en el suelo: el clip va en el sitio y la raíz lo desplaza, así que se baja la raíz en cada fotograma lo que el pie más bajo
    queda por encima de `rest` (sin fase de vuelo): el pie más bajo queda a z ≈ 0 (±3 cm)."""
    out = []
    for f in range(f0, f1 + 1):
        fz = foot_z(S, a, f)
        l = a.root.location.copy(); yaw = math.degrees(a.root.rotation_euler.z)
        place(S, a, f, l.x, l.y, l.z - (fz - rest), yaw, interp="LINEAR")
        out.append((f, round(fz - (fz - rest), 3)))
    return out


def seg(S, a, clip, f0, f1=None, start=0, speed=1.0, blend=4, repeat=1):
    S.f = f0
    cl = a.clips[clip]; avail = int((cl.frame_range[1] - cl.frame_range[0] - start) / speed)
    a.play(clip, frames=(min(avail * repeat, f1 - f0 + blend) if f1 is not None else None), speed=speed, blend=blend, start=start, repeat=repeat)


# ------------------------------------------------------------------ escenario
def clear_env(S):
    """Quita hierba, rocas, troncos y árboles de la zona de juego (queda un único árbol con sombra, el nuestro) y tapa el río."""
    for o in list(S.sc.objects):
        if o.instance_type == "COLLECTION" and -16.0 < o.location.x < 1.0 and -8.0 < o.location.y < 24.0:
            keep = "grass" in o.name and (o.location.y > 4.5 and o.location.y < 8.0 or o.location.x < -10.0)
            if not keep: bpy.data.objects.remove(o, do_unlink=True)
    ref = bpy.data.objects.get("orillaL")
    if getattr(S, "water", None): S.water.hide_render = True; S.water.hide_viewport = True
    dock = bpy.data.objects.get("muelle")
    if dock: dock.hide_render = True
    bpy.ops.mesh.primitive_plane_add(size=1, location=(0, 0, -0.002)); g = bpy.context.object; g.name = "suelo_rio"
    g.scale = (6.0, 400.0, 1.0)
    if ref is not None and ref.type == "MESH" and ref.data.materials: g.data.materials.append(ref.data.materials[0])


def sun_and_tree(S):
    """Sol a plomo (luz intensa y cálida, casi vertical, con disco visible) y el árbol de Poly Haven con su sombra clara."""
    import env_real
    sun = bpy.data.objects.get("sun")
    if sun:
        sun.data.energy = 7.0; sun.data.color = (1.0, 0.86, 0.62); sun.data.angle = R(1.2)
        sun.rotation_euler = (R(6), 0, R(-18))
    try: S.sc.view_settings.exposure = 0.15
    except Exception: pass
    disc = O(S, "cylinder", "sol", mmat(S, "sol", (1, 0.95, 0.7), emit=(1.0, 0.92, 0.6, 40.0)), (-7.6, 45.0, 24.0), (2.6, 2.6, 0.05), (R(90), 0, 0), vertices=48)
    S.key(disc, 29, scale=(2.6, 2.6, 0.05), interp="CONSTANT"); S.key(disc, 30, scale=(0.001,) * 3, interp="CONSTANT")   # el sol solo se ve en el plano 1
    col = bpy.data.collections.get("ph_island_tree_01") or env_real._model("island_tree_01")
    env_real._place(S, col, (TREE[0], TREE[1], 0), 0.4, 1.9)
    # sombra clara: elipse oscura semitransparente bajo el árbol (la sombra real del sol a plomo la refuerza)
    sh = O(S, "cylinder", "sombra_arbol", mmat(S, "sombra", (0.0, 0.01, 0.0), rough=1.0, alpha=0.42), (SH_C[0], SH_C[1], 0.012), (SH_R[0], SH_R[1], 0.004), vertices=64)
    # perro tumbado dentro de la sombra (motivo del banco legible: ya hay alguien a la sombra)
    fur = mmat(S, "pelo", (0.45, 0.28, 0.12), rough=0.9); dark = mmat(S, "pelo_osc", (0.18, 0.10, 0.05), rough=0.9)
    dg = S.empty("perro", (-5.55, 11.7, 0), None); dg.rotation_euler = (0, 0, R(-35))
    O(S, "uv_sphere", "perro_cuerpo", fur, (0, 0, 0.14), (0.34, 0.17, 0.14), parent=dg)
    O(S, "uv_sphere", "perro_cabeza", fur, (-0.36, 0, 0.17), (0.13, 0.11, 0.11), parent=dg)
    O(S, "uv_sphere", "perro_hocico", dark, (-0.47, 0, 0.14), (0.06, 0.05, 0.045), parent=dg)
    for sy in (-1, 1): O(S, "uv_sphere", "perro_oreja", dark, (-0.33, sy * 0.1, 0.22), (0.07, 0.03, 0.09), parent=dg)
    O(S, "uv_sphere", "perro_cola", fur, (0.36, 0.05, 0.1), (0.14, 0.04, 0.04), parent=dg)


class W: pass


def build_bench(S):
    """Banco de madera de parque (largo en x; asiento y respaldo; el frente mira a -y). Cuatro patas-pivote que "andan" por código
    y ojos que existen solo en el parpadeo del plano 2 (ocultos el resto del tiempo)."""
    w = W()
    w.root = S.empty("banco", (BX, BY0, 0))
    wood = wood_mat(S); iron = mmat(S, "hierro_banco", (0.05, 0.05, 0.055), rough=0.5, metal=0.9)
    box(S, "asiento", wood, (1.70, 0.44, 0.04), (0, 0.0, 0.44), parent=w.root)
    for dz, hh in ((0.62, 0.11), (0.77, 0.11)):
        box(S, "respaldo", wood, (1.70, 0.035, hh), (0, 0.22, dz + hh / 2), parent=w.root)
    for xx in (-0.80, 0.80):
        box(S, "poste", iron, (0.05, 0.05, 0.46), (xx, 0.22, 0.67), parent=w.root)
    w.legs = {}
    for nm, (lx, ly) in {"fl": (-0.76, -0.17), "fr": (0.76, -0.17), "bl": (-0.76, 0.17), "br": (0.76, 0.17)}.items():
        p = S.empty("pata_" + nm, (lx, ly, 0.42), parent=w.root)
        box(S, "pata", iron, (0.06, 0.06, 0.42), (0, 0, -0.21), parent=p)
        w.legs[nm] = p
    # ojos (en los extremos del travesaño superior, a ambos lados de los hombros del hombre sentado)
    white = mmat(S, "ojo_blanco", (0.97, 0.97, 0.95), rough=0.25); black = mmat(S, "ojo_negro", (0.01, 0.01, 0.01), rough=0.2)
    w.eyes = []
    for sx in (-1, 1):
        e = O(S, "uv_sphere", "ojo", white, (sx * 0.37, 0.10, 0.86), (0.001,) * 3, parent=w.root, segments=20, ring_count=12)
        pu = O(S, "uv_sphere", "pupila", black, (sx * 0.05, -0.74, 0.0), (0.46, 0.4, 0.46), parent=e, segments=14, ring_count=8)
        w.eyes.append(e)
    return w


def bench_key(S, w, f, x, y, z=0.0, yaw=0.0, interp="LINEAR", lift=None):
    S.key(w.root, f, loc=(x, y, z), rot=(0, 0, R(yaw)), interp=interp)


def legs_pose(S, w, f, swing=0.0, stretch=1.0):
    """Patas: pares diagonales (fl+br / fr+bl) con balanceo opuesto; stretch = escala vertical (patas estiradas al levantarse)."""
    for nm, p in w.legs.items():
        s = swing if nm in ("fl", "br") else -swing
        S.key(p, f, rot=(R(s), 0, 0), scale=(1, 1, stretch), interp="LINEAR")


def trot(S, w, f0, f1, stretch, amp=34.0, step_vol=-9):
    """Trote: cambio de pareja cada 3 fotogramas (6 = ciclo de 4 pasos/s), con un paso sonoro por cada cambio."""
    k = 0
    for f in range(f0, f1 + 1, 3):
        legs_pose(S, w, f, amp * (1 if k % 2 == 0 else -1), stretch)
        if f < f1: S.cue("step", f, vol=step_vol)
        k += 1
    legs_pose(S, w, f1 + 2, 0.0, stretch)


def eyes_blink(S, w, f0):
    """Ojos: aparecen de golpe (pop), miran, parpadean UNA vez y desaparecen. Única aparición."""
    s = 0.105
    for e in w.eyes:
        S.key(e, f0 - 1, scale=(0.001,) * 3, interp="LINEAR")
        S.key(e, f0, scale=(s, s, s), interp="LINEAR")
        S.key(e, f0 + 8, scale=(s, s, s), interp="LINEAR")
        S.key(e, f0 + 10, scale=(s * 1.05, s, s * 0.08), interp="LINEAR")      # párpado cerrado
        S.key(e, f0 + 12, scale=(s, s, s), interp="LINEAR")
        S.key(e, f0 + 17, scale=(s, s, s), interp="LINEAR")
        S.key(e, f0 + 18, scale=(0.001,) * 3, interp="LINEAR")
    S.cue("pop", f0, vol=-7); S.cue("pop", f0 + 10, vol=-10)


def sweat(S, a, f, dx=0.0):
    """Gota de sudor: sale de la sien y cae (cartoon)."""
    hp = head_pos(S, a, f)
    d = O(S, "uv_sphere", "sudor", mmat(S, "sudor", (0.55, 0.8, 1.0), rough=0.1), (hp.x, hp.y, hp.z), (0.001,) * 3, segments=10, ring_count=6)
    S.key(d, f - 1, loc=(hp.x + dx, hp.y - 0.05, hp.z + 0.05), scale=(0.001,) * 3, interp="LINEAR")
    S.key(d, f, loc=(hp.x + dx, hp.y - 0.05, hp.z + 0.05), scale=(0.025, 0.025, 0.035), interp="LINEAR")
    S.key(d, f + 8, loc=(hp.x + dx * 1.4, hp.y - 0.05, hp.z - 0.35), scale=(0.02, 0.02, 0.03), interp="LINEAR")
    S.key(d, f + 9, scale=(0.001,) * 3, interp="LINEAR")


# ------------------------------------------------------------------ cámara
def cam_set(S, f, loc, tgt, lens):
    S.cam.location = loc; S.cam.keyframe_insert("location", frame=f)
    S.cam.data.lens = lens; S.cam.data.keyframe_insert("lens", frame=f)
    S.tgt.location = tgt; S.tgt.keyframe_insert("location", frame=f)


def yb(f):   # y del banco en la carrera
    return BY0 + (BY1 - BY0) * sstep((f - F_B0) / float(F_B1 - F_B0))


def ym(f):   # y del hombre en la carrera (lineal con arranque suave y frenada)
    return 1.3 + (Y_STOP - 1.3) * sstep((f - F_M0) / float(F_M1 - F_M0)) ** 0.8


# ------------------------------------------------------------------ la historia
def l1(S):
    clear_env(S); sun_and_tree(S)
    w = build_bench(S)
    S.cam.data.dof.use_dof = False
    a = MixamoActor(S, x=-9.9, yaw=90, use=["Running", "Sitting Idle", "Falling Back Death"]); klunk(a)

    # ---- hombre ----
    seg(S, a, "Running", 1, F_SIT - 3, start=0, repeat=4, blend=3)
    seg(S, a, "Sitting Idle", F_SIT - 4, F_HOP + 2, start=0, blend=5)
    seg(S, a, "Running", F_HOP, F_M1 + 3, start=0, repeat=6, blend=4)
    seg(S, a, "Falling Back Death", F_FALL, F_HOP2 - 1, start=0, blend=3)
    seg(S, a, "Running", F_HOP2 - 3, F_HOP2 + 9, start=4, blend=3)               # el salto de vuelta al banco es un salto en pose de carrera
    seg(S, a, "Sitting Idle", F_HOP2 + 7, None, start=0, blend=3)                 # solo se sienta cuando ya está sobre el asiento

    # A) carrera lateral hacia el banco (en el carril y = 1.45), gira y se derrumba de espaldas en el asiento
    sy = BY0 + SIT_DY
    place(S, a, 1, -9.9, 1.45, 0, 90, interp="LINEAR")
    for f in range(2, F_SIT - 7): place(S, a, f, -9.9 + (BX - 0.1 + 9.9) * (f - 1) / float(F_SIT - 9), 1.45, 0, 90, interp="LINEAR")
    place(S, a, F_SIT - 3, BX, 1.75, 0.12, 45)
    place(S, a, F_SIT + 2, BX, sy, SIT_DZ, 0)
    # sentado: sigue al banco mientras éste sube
    place(S, a, F_RISE - 1, BX, sy, SIT_DZ, 0)
    place(S, a, F_RISE + 8, BX, sy, SIT_DZ + LIFT * 1.35, 0)
    place(S, a, F_RISE + 14, BX, sy, SIT_DZ + LIFT, 0)
    place(S, a, F_HOP - 1, BX, sy, SIT_DZ + LIFT, 0)
    # salta al suelo (carril de carrera), gira hacia el árbol y arranca
    # salta hacia delante-izquierda por encima del extremo del banco (1,7 m de largo) y cae en el carril, fuera de su giro
    place(S, a, F_HOP + 3, (BX + LANE_X) / 2, 1.15, 0.55, 60)
    place(S, a, F_M0, LANE_X, ym(F_M0), 0.0, 180)
    for f in range(F_M0 + 1, F_M1 + 1):
        place(S, a, f, LANE_X, ym(f), 0, 180, interp="LINEAR")
    place(S, a, F_FALL, LANE_X, Y_STOP + 0.15, 0, 180)
    place(S, a, F_IMP + 4, LANE_X, Y_STOP + 0.15, 0, 180)
    # salta a la hueco que deja el banco (a la sombra, de cara a cámara)
    xh = BX - 0.0
    place(S, a, F_HOP2 - 3, LANE_X, Y_STOP + 0.15, 0, 180)
    place(S, a, F_HOP2 + 2, (LANE_X + xh) / 2, (Y_STOP + BY1) / 2, 0.8, 139)
    place(S, a, F_HOP2 + 9, xh, BY1 + SIT_DY, SIT_DZ, 0)
    for f in range(F_HOP2 + 12, F_END + 1, 3):                       # risa: sacudidas de los hombros (el clip Laughing es de pie)
        place(S, a, f, xh, BY1 + SIT_DY, SIT_DZ + (0.025 if ((f - F_HOP2) // 3) % 2 else 0.0), 0, interp="LINEAR")

    # pies en el suelo durante la carrera (compensa la altura del clip)
    gf = ground_feet(S, a, 2, F_SIT - 7) + ground_feet(S, a, F_M0 + 2, F_M1)
    print("[ep012] pies (f, z del pie más bajo tras compensar):", gf[::4])
    # ---- banco ----
    bench_key(S, w, 1, BX, BY0, 0, 0); legs_pose(S, w, 1, 0, 1.0)
    eyes_blink(S, w, F_EYES)
    # se levanta: agacha, resorte y queda de pie sobre patas estiradas
    st = 1.0 + LIFT / 0.42
    bench_key(S, w, F_RISE - 6, BX, BY0, 0, 0); legs_pose(S, w, F_RISE - 6, 0, 1.0)
    bench_key(S, w, F_RISE - 1, BX, BY0, -0.05, 0, "BEZIER"); legs_pose(S, w, F_RISE - 1, 0, 0.88)
    bench_key(S, w, F_RISE + 8, BX, BY0, LIFT * 1.35, 0, "BEZIER"); legs_pose(S, w, F_RISE + 8, 0, st * 1.15)
    bench_key(S, w, F_RISE + 14, BX, BY0, LIFT, 0, "BEZIER"); legs_pose(S, w, F_RISE + 14, 0, st)
    bench_key(S, w, F_HOP - 1, BX, BY0, LIFT, 0); legs_pose(S, w, F_HOP - 1, 0, st)
    # el hombre salta: el banco se estremece y da media vuelta (de cara al árbol)
    bench_key(S, w, F_HOP + 6, BX, BY0, LIFT, 0, "BEZIER")
    bench_key(S, w, F_B0 - 1, BX, BY0, LIFT, 180, "BEZIER")
    # trote
    for f in range(F_B0, F_B1 + 1):
        y = yb(f); bob = 0.05 * abs(math.sin((f - F_B0) * math.pi / 3.0))
        bench_key(S, w, f, BX, y, LIFT + bob, 180)
    trot(S, w, F_B0, F_B1, st)
    # llega: pirueta con salto (media vuelta, de cara a cámara) y se sienta de golpe
    bench_key(S, w, F_B1 + 3, BX, BY1, LIFT + 0.45, 270, "BEZIER")
    bench_key(S, w, F_B1 + 6, BX, BY1, 0.0, 360, "BEZIER"); legs_pose(S, w, F_B1 + 6, 0, 1.0)
    bench_key(S, w, F_B1 + 8, BX, BY1, -0.03, 360, "BEZIER"); legs_pose(S, w, F_B1 + 8, 0, 0.93)
    bench_key(S, w, F_B1 + 11, BX, BY1, 0.0, 360, "BEZIER"); legs_pose(S, w, F_B1 + 11, 0, 1.0)
    # hace sitio: se desliza un palmo
    bench_key(S, w, F_SLIDE - 1, BX, BY1, 0, 360, "BEZIER")
    bench_key(S, w, F_SLIDE + 9, BX + SLIDE, BY1, 0, 360, "BEZIER")

    # ---- sonido ----
    S.cue("whoosh", 1, vol=-10); S.cue("step", 8, vol=-14)
    S.cue("hit", F_SIT + 2, vol=-8); S.cue("boing", F_SIT + 3, vol=-8)
    S.cue("creak", F_RISE - 3, vol=-8); S.cue("boing", F_RISE, vol=-6); S.cue("whoosh", F_RISE + 2, vol=-12)
    S.cue("boing", F_HOP + 2, vol=-8); S.cue("whoosh", F_HOP + 4, vol=-8)
    S.cue("whoosh", F_B0 - 2, vol=-6); S.cue("whoosh", F_M0 + 2, vol=-10)
    S.cue("boing", F_B1 + 1, vol=-8); S.cue("clunk", F_B1 + 6, vol=-5); S.cue("hit", F_B1 + 6, vol=-12)
    S.cue("whoosh", F_FALL - 4, vol=-10)
    S.cue("hit", F_IMP, vol=-3); S.cue("slide_down", F_IMP + 4, vol=-8)
    S.cue("creak", F_SLIDE - 2, vol=-9); S.cue("whoosh", F_SLIDE + 1, vol=-12); S.cue("step", F_SLIDE + 5, vol=-9)
    S.cue("clunk", F_SLIDE + 10, vol=-10)
    S.cue("boing", F_HOP2 + 1, vol=-6); S.cue("pop", F_HOP2 + 9, vol=-9)
    S.cue("tada", F_HOP2 + 14, vol=-7)

    # ---- cara del protagonista: parpadeo cada 2-3 s y expresiones en los momentos clave ----
    for f in (10, 66, 124, 183, 224, 262, 300):
        if f < F_END - 5: blink(a, f)
    expression(a, "neutra", 1, 1.0, ramp=2)
    expression(a, "sorpresa", F_EYES + 12, 1.0, ramp=3)
    expression(a, "neutra", F_HOP + 4, 1.0, ramp=3)
    expression(a, "enfado", F_IMP, 1.0, ramp=3)
    expression(a, "neutra", F_HOP2 - 2, 1.0, ramp=3)
    expression(a, "feliz", F_HOP2 + 16, 1.0, ramp=4)
    for f, dx in ((4, 0.04), (12, -0.04), (20, 0.05)): sweat(S, a, f, dx)

    # ---- cámara: planos de 1-2 s con cortes secos (CONSTANT) ----
    cam = []
    def shot(f0, f1, fn):
        for f in range(f0, f1 + 1):
            loc, tg, lens = fn(f); cam.append((f, loc, tg, lens))
    ex, ey = BX, 0.0
    # 1 general: carrera hacia el banco, árbol y sol al fondo
    shot(1, 30, lambda f: ((-9.3 + 0.9 * (f / 30.0), -2.4, 1.15), (-8.9 + 0.9 * (f / 30.0), 6.0, 1.45), 30))
    # 2 medio: se derrumba en el banco
    shot(31, 56, lambda f: ((BX + 0.1, -0.9, 1.15), (BX, BY0, 1.2), 34))
    # 3 primer plano del banco: parpadeo
    shot(57, 76, lambda f: ((BX + 0.05, 0.0, 1.0), (BX, BY0 + 0.1, 1.1), 38))
    # 4 primer plano de la cara: sorpresa (sigue a la cabeza)
    for f in range(77, 98):
        hp = head_pos(S, a, f); cam.append((f, (hp.x, hp.y - 1.7, hp.z + 0.12), (hp.x, hp.y, hp.z + 0.1), 50))
    # 5 medio: salta del banco, el banco da media vuelta y arranca
    shot(98, 120, lambda f: ((BX - 0.7, -1.0, 1.25), (BX - 0.55, BY0 + 0.3, 1.0), 30))
    # 6 persecución: plano lateral que sigue al banco y al hombre en profundidad
    shot(121, 147, lambda f: ((-1.2, (yb(f) + ym(f)) / 2 - 1.5, 1.3), (-7.9, (yb(f) + ym(f)) / 2 + 0.5, 1.0), 27))
    # 7 el árbol con sombra: el banco llega, se sienta; el hombre frena fuera de la sombra y cae de culo
    shot(148, F_IMP - 1, lambda f: ((-4.4, 8.2, 1.3), (-7.6, 8.9, 1.0), 24))
    # 8 primer plano de la cara: enfado al caer al sol
    for f in range(F_IMP, F_IMP + 17):
        hp = head_pos(S, a, f); cam.append((f, (hp.x + 0.25, hp.y + 0.95, hp.z + 0.85), (hp.x, hp.y, hp.z), 40))
    # 9 el banco se desliza y hace sitio (plano lateral con árbol y perro)
    shot(F_IMP + 17, F_HOP2 + 12, lambda f: ((-0.4, 9.0, 1.4), (-7.4, 9.2, 0.9), 22))
    # 10 remate: sentados a la sombra, cara a cámara, se ríe
    shot(F_HOP2 + 13, F_END + 10, lambda f: ((BX + 0.1, BY1 - 3.6, 1.2), (BX - 0.1, BY1, 1.0), 34))
    for f, loc, tg, lens in cam: cam_set(S, f, loc, tg, lens)
    S.set_interp(S.cam, "CONSTANT", ("location",)); S.set_interp(S.cam.data, "CONSTANT"); S.set_interp(S.tgt, "CONSTANT")
    S._bench = w
    S.f = F_END
    a.verify(S.f)
    return a


LEVELS = [(0, l1)]
