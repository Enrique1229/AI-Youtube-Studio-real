# Biblioteca de animación (anim/kit.py)

Ejecutar un nivel:  `python anim/run_level.py -- anim/episodes/ep001.py <nivel> <carpeta_salida> [fotograma]`
(con `pip install bpy` en Python 3.13, o dentro de Blender: `blender -b -P anim/run_level.py -- …`).
Montar el episodio: `python scripts/anim_build.py <carpeta_render> <salida.mp4> --iq -450,-80,120,900,5469`
Motor de render: variable `STUDIO_ENGINE` (por defecto CYCLES en CPU; con GPU, `STUDIO_DEVICE=GPU`). EEVEE no está probado.

## Escenario S (Stage)
- `S.actor(color="blue", hat="bombin"|"corona", x=0.0, size=1.0)` → actor
- `S.obj(prim, nombre, color, loc, scale, rot, parent)` crea un objeto (prim: cube, uv_sphere, cylinder, cone). Colores: ver PALETTE.
- `S.empty(nombre, loc, parent)`, `S.key(obj, f, loc, rot, scale, interp)` (interp: BEZIER, BACK, BOUNCE, ELASTIC, LINEAR)
- `S.wait(n)` avanza n fotogramas (24 por segundo). `S.f` = fotograma actual.
- `S.cue(tipo, f, vol)` anota un sonido: boing, splash, pop, slide_down, tada, creak, paddle, clunk, drain, whoosh, hit.
- `S.splash(x, big=1.0)` salpicadura. `S.water` es el agua del río (se puede bajar para vaciarlo).
- Geografía del río: orilla izquierda x < -2.5, agua entre -2.5 y 2.5 (superficie z ≈ -0.25, lecho z = -1.1), muelle en x ≈ -2.6 (z = 0.12).

## Actor
- Movimiento: `hop_to(x, z, h, dur)`, `walk_to(x)`, `fall_in_water()`, `cheer()`
- Gestos: `think(n)`, `shiver(n)`, `blink()`, `look(dx, dz)`, `tilt(grados)`, `arms_to(grados)`
- `drop_hat_floating(fotograma)`: el sombrero se suelta y queda flotando.
- Partes accesibles: `a.root`, `a.body`, `a.hat`, `a.arms`.

Medido en CPU (4 núcleos): ~3 s por fotograma a 432x768. Un episodio de 33 s: ~40 min. Con GPU, sin medir.
