"""run_level.py -- <episodio.py> <nivel 1..N> <carpeta_salida> [fotograma]   (con bpy o dentro de Blender)"""
import importlib.util, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from kit import Stage
a = sys.argv[sys.argv.index("--") + 1:]
spec = importlib.util.spec_from_file_location("ep", a[0]); ep = importlib.util.module_from_spec(spec); spec.loader.exec_module(ep)
iq, fn = ep.LEVELS[int(a[1]) - 1]
S = Stage(); actor = fn(S)
S.follow(actor, S.f + 10)
n = S.render(a[2], int(a[3]) if len(a) > 3 else None)
print(f"NIVEL {a[1]} IQ {iq}: {n} fotogramas")
