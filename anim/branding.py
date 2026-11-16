"""branding.py -- <avatar|banner> <salida.png>   (con bpy)

Foto de perfil (800x800) y banner (2560x1440) del canal con el personaje y el escenario del propio kit:
coherentes con los vídeos y sin material de terceros. El texto del banner se añade aparte (scripts/brand_text.py).
"""
import math, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import bpy
from kit import Stage, look_for

a = sys.argv[sys.argv.index("--") + 1:]
kind, out = a[0], a[1]
os.environ["STUDIO_SHOTS"] = "0"
res = (800, 800) if kind == "avatar" else (2560, 1440)
S = Stage(res=res, samples=int(os.environ.get("STUDIO_SAMPLES", 48)))
S.look = look_for("ep001.py")
act = S.actor(x=-3.6 if kind == "banner" else -4.0)
S.f = 1; act.face(-8, 1, turn=1)
# pose: saluda con una mano, la otra en la cadera; sonrisa de "listo"
for i, (sh, el) in enumerate(zip(act.arms, act.elbows)):                  # brazos relajados, un poco separados
    sx = -1 if i == 0 else 1
    S.key(sh, 1, rot=(0, math.radians(-10 * sx), 0)); S.key(el, 1, rot=(math.radians(-15), 0, 0))
act.look(0.0, -0.005, 1)
for lid in act.lids: S.key(lid, 1, scale=(0.001, 0.001, 0.001))                        # ojos bien abiertos: cara simpática
S.sc.frame_set(1); bpy.context.view_layer.update()
cam = S.cam; cam.parent = None
head = act.head.matrix_world.translation
for c in list(cam.constraints): cam.constraints.remove(c)
tgt = S.empty("mira_marca", tuple(head))
tc = cam.constraints.new("TRACK_TO"); tc.target = tgt; tc.track_axis = "TRACK_NEGATIVE_Z"; tc.up_axis = "UP_Y"
if kind == "avatar":
    tgt.location = (head.x, head.y, head.z - 0.20)
    cam.location = (head.x - 0.35, head.y - 2.1, head.z + 0.02); cam.data.lens = 55
    cam.data.dof.use_dof = True; cam.data.dof.focus_object = act.head; cam.data.dof.aperture_fstop = 1.8
else:
    # personaje entero dentro de la zona segura (1546x423 centrada): lejos y a la izquierda; el nombre va a la derecha
    tgt.location = (head.x + 2.9, head.y, 0.95)
    cam.location = (head.x - 1.5, head.y - 14.5, 1.15); cam.data.lens = 38
    cam.data.dof.use_dof = True; cam.data.dof.focus_object = act.head; cam.data.dof.aperture_fstop = 4.0
S.sc.render.filepath = out
bpy.ops.render.render(write_still=True)
print("OK", out)
