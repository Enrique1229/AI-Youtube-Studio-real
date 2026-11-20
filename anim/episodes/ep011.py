"""ep011 — Cada nivel de IQ llega a la manta de picnic. Parque (realista, personaje humano de Mixamo).
Charco de barro entre la orilla del hombre (izquierda) y la manta (derecha). Banco de madera a la izquierda.
-450 salta corriendo y cae a mitad del charco (barro hasta las rodillas); -80 lanza tres piedras que se hunden sin ruido;
120 empuja el banco al barro, se sienta en el respaldo y se hunde con él; 900 salta, cae en el borde de la manta, ésta resbala
y lo lleva de culo al barro; 5469 piensa, agarra la esquina doblada, tira y la manta cruza deslizándose por ENCIMA del barro.
La esquina doblada y la cesta se ven desde el fotograma 1 en todos los niveles."""
import math
import random
import bmesh
import bpy
from mathutils import Vector, noise
from mixamo import MixamoActor

TITLE = "Every IQ Level Reaches the Picnic Blanket"
ONSCREEN = "Every IQ level reaches the picnic blanket"
ENV = "parque"
CUSTOM_CAMERA = True
LABEL_STYLE = "big"

# geometría (metros). El hombre viene de la izquierda; y = 0 es la línea de la manta.
PCX, PCY, PRX, PRY = -7.28, 0.35, 0.55, 1.30      # charco: elipse (centro y semiejes)
BL_XR = -5.75                                     # borde lejano (derecho) de la manta
BL_L, BL_W, BL_T = 1.0, 1.0, 0.03                 # largo (x), ancho (y), grosor
TAB_L, TAB_W, TAB_A = 0.65, 0.36, 30.0            # esquina doblada: largo, ancho, ángulo de levantamiento
TAB_Y = -0.32
BEN_X = -8.35                                     # centro del banco (largo en x, de cara a la cámara)
BEN_Y = 0.95
YA = -0.15                                        # línea del actor en los niveles 1, 2 y 4


def R(d): return math.radians(d)


# ------------------------------------------------------------------ materiales y utilidades
def mmat(S, name, rgb, rough=0.5, metal=0.0, emit=None):
    k = "m_" + name
    if k in S.mats: return S.mats[k]
    m = bpy.data.materials.new(k); m.use_nodes = True
    b = m.node_tree.nodes["Principled BSDF"]
    b.inputs["Base Color"].default_value = (*rgb, 1); b.inputs["Roughness"].default_value = rough; b.inputs["Metallic"].default_value = metal
    if emit:
        b.inputs["Emission Color"].default_value = (*emit, 1); b.inputs["Emission Strength"].default_value = 3.0
    S.mats[k] = m
    return m


def mud_mat(S):
    """Barro mojado: marrón muy oscuro con variación, brillo húmedo irregular (rugosidad baja + capa clara) y relieve."""
    if "barro_ep011" in S.mats: return S.mats["barro_ep011"]
    m = bpy.data.materials.new("barro"); m.use_nodes = True; nt = m.node_tree; N = nt.nodes; L = nt.links
    b = N["Principled BSDF"]
    tc = N.new("ShaderNodeTexCoord")
    n1 = N.new("ShaderNodeTexNoise"); n1.inputs["Scale"].default_value = 4.0; n1.inputs["Detail"].default_value = 8.0
    n2 = N.new("ShaderNodeTexNoise"); n2.inputs["Scale"].default_value = 26.0; n2.inputs["Detail"].default_value = 10.0
    L.new(tc.outputs["Object"], n1.inputs["Vector"]); L.new(tc.outputs["Object"], n2.inputs["Vector"])
    cr = N.new("ShaderNodeValToRGB"); e = cr.color_ramp.elements
    e[0].position, e[0].color = 0.30, (0.030, 0.017, 0.008, 1); e[1].position, e[1].color = 0.70, (0.105, 0.060, 0.030, 1)
    L.new(n1.outputs["Fac"], cr.inputs["Fac"]); L.new(cr.outputs["Color"], b.inputs["Base Color"])
    rr = N.new("ShaderNodeMapRange"); rr.inputs["From Min"].default_value = 0.35; rr.inputs["From Max"].default_value = 0.65
    rr.inputs["To Min"].default_value = 0.04; rr.inputs["To Max"].default_value = 0.35
    L.new(n1.outputs["Fac"], rr.inputs["Value"]); L.new(rr.outputs["Result"], b.inputs["Roughness"])
    mix = N.new("ShaderNodeMath"); mix.operation = "ADD"; mix.inputs[1].default_value = 0.0
    L.new(n2.outputs["Fac"], mix.inputs[0])
    bp = N.new("ShaderNodeBump"); bp.inputs["Strength"].default_value = 1.4; bp.inputs["Distance"].default_value = 0.08
    L.new(mix.outputs["Value"], bp.inputs["Height"]); L.new(bp.outputs["Normal"], b.inputs["Normal"])
    for k, v in (("Coat Weight", 0.7), ("Coat Roughness", 0.04), ("Specular IOR Level", 0.7)):
        if k in b.inputs: b.inputs[k].default_value = v
    S.mats["barro_ep011"] = m
    return m


def checker_mat(S):
    """Manta de cuadros rojos y blancos (cuadros de ~12 cm) con trama de tela."""
    if "manta_ep011" in S.mats: return S.mats["manta_ep011"]
    m = bpy.data.materials.new("manta"); m.use_nodes = True; nt = m.node_tree; N = nt.nodes; L = nt.links
    b = N["Principled BSDF"]; b.inputs["Roughness"].default_value = 0.85
    tc = N.new("ShaderNodeTexCoord"); ck = N.new("ShaderNodeTexChecker"); ck.inputs["Scale"].default_value = 4.0
    ck.inputs["Color1"].default_value = (0.60, 0.025, 0.03, 1); ck.inputs["Color2"].default_value = (0.92, 0.90, 0.84, 1)
    L.new(tc.outputs["Object"], ck.inputs["Vector"]); L.new(ck.outputs["Color"], b.inputs["Base Color"])
    nz = N.new("ShaderNodeTexNoise"); nz.inputs["Scale"].default_value = 300.0
    L.new(tc.outputs["Object"], nz.inputs["Vector"])
    bp = N.new("ShaderNodeBump"); bp.inputs["Strength"].default_value = 0.15
    L.new(nz.outputs["Fac"], bp.inputs["Height"]); L.new(bp.outputs["Normal"], b.inputs["Normal"])
    S.mats["manta_ep011"] = m
    return m


def wood_mat(S):
    """Madera real (Poly Haven brown_planks_03) con coordenadas de objeto: la veta tiene tamaño real en cada tabla."""
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
    """Caja con dimensiones reales (escala aplicada: las coordenadas de objeto de los materiales son metros)."""
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


def cam_static(S, cx=-7.70, lens=30, dist=4.7, ch=2.0, tz=0.75):
    S.cam.location = (cx, -dist, ch); S.cam.data.lens = lens; S.tgt.location = (cx, 0, tz)
    S.cam.keyframe_insert("location", frame=1); S.cam.data.keyframe_insert("lens", frame=1); S.tgt.keyframe_insert("location", frame=1)


def place(S, a, f, x, y, z=0.0, yaw=90.0, pitch=0.0, interp="BEZIER"):
    S.key(a.root, f, loc=(x, y, z), rot=(R(pitch), 0, R(yaw)), interp=interp)


def seg(S, a, clip, f0, f1=None, start=0, speed=1.0, blend=4, repeat=1):
    S.f = f0
    cl = a.clips[clip]; avail = int((cl.frame_range[1] - cl.frame_range[0] - start) / speed)
    a.play(clip, frames=(min(avail * repeat, f1 - f0 + blend) if f1 is not None else None), speed=speed, blend=blend, start=start, repeat=repeat)


def foot_lift(S, a, f):
    """Altura de los pies del clip en el fotograma f (raíz sin animar): el mínimo de ambos pies, sin el apoyo en el suelo."""
    z = min(bone_pos(S, a, "RightFoot", f, 0.6).z, bone_pos(S, a, "LeftFoot", f, 0.6).z)
    return z


# ------------------------------------------------------------------ barro: salpicaduras, ondas, grumos
def mud_splash(S, x, y, f, n=12, size=0.045, up=1.6, spread=0.5, seed=0):
    """Gotas de barro en arco parabólico (LINEAR cada 2 fotogramas). Caen sobre la superficie del charco (z ≈ 0.03)."""
    rr = random.Random(seed + int(x * 10) + f); m = mud_mat(S)
    for i in range(n):
        d = S.obj("uv_sphere", "gota_barro", "white", (x, y, 0.05), (0.001,) * 3, segments=8, ring_count=6); d.data.materials[0] = m
        ang = rr.uniform(0, 2 * math.pi); sp = rr.uniform(0.2, spread); vz = rr.uniform(0.6, 1.0) * up
        vx, vy = math.cos(ang) * sp, math.sin(ang) * sp * 0.6
        sz = size * rr.uniform(0.6, 1.3); T = 2 * vz / 9.8 * 0.9
        nf = max(4, int(T * 24))
        S.key(d, f - 1, loc=(x, y, 0.05), scale=(0.001,) * 3, interp="LINEAR")
        for k in range(0, nf + 1, 2):
            t = k / 24.0; z = 0.05 + vz * t - 4.9 * t * t * 0.9
            if z < 0.03 and k > 0:
                S.key(d, f + k, loc=(x + vx * t, y + vy * t, 0.03), scale=(sz, sz, sz * 0.5), interp="LINEAR")
                S.key(d, f + k + 3, loc=(x + vx * t, y + vy * t, 0.0), scale=(0.001,) * 3, interp="LINEAR"); break
            S.key(d, f + k, loc=(x + vx * t, y + vy * t, z), scale=(sz, sz, sz * (1.2 if k < nf * 0.5 else 0.9)), interp="LINEAR")


def ripple(S, x, y, f, r1=0.5, delay=0, life=22):
    """Onda sencilla: aro bajo que se expande sobre la superficie del barro y se desvanece (encoge su sección)."""
    m = mud_mat(S)
    o = S.obj("torus", "onda_barro", "white", (x, y, 0.03), (0.001,) * 3, major_radius=1.0, minor_radius=0.03, major_segments=40, minor_segments=8)
    o.data.materials[0] = m; g = f + delay
    S.key(o, g - 1, loc=(x, y, 0.03), scale=(0.001,) * 3, interp="LINEAR")
    S.key(o, g, loc=(x, y, 0.025), scale=(0.08, 0.08, 0.25), interp="LINEAR")
    S.key(o, g + life // 2, loc=(x, y, 0.025), scale=(r1 * 0.7, r1 * 0.7, 0.25), interp="LINEAR")
    S.key(o, g + life, loc=(x, y, 0.025), scale=(r1, r1, 0.001), interp="LINEAR")


def lumps(S, x, y, f, n=6, r=0.17, seed=1, size=0.07):
    """Grumos de barro que se abomban alrededor del punto de impacto (donde se hunde algo)."""
    rr = random.Random(seed + f); m = mud_mat(S)
    for i in range(n):
        a_ = 2 * math.pi * i / n + rr.uniform(-0.3, 0.3); rad = r * rr.uniform(0.8, 1.25); s = size * rr.uniform(0.7, 1.2)
        o = S.obj("uv_sphere", "grumo", "white", (x + math.cos(a_) * rad, y + math.sin(a_) * rad * 0.8, 0.03), (0.001,) * 3, segments=10, ring_count=6)
        o.data.materials[0] = m
        S.key(o, f - 1, scale=(0.001,) * 3); S.key(o, f + 5, scale=(s * 1.4, s * 1.4, s * 0.55)); S.key(o, f + 14, scale=(s * 1.2, s * 1.2, s * 0.45))


# ------------------------------------------------------------------ escenario
class W: pass


def disc_mesh(S, name, mat, cx, cy, rx, ry, z=0.012, seed=3):
    """Charco: disco elíptico triangulado y subdividido, con relieve (ruido), borde que se funde con el suelo y labio de barro."""
    me = bpy.data.meshes.new(name); bm = bmesh.new()
    bmesh.ops.create_circle(bm, cap_ends=True, cap_tris=True, segments=72, radius=1.0)
    bmesh.ops.subdivide_edges(bm, edges=bm.edges[:], cuts=5, use_grid_fill=True)
    bmesh.ops.triangulate(bm, faces=bm.faces[:])
    for v in bm.verts:
        r = min(1.0, math.hypot(v.co.x, v.co.y)); ox, oy = v.co.x * rx, v.co.y * ry
        n1 = noise.noise(Vector((ox * 2.2 + seed, oy * 2.2, 0.0))); n2 = noise.noise(Vector((ox * 7 + seed, oy * 7, 1.0)))
        edge = 1.0 - max(0.0, (r - 0.82) / 0.18)                         # 1 en el centro, 0 en el borde
        rim = math.exp(-((r - 0.93) / 0.05) ** 2) * 0.020                 # labio
        v.co.x = ox; v.co.y = oy; v.co.z = 0.006 + (z - 0.006) * min(1.0, edge * 1.6) + (0.010 * n1 + 0.004 * n2) * edge + rim
    bm.to_mesh(me); bm.free()
    for p in me.polygons: p.use_smooth = True
    o = bpy.data.objects.new(name, me); S.sc.collection.objects.link(o); o.location = (cx, cy, 0); o.data.materials.append(mat)
    return o


def clear_env(S):
    """Quita hierba, rocas y troncos de la zona de juego y del primer plano, y TAPA el río (hierba en su lugar): no se ve agua."""
    for o in list(S.sc.objects):
        if o.instance_type == "COLLECTION" and -14.0 < o.location.x < -3.0 and -8.0 < o.location.y < 9.0:
            keep = "grass" in o.name and o.location.y > 4.5
            if not keep: bpy.data.objects.remove(o, do_unlink=True)
    ref = bpy.data.objects.get("orillaL")
    if getattr(S, "water", None): S.water.hide_render = True; S.water.hide_viewport = True
    dock = bpy.data.objects.get("muelle")
    if dock: dock.hide_render = True
    bpy.ops.mesh.primitive_plane_add(size=1, location=(0, 0, -0.002)); g = bpy.context.object; g.name = "suelo_rio"
    g.scale = (6.0, 400.0, 1.0)
    if ref is not None and ref.type == "MESH" and ref.data.materials: g.data.materials.append(ref.data.materials[0])


def build_set(S, bench=True):
    w = W(); clear_env(S)
    w.mud = disc_mesh(S, "charco", mud_mat(S), PCX, PCY, PRX, PRY)
    # manta (origen = centro del borde lejano; local x negativo hacia el hombre), con esquina doblada levantada hacia el charco
    chk = checker_mat(S)
    w.bl = S.empty("manta", (BL_XR, 0, 0))
    box(S, "manta_cuerpo", chk, (BL_L, BL_W, BL_T), (-BL_L / 2, 0, BL_T / 2), parent=w.bl)
    w.tab = S.empty("esquina", (-BL_L, TAB_Y, BL_T), parent=w.bl)
    box(S, "esquina_doblada", chk, (TAB_L, TAB_W, 0.022), (-TAB_L / 2, 0, 0.011), parent=w.tab)
    w.tab.rotation_euler = (0, R(TAB_A), 0)
    S.key(w.tab, 1, rot=(0, R(TAB_A), 0)); S.key(w.bl, 1, loc=(BL_XR, 0, 0), rot=(0, 0, 0))
    # cesta de picnic (mimbre) con asa, en la mitad trasera de la manta
    wick = mmat(S, "mimbre", (0.42, 0.26, 0.10), rough=0.8)
    nzt = wick.node_tree; bp = nzt.nodes.new("ShaderNodeBump"); nn = nzt.nodes.new("ShaderNodeTexNoise"); nn.inputs["Scale"].default_value = 120
    nzt.links.new(nn.outputs["Fac"], bp.inputs["Height"]); nzt.links.new(bp.outputs["Normal"], nzt.nodes["Principled BSDF"].inputs["Normal"])
    cloth = mmat(S, "pano_cesta", (0.85, 0.82, 0.74), rough=0.9)
    w.basket = S.empty("cesta", (-0.28, 0.33, BL_T), parent=w.bl)
    box(S, "cesta_cuerpo", wick, (0.34, 0.24, 0.17), (0, 0, 0.085), parent=w.basket)
    box(S, "cesta_tapa", wick, (0.36, 0.26, 0.025), (0, 0, 0.19), parent=w.basket)
    box(S, "cesta_pano", cloth, (0.20, 0.10, 0.03), (0.05, 0.0, 0.215), parent=w.basket, rot=(0, 0, R(12)))
    O(S, "torus", "cesta_asa", wick, (0, 0, 0.19), (1, 1, 1), (math.pi / 2, 0, 0), w.basket, major_radius=0.13, minor_radius=0.014, major_segments=24, minor_segments=8)
    # banco de madera de parque (largo en x, de cara a la cámara: asiento delante, respaldo detrás en y = +0.22)
    w.bench = S.empty("banco", (BEN_X, BEN_Y, 0))
    wood = wood_mat(S); iron = mmat(S, "hierro_banco", (0.05, 0.05, 0.055), rough=0.5, metal=0.9)
    box(S, "asiento", wood, (1.00, 0.44, 0.04), (0, 0.0, 0.44), parent=w.bench)
    for dz, hh in ((0.62, 0.11), (0.77, 0.11)):
        box(S, "respaldo", wood, (1.00, 0.035, hh), (0, 0.22, dz + hh / 2), parent=w.bench)
    for xx in (-0.46, 0.46):
        box(S, "pata_tras", iron, (0.05, 0.05, 0.90), (xx, 0.22, 0.45), parent=w.bench)
        box(S, "pata_del", iron, (0.05, 0.05, 0.44), (xx, -0.22, 0.22), parent=w.bench)
        box(S, "brazo", iron, (0.045, 0.50, 0.04), (xx + (0.04 if xx > 0 else -0.04), 0.0, 0.62), parent=w.bench)
    S.key(w.bench, 1, loc=(BEN_X, BEN_Y, 0), rot=(0, 0, 0))
    return w


def tab_tip(rot_deg=TAB_A):
    """Punta de la esquina doblada (mundo) con la manta en reposo."""
    return Vector((BL_XR - BL_L - TAB_L * math.cos(R(rot_deg)), TAB_Y, BL_T + TAB_L * math.sin(R(rot_deg))))


# ------------------------------------------------------------------ nivel -450
def l1(S):
    """-450: ya corriendo en el fotograma 1; salta con los brazos abiertos, se queda corto y se hunde hasta las rodillas."""
    w = build_set(S); cam_static(S)
    a = MixamoActor(S, x=-9.35, yaw=90, use=["Running", "Jumping", "Looking Around"])
    f_run, f_jump = 1, 13
    seg(S, a, "Running", f_run, f_jump, start=0, repeat=2, blend=3)
    sp = 1.25; j0 = 6                                               # fotograma del clip Jumping al despegar
    seg(S, a, "Jumping", f_jump, 52, start=j0, speed=sp, blend=4)
    seg(S, a, "Looking Around", 50, None, start=0, blend=6)
    f_land = int(f_jump + (43 - j0) / sp)                           # aterriza (clip 43)
    x_t, x_l = -8.40, -7.30
    # altura de los pies del clip: se compensa para que la trayectoria sea la deseada (arco de ~0.45 m)
    base = foot_lift(S, a, f_land + 3)
    place(S, a, 1, -9.35, YA, 0, 90, interp="LINEAR"); place(S, a, f_jump, x_t, YA, 0, 90, interp="LINEAR")
    for f in range(f_jump + 1, f_land + 1):
        t = (f - f_jump) / float(f_land - f_jump)
        want = 0.5 * math.sin(math.pi * t) ** 0.9
        zz = want - (foot_lift(S, a, f) - base)
        place(S, a, f, x_t + (x_l - x_t) * (1 - (1 - t) ** 1.4), YA, max(zz, -1.2) if t < 1 else 0.0, 90, interp="LINEAR")
    # al caer se hunde hasta las rodillas (~0.5 m): rápido y con rebote
    for f, z in ((f_land + 2, -0.12), (f_land + 5, -0.38), (f_land + 8, -0.50), (f_land + 14, -0.47), (f_land + 20, -0.52)):
        place(S, a, f, x_l, YA, z, 90)
    S.cue("boing", f_jump + 3, vol=-6); S.cue("splash", f_land, vol=-6); S.cue("drain", f_land + 3, vol=-9); S.cue("hit", f_land, vol=-11)
    mud_splash(S, x_l, YA, f_land + 1, n=16, size=0.05, up=1.9, spread=0.7)
    mud_splash(S, x_l, YA, f_land + 4, n=8, size=0.04, up=1.2, spread=0.5, seed=5)
    lumps(S, x_l, YA, f_land + 4, n=7, r=0.20)
    ripple(S, x_l, YA, f_land + 2, r1=0.50); ripple(S, x_l, YA, f_land + 2, r1=0.38, delay=6)
    S.f = 128
    a.verify(S.f)
    return a


# ------------------------------------------------------------------ nivel -80
def l2(S):
    """-80: lanza tres piedras (Throw) para hacer pasarela; cada una se hunde sin ruido; se queda mirando el barro, enfadado."""
    w = build_set(S); cam_static(S)
    xc = -8.55
    a = MixamoActor(S, x=xc, yaw=90, use=["Throw", "Angry"])
    place(S, a, 1, xc, YA, 0, 90)
    seg(S, a, "Throw", 1, 33, start=0)
    seg(S, a, "Throw", 31, 60, start=8)
    seg(S, a, "Throw", 58, 88, start=8)
    seg(S, a, "Angry", 86, None, start=0, blend=6)
    stone = mmat(S, "piedra", (0.30, 0.28, 0.25), rough=0.9)
    for (f_rel, xt, seed) in ((20, -7.45, 1), (43, -7.28, 2), (70, -7.12, 3)):
        st = S.obj("uv_sphere", "piedra", "white", (0, 0, -9), (0.085, 0.07, 0.065), segments=12, ring_count=8); st.data.materials[0] = stone
        f0 = f_rel - 13
        S.key(st, f0 - 1, loc=(0, 0, -9), scale=(0.001,) * 3, interp="LINEAR")
        for f in range(f0, f_rel + 1):                              # va en la mano hasta soltarla
            p = bone_pos(S, a, "RightHand", f, 0.8)
            S.key(st, f, loc=(p.x, p.y, p.z), scale=(0.085, 0.07, 0.065), interp="LINEAR")
        p0 = bone_pos(S, a, "RightHand", f_rel, 0.8); T = 15
        for k in range(1, T + 1):                                   # vuelo parabólico hasta la superficie del barro
            t = k / float(T)
            x = p0.x + (xt - p0.x) * t; y = p0.y + (YA - p0.y) * t
            z = p0.z + (0.07 - p0.z) * t + 0.75 * 4 * t * (1 - t)
            S.key(st, f_rel + k, loc=(x, y, z), rot=(0.5 * k, 0.3 * k, 0), interp="LINEAR")
        fa = f_rel + T
        for k, z in ((2, 0.03), (5, -0.03), (9, -0.09), (14, -0.16)):   # se hunde en el barro, sin ruido
            S.key(st, fa + k, loc=(xt, YA, z), interp="BEZIER")
        S.key(st, fa + 15, loc=(xt, YA, -0.30), scale=(0.085, 0.07, 0.065), interp="LINEAR")
        mud_splash(S, xt, YA, fa, n=5, size=0.03, up=0.9, spread=0.28, seed=seed)
        lumps(S, xt, YA, fa + 2, n=5, r=0.11, size=0.045, seed=seed)
        ripple(S, xt, YA, fa, r1=0.26); ripple(S, xt, YA, fa, r1=0.18, delay=5)
        S.cue("whoosh", f_rel - 2, vol=-11)                         # la piedra no suena al caer: es el chiste
    S.f = 136
    a.verify(S.f)
    return a


# ------------------------------------------------------------------ nivel 120
def l3(S):
    """120: empuja el banco al barro (Pushing); se hunde hasta que solo asoma el respaldo; se sienta en la barra del respaldo,
    de cara a cámara, con cara de gran idea (bombilla) y se hunde despacio con él."""
    w = build_set(S); cam_static(S)
    HX = 0.5 + 0.80                                                 # raíz -> centro del banco (extremo del banco + alcance de las manos)
    r0 = BEN_X - HX
    a = MixamoActor(S, x=r0, yaw=90, use=["Pushing", "Jumping", "Sitting Idle"])
    f_p = 56
    seg(S, a, "Pushing", 1, f_p - 4, start=0, blend=4)
    seg(S, a, "Jumping", f_p - 4, f_p + 8, start=14, speed=2.0, blend=3)           # salto de un solo impulso hasta el banco
    seg(S, a, "Sitting Idle", f_p + 6, None, start=0, blend=5)
    base = foot_lift(S, a, 1)
    lift = {f: foot_lift(S, a, f) - base for f in range(f_p - 3, f_p + 8)}
    bx1 = -7.30                                                     # centro del banco al terminar
    r1 = bx1 - HX
    place(S, a, 1, r0, BEN_Y, 0, 90, interp="LINEAR"); place(S, a, f_p - 6, r1, BEN_Y, 0, 90, interp="LINEAR")
    S.key(w.bench, 1, loc=(BEN_X, BEN_Y, 0), rot=(0, 0, 0), interp="LINEAR")
    x_edge = -7.77
    f_in = 1
    for f in range(2, f_p - 5):
        t = (f - 1) / float(f_p - 7); bx = BEN_X + (bx1 - BEN_X) * t
        d = max(0.0, bx + 0.5 - x_edge)                             # cuánto ha entrado el extremo delantero en el barro
        sink = min(0.45, d * 0.9); pitch = min(12.0, d * 20.0)
        if d > 0.12 and f_in == 1: f_in = f
        S.key(w.bench, f, loc=(bx, BEN_Y, -sink), rot=(0, R(pitch), 0), interp="LINEAR")
    S.cue("slide_down", 4, vol=-14); S.cue("slide_down", 20, vol=-14); S.cue("splash", f_in + 1, vol=-8); S.cue("drain", f_in + 8, vol=-8)
    mud_splash(S, x_edge + 0.2, BEN_Y - 0.1, f_in + 2, n=10, size=0.04, up=1.2, spread=0.5)
    lumps(S, x_edge + 0.25, BEN_Y - 0.1, f_in + 6, n=7, r=0.34, size=0.07)
    ripple(S, bx1, BEN_Y - 0.2, f_in + 14, r1=0.60); ripple(S, bx1, BEN_Y - 0.2, f_in + 14, r1=0.42, delay=7)
    S.key(w.bench, f_p - 4, loc=(bx1, BEN_Y, -0.45), rot=(0, R(12), 0), interp="LINEAR")
    # salta sobre la barra del respaldo (de cara a cámara) y se hunde despacio con el banco
    ys = BEN_Y + 0.22; zs = -0.05
    place(S, a, f_p - 4, r1, BEN_Y, 0, 90, interp="LINEAR")
    for f in range(f_p - 3, f_p + 8):
        t = (f - (f_p - 4)) / 12.0
        zz = 0.45 * math.sin(math.pi * t) - lift[f]
        place(S, a, f, r1 + (bx1 - r1) * t, BEN_Y + (ys - BEN_Y) * t, max(zz, -1.2), 90 * (1 - t), interp="LINEAR")
    place(S, a, f_p + 8, bx1, ys, zs, 0)
    for f in range(f_p + 9, 142, 3):
        t = (f - f_p - 8) / 60.0
        place(S, a, f, bx1, ys, zs - 0.20 * min(1.0, t), 0, interp="LINEAR")
        S.key(w.bench, f, loc=(bx1, BEN_Y, -0.45 - 0.20 * min(1.0, t)), rot=(0, R(8), 0), interp="LINEAR")
    S.cue("pop", f_p + 5, vol=-9); S.cue("clunk", f_p + 8, vol=-8)
    for f in (f_p + 28, f_p + 48):
        S.cue("drain", f, vol=-12)
        ripple(S, bx1, ys - 0.5, f - 6, r1=0.5)
    ripple(S, bx1, ys - 0.4, f_p + 10, r1=0.55)
    # bombilla de «gran idea» sobre la cabeza
    hp = head_pos(S, a, f_p + 22)
    gl = mmat(S, "bombilla", (1.0, 0.92, 0.45), rough=0.2, emit=(1.0, 0.85, 0.25))
    bu = S.obj("uv_sphere", "bombilla", "white", (hp.x, hp.y, hp.z + 0.34), (0.001,) * 3, segments=14, ring_count=8); bu.data.materials[0] = gl
    ba = S.obj("cylinder", "casquillo", "white", (hp.x, hp.y, hp.z + 0.26), (0.001,) * 3, vertices=10); ba.data.materials[0] = mmat(S, "casquillo", (0.5, 0.5, 0.5), rough=0.4, metal=0.8)
    fb = f_p + 20
    S.key(bu, fb - 1, scale=(0.001,) * 3); S.key(bu, fb + 3, loc=(hp.x, hp.y, hp.z + 0.12), scale=(0.075, 0.075, 0.09)); S.key(bu, fb + 30, scale=(0.075, 0.075, 0.09)); S.key(bu, fb + 33, scale=(0.001,) * 3)
    S.key(ba, fb - 1, scale=(0.001,) * 3); S.key(ba, fb + 3, loc=(hp.x, hp.y, hp.z + 0.045), scale=(0.035, 0.035, 0.03)); S.key(ba, fb + 30, scale=(0.035, 0.035, 0.03)); S.key(ba, fb + 33, scale=(0.001,) * 3)
    S.cue("pop", fb, vol=-8)
    S.f = 142
    a.verify(S.f)
    return a


# ------------------------------------------------------------------ nivel 900
def l4(S):
    """900: carrerilla, salto y cae en el borde de la manta; ésta resbala bajo sus pies y lo lleva de culo al charco, manta incluida."""
    w = build_set(S); cam_static(S)
    ya = YA + 0.05
    a = MixamoActor(S, x=-9.35, yaw=90, use=["Running", "Jumping", "Falling Back Death"])
    f_jump = 13; sp = 1.25; j0 = 6
    seg(S, a, "Running", 1, f_jump, start=0, repeat=2, blend=3)
    seg(S, a, "Jumping", f_jump, 46, start=j0, speed=sp, blend=4)
    f_land = int(f_jump + (43 - j0) / sp)
    f_fall = f_land + 6
    seg(S, a, "Falling Back Death", f_fall, None, start=0, blend=4)
    x_t, x_l = -8.45, -6.50
    base = foot_lift(S, a, f_land + 3)
    place(S, a, 1, -9.35, ya, 0, 90, interp="LINEAR"); place(S, a, f_jump, x_t, ya, 0, 90, interp="LINEAR")
    for f in range(f_jump + 1, f_land + 1):
        t = (f - f_jump) / float(f_land - f_jump)
        want = 0.45 * math.sin(math.pi * t) ** 0.9 + BL_T * t
        zz = want - (foot_lift(S, a, f) - base)
        place(S, a, f, x_t + (x_l - x_t) * (1 - (1 - t) ** 1.3), ya, max(zz, -1.2) if t < 1 else BL_T, 90, interp="LINEAR")
    # la manta resbala hacia el charco desde que pisa (acelera), llevándoselo encima; luego se asienta sobre el barro
    sl = [(f_land, 0.0), (f_land + 3, -0.02), (f_land + 6, -0.10), (f_land + 9, -0.28), (f_land + 12, -0.52), (f_land + 15, -0.76), (f_land + 18, -0.93), (f_land + 21, -1.02), (f_land + 26, -1.06)]
    for f, dx in sl:
        S.key(w.bl, f, loc=(BL_XR + dx, 0, 0.03 if dx < -0.01 else 0.0), rot=(0, 0, 0), interp="BEZIER")
        place(S, a, f, x_l + dx, ya, BL_T + (0.03 if dx < -0.01 else 0.0), 90)
    # termina de caer de espaldas: cadera hundida unos centímetros en el barro, manta apoyada encima
    xf = x_l - 1.06
    for f, z in ((f_land + 32, 0.05), (f_land + 40, 0.0), (f_land + 60, -0.03)):
        place(S, a, f, xf, ya, z, 90)
        S.key(w.bl, f, loc=(BL_XR - 1.06, 0, 0.03 if f < f_land + 40 else 0.028), rot=(0, 0, 0))
    S.cue("boing", f_jump + 3, vol=-6); S.cue("clunk", f_land, vol=-8); S.cue("slide_down", f_land + 2, vol=-9); S.cue("whoosh", f_land + 6, vol=-10)
    S.cue("splash", f_land + 24, vol=-4); S.cue("drain", f_land + 28, vol=-9); S.cue("hit", f_land + 26, vol=-8)
    mud_splash(S, xf + 0.1, ya, f_land + 22, n=18, size=0.05, up=2.0, spread=0.8)
    mud_splash(S, xf + 0.1, ya, f_land + 25, n=10, size=0.04, up=1.3, spread=0.6, seed=4)
    ripple(S, xf, ya, f_land + 24, r1=0.62); ripple(S, xf, ya, f_land + 24, r1=0.46, delay=6)
    S.f = 128
    a.verify(S.f)
    return a


# ------------------------------------------------------------------ nivel 5469
def l5(S):
    """5469: piensa; agarra la esquina doblada (Picking Up) y tira dando un paso atrás: la manta sigue a la mano deslizándose por
    ENCIMA del barro (inclinada por la esquina), la suelta y se desliza hasta su orilla; saluda y se sienta encima."""
    w = build_set(S); cam_static(S)
    yt = TAB_Y
    a = MixamoActor(S, x=-7.95, yaw=90, use=["Thinking", "Picking Up", "Waving", "Sitting Idle"])
    seg(S, a, "Thinking", 1, 40, start=0, blend=5)
    f0p, st_p, spd = 36, 18, 1.6
    seg(S, a, "Picking Up", f0p, 84, start=st_p, speed=spd, blend=5)
    f_low = int(f0p + (55 - st_p) / spd)                            # la mano está más abajo (agarra la esquina)
    f_rel = 80                                                      # suelta la manta
    f_wave, f_sit = 98, 124
    seg(S, a, "Waving", f_wave - 2, f_sit, start=0, blend=5, repeat=3)
    seg(S, a, "Sitting Idle", f_sit - 2, None, start=0, blend=7)
    # 1) raíz provisional (con una inclinación hacia delante al agacharse) para medir dónde queda la mano
    lean = ((f_low - 14, 0.0), (f_low, 12.0), (f_low + 8, 6.0))
    for f, ang in lean: place(S, a, f, -7.95, yt, 0, 90, ang)
    place(S, a, 1, -7.95, yt, 0, 90)
    hand = bone_pos(S, a, "RightHand", f_low, 0.95)
    tip = tab_tip()
    x_r = -7.95 + (tip.x - hand.x)                                  # raíz para que la mano toque la punta de la esquina
    print(f"[ep011] raiz de agarre x={x_r:.3f}  (borde del charco a y={yt}: x={PCX - PRX * math.sqrt(max(0, 1 - ((yt - PCY) / PRY) ** 2)):.3f})")
    # 2) raíz definitiva: agarra, y tira dando un paso atrás (de f_low a f_rel) mientras se incorpora
    place(S, a, 1, x_r, yt, 0, 90)
    for f, ang in lean: place(S, a, f, x_r, yt, 0, 90, ang)
    x_end = x_r - 0.55
    for f in range(f_low + 1, f_rel + 1):
        t = (f - f_low) / float(f_rel - f_low)
        place(S, a, f, x_r + (x_end - x_r) * (t * t * (3 - 2 * t)), yt, 0, 90, 6.0 * (1 - t) - 4.0 * math.sin(math.pi * t), interp="LINEAR")
    place(S, a, f_rel + 14, x_end, yt, 0, 90, 0.0)
    x_sit = -8.68
    place(S, a, f_rel + 22, x_end, yt, 0, 90); place(S, a, f_sit - 2, x_sit, yt, 0, 90)
    # 3) la manta sigue a la mano: la esquina (distancia D a lo largo de la manta) coincide con la mano; se inclina por esa punta
    D = BL_L + TAB_L
    S.key(w.tab, f_low - 3, rot=(0, R(TAB_A), 0)); S.key(w.tab, f_low + 1, rot=(0, R(2.0), 0))
    S.key(w.bl, f_low - 1, loc=(BL_XR, 0, 0), rot=(0, 0, 0), interp="LINEAR")
    zb = 0.025
    Fx = BL_XR; th = 0.0
    for f in range(f_low, f_rel + 1):
        h = bone_pos(S, a, "RightHand", f, 0.95)
        hz = max(h.z, 0.10)
        th = math.asin(max(0.0, min(0.9, (hz - zb) / D)))
        Fx = h.x + D * math.cos(th)
        S.key(w.bl, f, loc=(Fx, 0, zb), rot=(0, th, 0), interp="LINEAR")
    # 4) la suelta: sigue por inercia (decelera) hasta su orilla, baja a la hierba y queda plana
    d_tot = Fx - (-8.02); T = 17; v0 = 2 * d_tot / T
    for k in range(1, T + 1):
        dx = v0 * k - 0.5 * (v0 / T) * k * k
        thk = th * max(0.0, 1 - k / 8.0)
        zk = zb * (1 - max(0.0, (k - 12) / 5.0))
        S.key(w.bl, f_rel + k, loc=(Fx - dx, 0, zk), rot=(0, thk, 0), interp="LINEAR")
        if k == 8: S.key(w.tab, f_rel + 8, rot=(0, R(2.0), 0))
    S.key(w.tab, f_rel + 12, rot=(0, 0, 0))
    S.cue("pop", f_low, vol=-12); S.cue("slide_down", f_low + 4, vol=-10); S.cue("whoosh", f_low + 6, vol=-9)
    S.cue("slide_down", f_rel + 2, vol=-12); S.cue("tada", f_wave + 4, vol=-9)
    S.f = 150
    a.verify(S.f)
    return a


LEVELS = [(-450, l1), (-80, l2), (120, l3), (900, l4), (5469, l5)]
