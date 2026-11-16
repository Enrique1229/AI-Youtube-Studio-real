"""run_level.py -- <episodio.py> <nivel 1..N> <carpeta_salida> [fotograma]   (con bpy o dentro de Blender)"""
import importlib.util, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from kit import Stage, look_for
a = sys.argv[sys.argv.index("--") + 1:]
spec = importlib.util.spec_from_file_location("ep", a[0]); ep = importlib.util.module_from_spec(spec); spec.loader.exec_module(ep)
iq, fn = ep.LEVELS[int(a[1]) - 1]
S = Stage(env=getattr(ep, "ENV", "rio")); S.look = getattr(ep, 'LOOK', None) or look_for(os.path.basename(a[0]))   # un personaje distinto por episodio
actor = fn(S)
if not getattr(ep, "CUSTOM_CAMERA", False): S.follow(actor, S.f + 10)   # CUSTOM_CAMERA: el episodio keyea su propia cámara
n = S.render(a[2], int(a[3]) if len(a) > 3 else None)
print(f"NIVEL {a[1]} IQ {iq}: {n} fotogramas")
