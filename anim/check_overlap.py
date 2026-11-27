"""check_overlap.py -- detecta objetos que se atraviesan, SIN renderizar.

Uso:  /home/user/blender-proto/venv/bin/python anim/check_overlap.py -- anim/episodes/<id>.py <nivel 1..N|all> [--tol 0.01] [--step 1] [--ignore sub1,sub2]

Carga el episodio igual que run_level.py, recorre todos los fotogramas, evalua las mallas deformadas (armadura del actor, animaciones) y compara
cada objeto ANIMADO (o skineado) contra el resto de mallas con mathutils.bvhtree. Para ignorar contactos menores de `tol` metros (1 cm por defecto)
la malla del objeto animado se encoge `tol` a lo largo de sus normales antes del test: solo hay solape si la penetracion supera ~tol.
Se ignoran: el suelo, objetos de la misma jerarquia, objetos con escala 0 (no visibles) y los "decals" de nata/confeti/salpicaduras
(parches pegados a proposito). Imprime, por pareja de grupos, el rango de fotogramas y el maximo de triangulos solapados.
Sale con codigo 1 si hay intersecciones."""
import importlib.util, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import bpy
from mathutils import Vector
from mathutils.bvhtree import BVHTree
from kit import Stage, look_for

DECALS = ("nata_cara", "fresa_pelo", "moreton", "dollop", "mancha", "gota", "fresa_puerta", "salpica", "fresa_cae", "confeti", "dedo")
FOCUS = ("mixamo", "tarta", "silla", "mantel", "vaso")        # solo se reportan parejas donde interviene uno de estos grupos (persona, tarta, silla, mantel, vasos)
FLOOR = ("suelo", "floor", "ground", "agua")


def parse():
    a = sys.argv[sys.argv.index("--") + 1:]
    opts = {"tol": 0.01, "step": 1, "ignore": []}
    pos = []
    i = 0
    while i < len(a):
        if a[i] in ("--tol", "--step", "--ignore"):
            k = a[i][2:]; v = a[i + 1]; opts[k] = v.split(",") if k == "ignore" else (float(v) if k == "tol" else int(v)); i += 2
        else: pos.append(a[i]); i += 1
    return pos, opts


def root_of(o):
    while o.parent is not None: o = o.parent
    return o


def is_animated(o):
    p = o
    while p is not None:
        ad = p.animation_data
        if ad is not None and (ad.action is not None or ad.nla_tracks): return True
        if any(m.type == "ARMATURE" for m in getattr(p, "modifiers", [])): return True
        p = p.parent
    return False


def world_mesh(o, dg, shrink):
    """(verts_mundo, triangulos) de la malla evaluada; `shrink` > 0 mueve cada vertice hacia dentro a lo largo de su normal."""
    ev = o.evaluated_get(dg); me = ev.to_mesh()
    try:
        mw = ev.matrix_world; nm = mw.to_3x3().inverted_safe().transposed()
        me.calc_loop_triangles()
        vs = []
        for v in me.vertices:
            w = mw @ v.co
            if shrink: w = w - (nm @ v.normal).normalized() * shrink
            vs.append(w)
        tris = [tuple(t.vertices) for t in me.loop_triangles]
    finally:
        ev.to_mesh_clear()
    return vs, tris


def bbox_world(o):
    pts = [o.matrix_world @ Vector(c) for c in o.bound_box]
    return Vector(map(min, zip(*pts))), Vector(map(max, zip(*pts)))


def run_level(ep_path, level, tol=0.01, step=1, ignore=()):
    spec = importlib.util.spec_from_file_location("ep", ep_path); ep = importlib.util.module_from_spec(spec); spec.loader.exec_module(ep)
    iq, fn = ep.LEVELS[level - 1]
    S = Stage(env=getattr(ep, "ENV", "rio")); S.look = getattr(ep, "LOOK", None) or look_for(os.path.basename(ep_path))
    fn(S)
    sc = S.sc; n = S.f + 10; dg = bpy.context.evaluated_depsgraph_get()
    skip = DECALS + tuple(ignore)
    meshes = [o for o in sc.objects if o.type == "MESH" and not any(s in o.name.lower() for s in skip) and not any(s in o.name.lower() for s in FLOOR)]
    movers = [o for o in meshes if is_animated(o)]
    static = [o for o in meshes if o not in movers]
    cache = {}                                                       # BVH de estaticos (se construyen bajo demanda)
    hits = {}                                                        # (grupoA, grupoB) -> {frame: n}
    for f in range(1, n + 1, step):
        sc.frame_set(f); bpy.context.view_layer.update(); dg = bpy.context.evaluated_depsgraph_get()
        mv = []
        for o in movers:
            if o.hide_viewport or o.hide_render: continue
            lo, hi = bbox_world(o.evaluated_get(dg)) if False else bbox_world(o)
            if (hi - lo).length < 1e-3: continue                     # escala 0: invisible
            vs, tr = world_mesh(o, dg, tol)
            if not tr: continue
            xs = [v.x for v in vs]; ys = [v.y for v in vs]; zs = [v.z for v in vs]
            mv.append((o, BVHTree.FromPolygons(vs, tr, epsilon=0.0), (min(xs), min(ys), min(zs)), (max(xs), max(ys), max(zs))))
        def boxes_touch(a, b): return all(a[0][i] <= b[1][i] and b[0][i] <= a[1][i] for i in range(3))
        for i, (o, bv, lo, hi) in enumerate(mv):
            go = root_of(o)
            for s in static:
                if root_of(s) is go: continue
                key = s.name
                if key not in cache:
                    vs, tr = world_mesh(s, dg, 0.0)
                    if not tr: cache[key] = None
                    else:
                        xs = [v.x for v in vs]; ys = [v.y for v in vs]; zs = [v.z for v in vs]
                        cache[key] = (BVHTree.FromPolygons(vs, tr, epsilon=0.0), (min(xs), min(ys), min(zs)), (max(xs), max(ys), max(zs)))
                c = cache[key]
                if c is None or not boxes_touch((lo, hi), (c[1], c[2])): continue
                if (Vector(c[2]) - Vector(c[1])).length < 1e-3: continue
                ov = bv.overlap(c[0])
                if ov: hits.setdefault((go.name, root_of(s).name, o.name, s.name), {})[f] = len(ov)
            for (o2, bv2, lo2, hi2) in mv[i + 1:]:                   # animado vs animado
                if root_of(o2) is go or not boxes_touch((lo, hi), (lo2, hi2)): continue
                ov = bv.overlap(bv2)
                if ov: hits.setdefault((go.name, root_of(o2).name, o.name, o2.name), {})[f] = len(ov)
    return iq, n, hits


def summarize(hits):
    """Agrupa por pareja de grupos raiz: rangos de fotogramas y partes implicadas."""
    g = {}
    for (ga, gb, oa, ob), fr in hits.items():
        if not any(k in ga.lower() or k in gb.lower() for k in FOCUS): continue
        k = tuple(sorted((ga, gb))); e = g.setdefault(k, {"frames": {}, "parts": set()})
        for f, c in fr.items(): e["frames"][f] = e["frames"].get(f, 0) + c
        e["parts"].add(f"{oa}~{ob}")
    return g


def ranges(fs):
    fs = sorted(fs); out = []; s = p = fs[0]
    for f in fs[1:]:
        if f - p > 2: out.append((s, p)); s = f
        p = f
    out.append((s, p)); return ", ".join(f"f{a}-f{b}" if a != b else f"f{a}" for a, b in out)


if __name__ == "__main__":
    pos, opts = parse()
    ep_path = pos[0]; sel = pos[1] if len(pos) > 1 else "all"
    spec = importlib.util.spec_from_file_location("ep0", ep_path); ep0 = importlib.util.module_from_spec(spec); spec.loader.exec_module(ep0)
    levels = range(1, len(ep0.LEVELS) + 1) if sel == "all" else [int(sel)]
    if sel != "all" and False: pass
    total = 0
    if len(levels) > 1 or sel == "all":                              # un proceso por nivel (la escena de Blender no se limpia entre niveles)
        import subprocess
        for l in levels:
            r = subprocess.run([sys.executable, os.path.abspath(__file__), "--", ep_path, str(l), "--tol", str(opts["tol"]), "--step", str(opts["step"]),
                                "--ignore", ",".join(opts["ignore"]) or "-"], capture_output=True, text=True)
            lines = [x for x in r.stdout.splitlines() if x.startswith(("NIVEL", "  ", "OK"))]
            print("\n".join(lines) if lines else (r.stdout + r.stderr)[-1500:]); total += r.returncode
        sys.exit(1 if total else 0)
    iq, n, hits = run_level(ep_path, levels[0], opts["tol"], opts["step"], [x for x in opts["ignore"] if x != "-"])
    g = summarize(hits)
    print(f"NIVEL {levels[0]} IQ {iq}: {n} fotogramas, tol {opts['tol'] * 100:.1f} cm -> {len(g)} parejas que se atraviesan")
    for (a, b), e in sorted(g.items(), key=lambda kv: min(kv[1]["frames"])):
        print(f"  {a} <-> {b}: {ranges(e['frames'])} ({len(e['frames'])} fotogramas; max {max(e['frames'].values())} tri; {', '.join(sorted(e['parts'])[:3])})")
    if not g: print("OK: sin intersecciones")
    sys.exit(1 if g else 0)
