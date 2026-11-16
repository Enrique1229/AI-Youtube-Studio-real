# anim-check story-005 (ep002, "A Match Warms Up an Ice Cube")

Un nivel (LEVELS = [(0, l1)], CAPTION = None, ENV = "mesa", CUSTOM_CAMERA = True). 481 fotogramas a 24 fps = 20 s a velocidad normal.
Pruebas a 270x480, 8 muestras. Fotogramas mirados: 20, 60, 100, 180, 230, 310, 349, 365, 400/410, 440, 470/480.

## Que vi y que corregi
- f20 (primer plano, tirita): primera version, cubo cortado por el borde y descentrado (lens 50 en vertical da un campo horizontal muy estrecho). Cambie a lens 35 y aleje la camara; ahora cubo centrado, ojos y cejas preocupadas. Las cejas salian enfadadas (signo invertido): corregido.
- f60 (la cerilla entra): cerilla a la izquierda, caja de cerillas de pie (la ampliada con tira negra y etiqueta), cubo a la derecha. Cejas de la cerilla por defecto enfadadas: las puse amables con keys de rotacion.
- f100 (cerilla encendida, se inclina): llama visible, cubo sonrie. La caja se veia como un pilar rojo: anadi tira negra frontal.
- f180 (derritiendo): bloque aplastado, charco azul que crece, cubo triste; cara baja con el bloque. OK.
- f230 (casi charco): losa fina con ojos sobre el charco; cerilla abanica con la llama. OK.
- f310 (gota): charco ancho, gota con ojos que mira a la cerilla. OK.
- f349 (abrazo): la gota cubre la cabeza de la cerilla, llama aun visible (se apaga en f351). Se lee como salpicadura/abrazo; mouth demasiado grande al principio, reducido.
- f365 (silencio): cabeza negra con gota encima, charco vacio. OK.
- f400/410 (vapor): nube blanca con dos caritas separadas (antes parecian 4 ojos juntos; separe caras y ensanche la nube), cerilla negra. OK.
- f440/470 (final): nube sube fuera de plano por arriba; quedan cerilla negra de ojos cerrados/vacia y charco. La camara subia hasta ver el cielo azul por encima de la pared: limite el cabeceo (tgt z 0.48).

## Notas / riesgos
- Cubo y charco con alpha en Principled: se ven casi opacos con tinte azul (no hay transmision real). Aceptable.
- No se ha renderizado el nivel completo ni comprobado el audio (cues: creak x2, ignite, drain x2, whoosh, pop x2, tada).
- La velocidad del montaje (1,5x) acortaria el nivel a ~13 s: montar con `--speed 1.0` (o <=1.1) para llegar a 18-22 s.
- Cambios fuera del episodio: anim/run_level.py usa Stage(env=getattr(ep,"ENV","rio")) y salta S.follow si el episodio define CUSTOM_CAMERA = True.
