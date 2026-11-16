# anim-check story-005 (ep002, "A Match Warms Up an Ice Cube") - ronda 2

Un nivel (LEVELS = [(0, l1)], CAPTION = None, ENV = "mesa", CUSTOM_CAMERA = True). 420 fotogramas a 24 fps = 17,5 s a velocidad normal (SPEED 1.0). Montar con --speed 1.0.
Pruebas a 270x480, 8 muestras. Fotogramas mirados (ronda 2): 20, 48, 70, 85, 105, 110, 135, 160, 175, 205, 245, 262, 270, 285, 290, 300, 310, 312, 322, 328, 330, 335, 345, 360, 365, 380, 395, 410, 419.

## Cambios de la ronda 2 (rechazo del Director)
1. Encuadre: lens fijo 50 y cortes secos entre planos cerrados (un helper `shot` por corte). Hallazgo: el sensor encaja por la altura en vertical, el ancho de cuadro es ~0,405 x distancia (no 0,72). Con d=0,85*1,75 el cuadro mide ~0,6 de ancho: la cara del cubito (~0,2) ocupa ~1/3-1/2. Descubri tambien que la preferencia de interpolacion de Blender no se aplicaba (la camara se deslizaba entre planos): ahora se fuerza CONSTANT en el key del corte.
   Planos: 1-35 cubito tiritando (cerrado) / 36-61 abierto 1 s (entra la cerilla, caja, cubito) / 62-93 cerilla se enciende / 94-149 dos planos cubito+cabeza de cerilla / 150-189 cerilla duda / 190-237 cubito aplastandose / 238-265 charco con cara / 266-279 cerilla abanica / 280-317 gota que mira / 318-368 salto y abrazo / 369-410 nube subiendo, camara la sigue.
2. Cabeza cortada: la cerilla recta llega a z~0,6 con llama a ~0,72. Ahora los planos de la cerilla se centran en z 0,44-0,46 (arriba libre >15 %). f70/f85: cabeza y llama enteras, ~30 % del alto libre arriba. Solo queda la punta de la llama (no la cara) asomando en el borde en f245 mientras la cerilla abanica fuera de plano.
3. Final: el abrazo se adelanta (F_HUG 351 -> 335: abanico mas corto y gota antes), la nube sube en 40 fotogramas (en vez de 80) y el nivel termina en F_HUG+75 (+10 del kit). Tras el "tada" (f383) quedan ~1,5 s: la camara sube con la nube y se ve la cerilla negra parpadeando abajo (f395/f410/f419). Total 17,5 s.

## Que vi
- f20: cubito centrado, cara >1/2 del ancho, ceja preocupada, aliento. OK.
- f48: plano abierto: cerilla entrando por la izquierda con caja roja, cubito a la derecha; cabeza entera, arriba libre. OK (1 s).
- f70/f85: cerilla cerrada, cabeza y llama enteras, cejas amables. OK.
- f105/f135: cubito sonrie/derritiendo con la cabeza de la cerilla entera arriba-izquierda; cara ~1/3 del ancho. OK.
- f160/f175: cerilla duda mirando a camara; cabeza entera. OK.
- f205: bloque aplastado sobre charco, cerilla con llama sobre el. OK.
- f245/f262/f270: charco con ojos tristes, grandes (>50 %); cerilla abanicando en plano propio. OK.
- f285-f312: gota nace pequena (pop), luego cara grande que mira a la cerilla. OK.
- f322/f328: la gota salta (apice bajado a z 0,36 para que no toque el borde superior). f330/f335: abrazo, cubre la cabeza, llama se apaga. Se lee. OK.
- f345/f360: gota sobre cabeza oscura, charco vacio. OK.
- f380/f395/f410/f419: nube con dos caritas (cada una ~30 % del ancho) sube; cerilla negra abajo, ojos entrecerrados. OK.

## Notas / riesgos
- No se ha renderizado el nivel completo a resolucion final ni comprobado el audio (cues: creak x2, drain x2, whoosh, pop x2, tada; el "pop" y "whoosh" de la gota se movieron 16 fotogramas antes con su accion).
- Los cortes son en el propio nivel; el CTA "follow for more" lo anade el montaje en el ultimo 1,6 s (cubre bajo la cerilla negra, sin caras).
- Cambios fuera del episodio: ninguno nuevo (anim/run_level.py ya soportaba ENV y CUSTOM_CAMERA).
