"""ep015 — Mini-historia (POV): "The Pool With a Secret". Piscina exterior VACIA (azulejos azul claro con juntas, bordes de piedra,
escalerilla metálica, trampolín de 1 m, césped y losas). Un hombre sube al trampolín, mira abajo (un solo Looking Around, huh/hmm),
salta con los ojos cerrados: el fondo se hunde como una cama elástica, pausa de un beat con el fondo hundido y primer boing.
EXACTAMENTE tres botes, boing cada vez más agudo (boing, boing_hi, boing_top); el tercero aterriza en el trampolín en la pose y el
encuadre del fotograma 1 (bucle). ~13 s, cortes de plano cada 1-2 s, cámara CONSTANT. Cielo = HDRI del parque (sin río ni muelle).
Suelo: cubierta (z=-1.0) a 1 m por debajo del trampolín, de modo que los pies del protagonista pisan z≈0 sobre la tabla."""
import math
import bpy
from mathutils import Vector
from mixamo import MixamoActor
from klunk_toon import apply as klunk, expression, blink

TITLE = "The Pool With a Secret"
CAPTION = "POV: the pool is empty"
SPEED = 1.0
ENV = "mesa"                 # entorno mínimo del kit: se vacía y se construye el patio aquí
CUSTOM_CAMERA = True

# ---- geometría (metros). Cubierta a z = DECK; trampolín a 1 m (cara superior z = 0).
DECK = -1.0
X0, X1, Y0, Y1 = -2.0, 3.0, -1.2, 3.6          # hueco de la piscina
YC = 0.5 * (Y0 + Y1)                            # eje del trampolín y centro del fondo
FLOOR = -2.0                                    # fondo de la piscina (1 m bajo la cubierta)
DEPTH = 0.95                                    # lo que se hunde el fondo
BX0, BX1 = -4.6, -1.2                           # trampolín (x)
X_START, X_TIP = -3.3, -1.8                     # pose del fotograma 1 (también la de aterrizaje) y punta donde mira
REST = 0.015                                    # el pie más bajo queda a 1,5 cm de la superficie

# ---- tiempos (fotogramas, 24 fps)
F_WALK = 48
F_J0 = 110                                      # despegue del trampolín
T_AIR_A = 18
F_IN_A = F_J0 + T_AIR_A                         # primer contacto con el fondo
SINK_A, HOLD_A, REL_A = 7, 11, 6                # hundirse, PAUSA con el fondo hundido, soltarse
F_OUT_A = F_IN_A + SINK_A + HOLD_A + REL_A
T1, T2, T3 = 29, 31, 24                         # tiempos de vuelo de los tres botes
F_IN_B = F_OUT_A + T1
F_OUT_B = F_IN_B + 8
F_IN_C = F_OUT_B + T2
F_OUT_C = F_IN_C + 8
F_LAND = F_OUT_C + T3
F_END = F_LAND + 62
APEX = (1.7, 2.4, 2.0)                          # altura máxima (pies) de cada bote respecto al suelo mundial
# x de los contactos: despegue, A, B, C, aterrizaje
XS = {"tip": X_TIP, "A": 0.0, "B": 0.7, "C": 0.3, "land": X_START}


def R(d): return math.radians(d)


def ease(t, p=2.0): t = max(0.0, min(1.0, t)); return t * t * (3 - 2 * t)


def shape(x, y):
    """Forma de la membrana: 0 en el borde (anclada a las paredes), ~1 en el centro."""
    u = (x - X0) / (X1 - X0); v = (y - Y0) / (Y1 - Y0)
    if not (0 < u < 1 and 0 < v < 1): return 0.0
    return (math.sin(math.pi * u) * math.sin(math.pi * v)) ** 0.55


# ---- evolución del hundimiento s(f): 1 = hundido al máximo, 0 = reposo, <0 = abombado hacia arriba
def build_s():
    pts = [(0, 0.0)]
    for t_in, sink, hold, rel in ((F_IN_A, SINK_A, HOLD_A, REL_A), (F_IN_B, 4, 0, 4), (F_IN_C, 4, 0, 4)):
        t_out = t_in + sink + hold + rel
        pts += [(t_in, 0.0), (t_in + sink, 1.0), (t_in + sink + hold, 1.0), (t_out, 0.0),
                (t_out + 4, -0.35), (t_out + 9, 0.12), (t_out + 14, -0.05), (t_out + 19, 0.0)]
    pts.append((F_END + 20, 0.0))
    # puntos de contacto con la salida acelerada (cúbica) y la entrada suave
    kinds = {}
    for t_in, sink, hold, rel in ((F_IN_A, SINK_A, HOLD_A, REL_A), (F_IN_B, 4, 0, 4), (F_IN_C, 4, 0, 4)):
        kinds[t_in + sink + hold] = "rel"
    def s_of(f):
        for (fa, sa), (fb, sb) in zip(pts, pts[1:]):
            if fa <= f <= fb and fb > fa:
                t = (f - fa) / float(fb - fa)
                if fa in kinds: return sa + (sb - sa) * (t ** 3)
                return sa + (sb - sa) * ease(t)
        return 0.0
    return s_of


S_OF = build_s()


def floor_z(x, y, f): return FLOOR - DEPTH * S_OF(f) * shape(x, y)


# ------------------------------------------------------------------ materiales
def mmat(S, name, rgb, rough=0.5, metal=0.0):
    k = "m_" + name
    if k in S.mats: return S.mats[k]
    m = bpy.data.materials.new(k); m.use_nodes = True
    b = m.node_tree.nodes["Principled BSDF"]
    b.inputs["Base Color"].default_value = (*rgb, 1); b.inputs["Roughness"].default_value = rough; b.inputs["Metallic"].default_value = metal
    S.mats[k] = m
    return m


def tile_mat(S, name, axes, dims, size, c1, c2, mortar, msize=0.03, rough=0.3, bump=0.25):
    """Azulejos cuadrados con juntas (nodo Brick) sobre coordenadas GENERADAS (siguen a la malla en reposo: no se estiran al hundirse).
    axes = índices de los dos ejes del plano (0=x,1=y,2=z); dims = tamaño del objeto (m); size = lado del azulejo (m)."""
    k = "t_" + name
    if k in S.mats: return S.mats[k]
    m = bpy.data.materials.new(k); m.use_nodes = True; nt = m.node_tree; N = nt.nodes; L = nt.links
    b = N["Principled BSDF"]; b.inputs["Roughness"].default_value = rough
    tc = N.new("ShaderNodeTexCoord"); sep = N.new("ShaderNodeSeparateXYZ"); L.new(tc.outputs["Generated"], sep.inputs[0])
    mu = [N.new("ShaderNodeMath") for _ in range(2)]
    for i, mm in enumerate(mu):
        mm.operation = "MULTIPLY"; L.new(sep.outputs[axes[i]], mm.inputs[0]); mm.inputs[1].default_value = dims[axes[i]]
    cb = N.new("ShaderNodeCombineXYZ"); L.new(mu[0].outputs[0], cb.inputs["X"]); L.new(mu[1].outputs[0], cb.inputs["Y"])
    br = N.new("ShaderNodeTexBrick"); br.offset = 0.0; br.squash = 1.0
    br.inputs["Scale"].default_value = 0.5 / size; br.inputs["Brick Width"].default_value = 0.5; br.inputs["Row Height"].default_value = 0.5
    br.inputs["Mortar Size"].default_value = msize; br.inputs["Mortar Smooth"].default_value = 0.0
    br.inputs["Color1"].default_value = (*c1, 1); br.inputs["Color2"].default_value = (*c2, 1); br.inputs["Mortar"].default_value = (*mortar, 1)
    br.inputs["Bias"].default_value = 0.0
    L.new(cb.outputs["Vector"], br.inputs["Vector"]); L.new(br.outputs["Color"], b.inputs["Base Color"])
    bp = N.new("ShaderNodeBump"); bp.inputs["Strength"].default_value = bump; bp.inputs["Distance"].default_value = 0.01
    L.new(br.outputs["Fac"], bp.inputs["Height"]); L.new(bp.outputs["Normal"], b.inputs["Normal"])
    S.mats[k] = m
    return m


def box(S, name, mat, x0, x1, y0, y1, z0, z1, parent=None):
    o = S.obj("cube", name, "white", ((x0 + x1) / 2, (y0 + y1) / 2, (z0 + z1) / 2), ((x1 - x0) / 2, (y1 - y0) / 2, (z1 - z0) / 2), (0, 0, 0), None, False)
    o.data.materials[0] = mat
    for o2 in bpy.context.view_layer.objects: o2.select_set(False)
    bpy.context.view_layer.objects.active = o; o.select_set(True)
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    if parent: o.parent = parent
    return o


def cyl(S, name, mat, p0, p1, r=0.025):
    """Tubo entre dos puntos."""
    a, b = Vector(p0), Vector(p1); d = b - a
    o = S.obj("cylinder", name, "white", tuple((a + b) / 2), (r, r, d.length / 2), (0, 0, 0), None, True, vertices=16)
    o.rotation_mode = "QUATERNION"; o.rotation_quaternion = Vector((0, 0, 1)).rotation_difference(d)
    o.data.materials[0] = mat
    return o


# ------------------------------------------------------------------ escenario
def clear_stage(S):
    """Quita todo lo de env_mesa (encimera, paredes, focos): solo quedan el sol, la cámara y su objetivo."""
    for o in list(S.sc.objects):
        if o.name.startswith("sun") or o is S.cam or o is S.tgt: continue
        bpy.data.objects.remove(o, do_unlink=True)


def build_pool(S):
    import env_real
    clear_stage(S)
    env_real._hdri(S, strength=1.0, rot_deg=40)                  # cielo: HDRI del parque (se ve al fondo; sin río ni muelle)
    sun = bpy.data.objects["sun"]; sun.data.energy = 3.0; sun.data.color = (1.0, 0.92, 0.80); sun.data.angle = R(1.5)
    sun.rotation_euler = (R(48), 0, R(-30))
    S.sc.view_settings.view_transform = "AgX"
    try: S.sc.view_settings.look = "AgX - Base Contrast"; S.sc.view_settings.exposure = 0.0
    except Exception: pass
    S.cam.data.dof.use_dof = False; S.water = None
    # césped (textura PBR real) hasta el horizonte
    grass = env_real._pbr(S, "aerial_grass_rock", scale=40.0)
    GX0, GX1, GY0, GY1 = -8.0, X1 + 0.35 + 8.0, Y0 - 0.35 - 4.5, Y1 + 0.35 + 4.5      # límites de la cubierta; fuera, césped (el hueco de la piscina queda libre)
    for nm, (a0, a1, b0, b1) in {"l": (-150, GX0, -150, 150), "r": (GX1, 150, -150, 150), "f": (GX0, GX1, -150, GY0), "b": (GX0, GX1, GY1, 150)}.items():
        bpy.ops.mesh.primitive_plane_add(size=1, location=((a0 + a1) / 2, (b0 + b1) / 2, DECK - 0.06)); g = bpy.context.object
        g.name = "cesped_" + nm; g.scale = ((a1 - a0), (b1 - b0), 1); g.data.materials.append(grass)
        bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
        # UV en coordenadas de mundo (la textura se repite cada 3 m en todos los trozos)
        g.data.uv_layers.active.data.foreach_set("uv", [c for l in g.data.loops for c in ((g.data.vertices[l.vertex_index].co.x + g.location.x) / 120.0, (g.data.vertices[l.vertex_index].co.y + g.location.y) / 120.0)])
    # losas de la cubierta alrededor de la piscina
    slab = tile_mat(S, "losa", (0, 1), (1, 1, 1), 0.6, (0.80, 0.76, 0.68), (0.74, 0.70, 0.62), (0.52, 0.50, 0.46), msize=0.025, rough=0.8, bump=0.3)
    stone = S.pmat("piedra_borde", [(0.3, (0.74, 0.70, 0.62)), (0.7, (0.86, 0.82, 0.74))], scale=14, rough=0.7, bump=0.25)
    CW = 0.35                                                    # ancho de la albardilla (borde de piedra)
    ex = 8.0
    for nm, (a0, a1, b0, b1) in {"front": (-ex, X1 + CW + ex, Y0 - CW - 4.5, Y0 - CW), "back": (-ex, X1 + CW + ex, Y1 + CW, Y1 + CW + 4.5),
                                 "left": (-ex, X0 - CW, Y0 - CW, Y1 + CW), "right": (X1 + CW, X1 + CW + ex, Y0 - CW, Y1 + CW)}.items():
        dims = (a1 - a0, b1 - b0, 0.3)
        m = tile_mat(S, "losa_" + nm, (0, 1), dims, 0.6, (0.80, 0.76, 0.68), (0.74, 0.70, 0.62), (0.52, 0.50, 0.46), msize=0.025, rough=0.8, bump=0.3)
        box(S, "cubierta_" + nm, m, a0, a1, b0, b1, DECK - 0.3, DECK)
    # albardilla de piedra (borde): 4 piezas con vuelo hacia dentro
    for nm, (a0, a1, b0, b1) in {"f": (X0 - CW, X1 + CW, Y0 - CW, Y0 + 0.04), "b": (X0 - CW, X1 + CW, Y1 - 0.04, Y1 + CW),
                                 "l": (X0 - CW, X0 + 0.04, Y0 + 0.04, Y1 - 0.04), "r": (X1 - 0.04, X1 + CW, Y0 + 0.04, Y1 - 0.04)}.items():
        box(S, "borde_" + nm, stone, a0, a1, b0, b1, DECK, DECK + 0.08)
    # paredes de azulejo (cara interior con juntas) hasta bien por debajo del fondo, que se hunde
    ZB = FLOOR - DEPTH - 0.4
    walls = {"far": (X0, X1, Y1, Y1 + 0.3, (0, 2)), "near": (X0, X1, Y0 - 0.3, Y0, (0, 2)), "left": (X0 - 0.3, X0, Y0, Y1, (1, 2)), "right": (X1, X1 + 0.3, Y0, Y1, (1, 2))}
    for nm, (a0, a1, b0, b1, ax) in walls.items():
        dims = (a1 - a0, b1 - b0, DECK + 0.0 - ZB)
        m = tile_mat(S, "pared_" + nm, ax, dims, 0.3, (0.52, 0.80, 0.93), (0.60, 0.86, 0.96), (0.90, 0.94, 0.95), msize=0.04, rough=0.2)
        box(S, "pared_" + nm, m, a0, a1, b0, b1, ZB, DECK)
    # fondo de azulejos: rejilla subdividida con shape key "dip" (cama elástica); slider de -1 a 1,5
    bpy.ops.mesh.primitive_grid_add(x_subdivisions=64, y_subdivisions=56, size=1.0, location=((X0 + X1) / 2, YC, FLOOR))
    fl = bpy.context.object; fl.name = "fondo_piscina"; fl.scale = (X1 - X0, Y1 - Y0, 1.0)
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    for p in fl.data.polygons: p.use_smooth = True
    fl.data.materials.append(tile_mat(S, "fondo", (0, 1), (X1 - X0, Y1 - Y0, 1.0), 0.3, (0.52, 0.80, 0.93), (0.60, 0.86, 0.96), (0.90, 0.94, 0.95), msize=0.04, rough=0.2))
    fl.shape_key_add(name="Basis", from_mix=False); dip = fl.shape_key_add(name="dip", from_mix=False)
    dip.slider_min = -1.0; dip.slider_max = 1.5
    for v, vb in zip(dip.data, fl.data.vertices):
        v.co.z = vb.co.z - DEPTH * shape(vb.co.x + (X0 + X1) / 2, vb.co.y + YC)      # coordenadas locales -> mundo (origen en el centro del fondo)
    S.floor, S.dip = fl, dip
    # trampolín de 1 m: base de hormigón, tabla antideslizante, tornillería
    conc = S.pmat("hormigon", [(0.3, (0.60, 0.60, 0.58)), (0.7, (0.74, 0.74, 0.72))], scale=18, rough=0.8, bump=0.3)
    board_m = S.pmat("tabla", [(0.3, (0.82, 0.84, 0.86)), (0.7, (0.92, 0.93, 0.94))], scale=60, rough=0.55, bump=0.5, detail=2)
    metal = mmat(S, "cromo", (0.80, 0.82, 0.86), rough=0.18, metal=0.95)
    S.board = box(S, "trampolin", board_m, BX0, BX1, YC - 0.3, YC + 0.3, -0.08, 0.0)
    box(S, "base_trampolin", conc, BX0 + 0.05, BX0 + 0.85, YC - 0.4, YC + 0.4, DECK, -0.08)
    box(S, "pivote_trampolin", metal, BX0 + 1.7, BX0 + 1.78, YC - 0.25, YC + 0.25, DECK, -0.08)
    # escalerilla metálica en la pared del fondo (carriles curvos por encima del borde, peldaños)
    XL, YW = 2.3, Y1 - 0.16
    for sx in (-0.25, 0.25):
        cyl(S, "carril_in", metal, (XL + sx, YW, -1.75), (XL + sx, YW, -0.38), 0.025)
        cyl(S, "carril_arco", metal, (XL + sx, YW, -0.38), (XL + sx, Y1 + 0.28, -0.38), 0.025)
        cyl(S, "carril_out", metal, (XL + sx, Y1 + 0.28, -0.38), (XL + sx, Y1 + 0.28, DECK), 0.025)
        S.obj("uv_sphere", "codo", "white", (XL + sx, YW, -0.38), (0.032,) * 3).data.materials[0] = metal
        S.obj("uv_sphere", "codo", "white", (XL + sx, Y1 + 0.28, -0.38), (0.032,) * 3).data.materials[0] = metal
    for zz in (-0.85, -1.2, -1.55):
        cyl(S, "peldano", metal, (XL - 0.25, YW, zz), (XL + 0.25, YW, zz), 0.02)



# ------------------------------------------------------------------ utilidades de animación
def head_pos(S, a, f):
    S.sc.frame_set(f); bpy.context.view_layer.update()
    return a.head.matrix_world.translation.copy()


def foot_z(S, a, f):
    S.sc.frame_set(f); bpy.context.view_layer.update()
    mw, pb = a.arm.matrix_world, a.arm.pose.bones
    zs = [(mw @ pb[a.pfx + b].head).z for b in ("LeftFoot", "RightFoot", "LeftToeBase", "RightToeBase", "LeftToe_End", "RightToe_End")]
    zs += [(mw @ pb[a.pfx + b].tail).z for b in ("LeftToe_End", "RightToe_End")]            # la punta de la zapatilla también cuenta
    return min(zs)


def seg(S, a, clip, f0, f1, start=0, speed=1.0, blend=3, repeat=1):
    S.f = f0
    cl = a.clips[clip]; avail = int((cl.frame_range[1] - cl.frame_range[0] - start) / speed)
    a.play(clip, frames=min(avail * repeat, f1 - f0 + blend), speed=speed, blend=blend, start=max(0, start), repeat=repeat)


def parabola(z0, z1, T, apex):
    """Parábola de z0 a z1 en T fotogramas con altura máxima `apex`: devuelve z(t) con t en fotogramas (0..T)."""
    d = z1 - z0; h = apex - z0; Ts = T / 24.0
    # (d + g T^2/2)^2 = 2 g h T^2  ->  (T^4/4) g^2 + (d T^2 - 2 h T^2) g + d^2 = 0
    A, B, C = Ts ** 4 / 4.0, d * Ts ** 2 - 2 * h * Ts ** 2, d * d
    disc = max(B * B - 4 * A * C, 0.0)
    best = None
    for g in ((-B - math.sqrt(disc)) / (2 * A), (-B + math.sqrt(disc)) / (2 * A)):      # dos raíces: vale la que sube primero y llega al ápice dentro del vuelo
        if g <= 0: continue
        v = (d + 0.5 * g * Ts ** 2) / Ts
        if v > 0 and v / g <= Ts: best = (g, v)
    g, v = best if best else (2 * h / (Ts / 2) ** 2, 2 * h / (Ts / 2))
    return lambda t: z0 + v * (t / 24.0) - 0.5 * g * (t / 24.0) ** 2


def lerp(a, b, t): return a + (b - a) * t


def trajectory():
    """(x, y, z del pie más bajo, escala z, escala xy) para cada fotograma f=1..F_END."""
    zb, zf = REST, FLOOR + REST
    air = {
        "jump": (F_J0, F_IN_A, XS["tip"], XS["A"], parabola(zb, zf, T_AIR_A, 0.55)),
        "b1": (F_OUT_A, F_IN_B, XS["A"], XS["B"], parabola(zf, zf, T1, APEX[0])),
        "b2": (F_OUT_B, F_IN_C, XS["B"], XS["C"], parabola(zf, zf, T2, APEX[1])),
        "b3": (F_OUT_C, F_LAND, XS["C"], XS["land"], parabola(zf, zb, T3, APEX[2])),
    }
    out = {}
    for f in range(1, F_END + 1):
        x, z = X_START, zb
        if f <= F_WALK: x = lerp(X_START, X_TIP, (f - 1) / float(F_WALK - 1))
        elif f < F_J0: x = X_TIP
        elif f >= F_LAND: x = X_START
        for nm, (fa, fb, xa, xb, zf_) in air.items():
            if fa <= f <= fb:
                t = (f - fa); x = lerp(xa, xb, t / float(fb - fa)); z = zf_(t); break
        else:
            # contactos: el pie sigue la superficie del fondo
            for cin, cout, xc in ((F_IN_A, F_OUT_A, XS["A"]), (F_IN_B, F_OUT_B, XS["B"]), (F_IN_C, F_OUT_C, XS["C"])):
                if cin <= f <= cout: x = xc; z = floor_z(xc, YC, f) + 0.03; break
        # squash & stretch (escala z y xy)
        sz, sxy = 1.0, 1.0
        for cin, cout in ((F_IN_A, F_OUT_A), (F_IN_B, F_OUT_B), (F_IN_C, F_OUT_C)):
            if cin <= f <= cout:
                k = max(0.0, S_OF(f)); sz, sxy = 1 - 0.10 * k, 1 + 0.06 * k
            elif cout < f <= cout + 9:
                k = 1 - (f - cout) / 9.0; sz, sxy = 1 + 0.12 * k, 1 - 0.06 * k
        if F_J0 - 3 <= f < F_J0: sz, sxy = 0.95, 1.03
        if F_J0 <= f <= F_J0 + 4: k = 1 - (f - F_J0) / 4.0; sz, sxy = 1 + 0.08 * k, 1 - 0.04 * k
        if F_LAND <= f <= F_LAND + 6: k = (1 - (f - F_LAND) / 6.0); sz, sxy = 1 - 0.07 * k, 1 + 0.04 * k
        out[f] = (x, YC, z, sz, sxy)
    return out


# ------------------------------------------------------------------ cámara
def cam_set(S, f, loc, tgt, lens):
    S.cam.location = loc; S.cam.keyframe_insert("location", frame=f)
    S.cam.data.lens = lens; S.cam.data.keyframe_insert("lens", frame=f)
    S.tgt.location = tgt; S.tgt.keyframe_insert("location", frame=f)


# cámara del fotograma 1 (se repite idéntica al final: bucle)
CAM1 = ((0.0, -3.3, 2.3), (-2.2, YC, 0.85), 36)


# ------------------------------------------------------------------ la historia
def l1(S):
    build_pool(S)
    a = MixamoActor(S, x=X_START, yaw=90, use=["Walking Left Turn", "Looking Around", "Jumping", "Victory"]); klunk(a)

    # ---- clips ----
    seg(S, a, "Walking Left Turn", 1, F_WALK + 1, start=0, speed=0.6, blend=0)
    seg(S, a, "Looking Around", F_WALK - 2, F_J0 - 1, start=0, blend=4)
    clipf = 37                                                     # fotograma del clip Jumping en el que los pies tocan el suelo
    seg(S, a, "Jumping", F_J0 - 2, F_OUT_A, start=clipf - (F_IN_A - (F_J0 - 2)), blend=4)
    seg(S, a, "Jumping", F_OUT_A, F_OUT_B, start=clipf - (F_IN_B - F_OUT_A), blend=3)
    seg(S, a, "Jumping", F_OUT_B, F_OUT_C, start=clipf - (F_IN_C - F_OUT_B), blend=3)
    seg(S, a, "Jumping", F_OUT_C, F_LAND + 10, start=clipf - (F_LAND - F_OUT_C), blend=3)
    seg(S, a, "Victory", F_LAND + 10, F_END, start=72, blend=4)

    # ---- raíz: posición por fotograma, escala (squash) y suelo ----
    tr = trajectory()
    for f in range(1, F_END + 1):
        x, y, z, sz, sxy = tr[f]
        S.key(a.root, f, loc=(x, y, 0.0), rot=(0, 0, R(90)), scale=(sxy, sxy, sz), interp="LINEAR")
    # pin de los pies: el pie más bajo queda a z objetivo (± 3 cm) en el trampolín, el fondo y todo el vuelo
    rep = []
    for f in range(1, F_END + 1):
        x, y, z, sz, sxy = tr[f]
        fz = foot_z(S, a, f)
        S.key(a.root, f, loc=(x, y, z - fz), rot=(0, 0, R(90)), scale=(sxy, sxy, sz), interp="LINEAR")
        rep.append((f, round(z, 3)))
    S._traj = tr

    # ---- fondo: hundimiento (shape key) + sonido ----
    bpy.context.preferences.edit.keyframe_new_interpolation_type = "LINEAR"
    for f in range(1, F_END + 20):
        S.dip.value = S_OF(f); S.dip.keyframe_insert("value", frame=f)
    S.sc.frame_end = F_END + 10

    # ---- sonido ----
    for k, f in enumerate(range(3, F_WALK - 6, 12)): S.cue("step", f, vol=-12)       # pasos sobre la tabla
    S.cue("huh", 74, vol=-6)
    S.cue("hmm", 92, vol=-8)
    S.cue("whoosh", F_J0 - 1, vol=-8); S.cue("clunk", F_J0, vol=-12)                       # salto
    S.cue("creak", F_IN_A + 2, vol=-9); S.cue("hit", F_IN_A, vol=-9)                       # el fondo cede
    S.cue("huh", F_OUT_A - 2, vol=-6)                                                      # sorpresa al primer rebote
    S.cue("boing", F_IN_A + SINK_A + HOLD_A, vol=-4); S.cue("whoosh", F_OUT_A, vol=-8)
    S.cue("boing_hi", F_IN_B + 2, vol=-4); S.cue("whoosh", F_OUT_B, vol=-8)
    S.cue("boing_top", F_IN_C + 2, vol=-3); S.cue("whoosh", F_OUT_C, vol=-8)
    S.cue("clunk", F_LAND, vol=-5); S.cue("hit", F_LAND, vol=-12)
    S.cue("yay", F_LAND + 3, vol=-5); S.cue("tada", F_LAND + 6, vol=-12)

    # ---- cara: parpadeos, ojos cerrados al saltar y expresiones ----
    lids = a.toon["parpados"]
    expression(a, "neutra", 1, 1.0, ramp=2)
    for f in (14, 40, 66):
        blink(a, f)
    expression(a, "sorpresa", 70, 0.5, ramp=4)                                              # huh: mira dentro
    expression(a, "neutra", 88, 1.0, ramp=4)                                                # hmm
    # ojos bien cerrados desde antes de saltar hasta el momento hundido
    r0 = [L.rotation_euler.x for L in lids]
    for L, r in zip(lids, r0):
        for f, v in ((F_J0 - 14, r), (F_J0 - 11, R(62)), (F_IN_A + SINK_A + 3, R(62)), (F_IN_A + SINK_A + 6, r)):
            L.rotation_euler.x = v; L.keyframe_insert("rotation_euler", frame=f)
    expression(a, "enfado", F_J0 - 10, 0.5, ramp=4)                                         # tensión: aprieta los párpados
    expression(a, "sorpresa", F_IN_A + SINK_A + 6, 0.6, ramp=3)                             # abre los ojos: el fondo está hundido
    expression(a, "sorpresa", F_OUT_A - 3, 1.0, ramp=3)                                     # ¡rebota! sorpresa
    expression(a, "feliz", F_IN_B + 2, 0.7, ramp=4)
    expression(a, "feliz", F_IN_C + 2, 1.0, ramp=4)
    expression(a, "feliz", F_LAND + 2, 1.0, ramp=3)
    expression(a, "neutra", F_END - 24, 1.0, ramp=10)                                       # vuelve a la cara del plano 1
    for f in (F_IN_B + 10, F_LAND + 20, F_END - 14): blink(a, f)

    # ---- cámara: cortes de 1-2 s (CONSTANT); la del plano final repite exactamente la del fotograma 1 ----
    cam = []
    def shot(f0, f1, fn):
        for f in range(f0, f1 + 1):
            loc, tg, lens = fn(f); cam.append((f, loc, tg, lens))
    def at_head(dx, dy, dz, lens, tdz=0.0, tdx=0.0):
        return lambda f: ((lambda hp: ((hp.x + dx, hp.y + dy, hp.z + dz), (hp.x + tdx, hp.y, hp.z + tdz), lens))(head_pos(S, a, f)))
    c1 = lambda f: CAM1
    def fixed_track(loc, lens, dz=-0.3, dx=0.0):                    # cámara fija que gira para seguir la cabeza (el cuadro no se sale en los botes)
        return lambda f: (loc, (lambda hp: (hp.x + dx, hp.y, hp.z + dz))(head_pos(S, a, f)), lens)
    shot(1, 34, c1)                                                                         # 1 general: sube andando al trampolín
    shot(35, 58, lambda f: ((-0.3, -3.6, 1.1), (X_TIP - 0.4, YC, 0.8), 30))                 # 2 medio: llega a la punta
    shot(59, 82, at_head(2.0, -1.3, 0.05, 36, -0.1))                                     # 3 primer plano: mira abajo (huh)
    shot(83, F_J0 - 11, lambda f: ((X_START - 1.2, YC - 0.5, 3.0), (0.0, YC, 0.6), 30))                   # 4 sobre su hombro: la piscina vacía (hmm)
    shot(F_J0 - 10, F_IN_A - 1, at_head(1.8, -2.6, 0.3, 32, -0.35))               # 5 salto y caída
    shot(F_IN_A, F_IN_A + SINK_A + 5, fixed_track((3.2, -2.4, 0.9), 30, -0.45))     # 6 el fondo se hunde bajo él
    shot(F_IN_A + SINK_A + 6, F_OUT_A + 3, at_head(1.9, -2.4, 0.5, 32, -0.55))             # 7 pausa y primer boing: cara
    shot(F_OUT_A + 4, F_IN_B - 1, at_head(2.3, -3.6, -0.6, 32, 0.0))                        # 8 primer bote
    shot(F_IN_B, F_OUT_B + 2, fixed_track((3.6, -3.4, 0.9), 30, -0.4))            # 9 segundo contacto
    shot(F_OUT_B + 3, F_IN_C - 1, at_head(2.6, -3.9, -0.4, 30, 0.0))                        # 10 segundo bote
    shot(F_IN_C, F_OUT_C + 2, at_head(1.9, -2.3, 0.2, 34, -0.55))                            # 11 tercer contacto: cara
    shot(F_OUT_C + 3, F_LAND, at_head(2.4, -4.2, -0.5, 30, 0.0, -0.4))                  # 12 tercer bote hacia el trampolín
    shot(F_LAND + 1, F_END + 10, c1)                                                        # 13 encuadre del fotograma 1: bucle
    for f, loc, tg, lens in cam: cam_set(S, f, loc, tg, lens)
    S.set_interp(S.cam, "CONSTANT", ("location",)); S.set_interp(S.cam.data, "CONSTANT"); S.set_interp(S.tgt, "CONSTANT")
    S.f = F_END
    a.verify(S.f)
    return a


LEVELS = [(0, l1)]
