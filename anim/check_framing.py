"""check_framing.py -- <episodio.py> <nivel>  (con bpy): avisa de fotogramas con la cabeza del protagonista fuera de la zona útil (bajo el rótulo, dentro del cuadro)."""
import sys, os, importlib.util; sys.path.insert(0, "anim")
import bpy
from bpy_extras.object_utils import world_to_camera_view
from kit import Stage, look_for
spec = importlib.util.spec_from_file_location("ep", sys.argv[-2]); ep = importlib.util.module_from_spec(spec); spec.loader.exec_module(ep)
lv = int(sys.argv[-1])
S = Stage(res=(1080, 1920)); S.look = look_for(os.path.basename(sys.argv[-2])); a = ep.LEVELS[lv - 1][1](S); n = S.f + 10; S.follow(a, n)
bad = []
for f in range(1, n + 1, 2):
    S.sc.frame_set(f); bpy.context.view_layer.update()
    h = a.head.matrix_world.translation; p = a.root.matrix_world.translation
    if p.z < -0.6: continue                                          # ya bajo el agua
    v = world_to_camera_view(S.sc, S.cam, h)
    if v.y > 0.83 or v.y < 0.05 or v.x < 0.03 or v.x > 0.97: bad.append((f, round(v.x, 2), round(v.y, 2)))
print("NIVEL", lv, "fotogramas con la cabeza fuera de la zona útil:", bad if bad else "ninguno")
