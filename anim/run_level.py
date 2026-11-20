"""run_level.py -- <episodio.py> <nivel 1..N> <carpeta_salida> [fotograma]   (con bpy o dentro de Blender)"""
import importlib.util, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from kit import Stage, look_for
a = sys.argv[sys.argv.index("--") + 1:]
spec = importlib.util.spec_from_file_location("ep", a[0]); ep = importlib.util.module_from_spec(spec); spec.loader.exec_module(ep)
iq, fn = ep.LEVELS[int(a[1]) - 1]
S = Stage(env=getattr(ep, "ENV", "rio")); S.look = getattr(ep, 'LOOK', None) or look_for(os.path.basename(a[0]))   # un personaje distinto por episodio
if getattr(ep, "ASSETS", None):                         # modelos externos (Mixar → GLB): se cargan y verifican
    from assets import load_manifest, verify_animated
    S.asset_manifest = load_manifest(ep.ASSETS)
actor = fn(S)
if getattr(ep, "ASSETS", None): verify_animated(S, S.f)  # lo marcado como animado debe moverse de verdad
if not getattr(ep, "CUSTOM_CAMERA", False): S.follow(actor, S.f + 10)   # CUSTOM_CAMERA: el episodio keyea su propia cámara
def framing_check(S, actor, n):
    """Encuadre: la cabeza (con margen para pelo) no debe entrar en el 22 % superior (título y etiqueta) ni salir del cuadro."""
    import bpy
    from bpy_extras.object_utils import world_to_camera_view
    head = getattr(actor, "head", None)
    if head is None: return []
    bad = []
    for f in range(1, n + 1, 2):
        S.sc.frame_set(f); bpy.context.view_layer.update()
        p = head.matrix_world.translation.copy(); p.z += 0.28
        v = world_to_camera_view(S.sc, S.cam, p)
        if v.z > 0 and (v.y > 0.78 or v.x < 0.02 or v.x > 0.98): bad.append((f, round(v.x, 2), round(v.y, 2)))
    return bad


bad = framing_check(S, actor, S.f + 10)
if bad: print(f"AVISO ENCUADRE nivel {a[1]}: la cabeza entra en la zona del texto o sale del cuadro en {len(bad)} fotogramas, p. ej. {bad[:4]}")
n = S.render(a[2], int(a[3]) if len(a) > 3 else None)
print(f"NIVEL {a[1]} IQ {iq}: {n} fotogramas")
