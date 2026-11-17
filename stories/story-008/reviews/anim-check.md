# anim-check story-008 (ep005, "Every IQ Level Feeds a Duck")

Archivo: anim/episodes/ep005.py. Escenario rio, camara automatica del kit (sin CUSTOM_CAMERA). Pato y patitos construidos con S.obj (cuerpo, cola, alas, pies, cabeza, pico, ojos, cuello) y animados con S.key.
check_framing.py: "ninguno" en los 5 niveles. Fotogramas a 270x480 revisados uno a uno.
Duracion (a 24 fps): N1 150, N2 ~160, N3 158, N4 165, N5 170 fotogramas (aprox. 4,2-4,7 s a 1,5x).

Condiciones del Director aplicadas: en -420 la hogaza NO toca al pato (cae al agua a su lado, salpicadura, el pato se sobresalta, da media vuelta y se aleja ileso mirando atras); 3 patitos y torre estable; ningun animal sufre dano.

## Nivel 1 (IQ -420)
- f1: hombre con la hogaza (color miel, bien visible) alzada sobre la cabeza (siembra el remate); pato amarillo en primer plano mirandole. Accion desde el primer fotograma.
- f28: hogaza volando en arco hacia el agua; pato junto al muelle, entero y visible.
- f60: pato ya fuera de plano (se ha ido nadando), el protagonista de frente saluda a la nada. Se ve: personaje centrado, sin cortes.
- Corregido: el primer chapuzon forzaba un primer plano que sacaba al actor del cuadro (se anula el plano de detalle del kit); la hogaza era del color de la mano y se confundia (ahora khaki y mas grande).

## Nivel 2 (IQ -60)
- f1: desmigando la hogaza con ambas manos, pato a la vista.
- f40: migas en fila sobre el muelle, pato mirando, actor de frente con brazos abiertos.
- f62: rafaga de viento: migas volando a la derecha (puntos blancos), actor quieto sorprendido.
- f105: actor al borde del muelle con brazos en molinillo (casi cae), el pato le mira. Corregido: las migas salian gigantes por sobrescribir la escala.

## Nivel 3 (IQ +130)
- f1: agachado e inmovil en el borde del muelle con la miga en la palma; pato en el agua observando.
- f94: pico del pato junto a la mano, a punto de picotear (antes de eso duda, retrocede y avanza).
- f110 y f125: miga comida; el actor se lleva la mano al pecho, pato satisfecho al lado. Las lagrimas son muy pequenas: se leen poco a esta resolucion (riesgo bajo).

## Nivel 4 (IQ +850)
- f1: sentado en el muelle, reguero de migas desde el borde del agua hacia el, pato entrando en cuadro.
- f70: pato sobre el muelle picoteando el reguero hacia el actor.
- f90 y f125: el pato sube por la pierna y se sienta en su regazo (se ve de lado, delante del torso). Lectura correcta; el pato tapa algo el torso pero la cabeza queda visible.

## Nivel 5 (IQ +5100)
- f1: hogaza en la mano junto a la cabeza, pato nadando hacia el.
- f66: pato saltando hacia la cabeza (hogaza ya como sombrero); patitos en fila sobre el muelle.
- f105 y f135: torre estable: hogaza, pato y 3 patitos apilados sobre su casco. f138 (540x960): de perfil, guiño a camara con un ojo cerrado; torre completa dentro del cuadro.

## ISSUES
- Ninguno bloqueante. Mejora posible (kit): accion reutilizable "peck" y utilidad de pato/patitos si se reusan en otros episodios (hoy viven en ep005.py).
- Nota: la camara automatica del kit sigue solo al actor; el pato debe quedarse cerca del muelle (x -2.1 a -1.5, y -0.5) para salir en cuadro.
