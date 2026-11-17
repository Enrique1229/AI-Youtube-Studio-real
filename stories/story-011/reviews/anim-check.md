# anim-check — ep008 "Every IQ Level Moves a Boulder" (story-011)

Archivo: anim/episodes/ep008.py. Escenario "rio", cámara automática del kit (sin CUSTOM_CAMERA), ONSCREEN = "Every IQ level moves a boulder".
Fotogramas de prueba (270x480, 8 muestras) en el scratchpad ep008/l<nivel>_fNNN. check_framing: "ninguno" en los 5 niveles.
Duración bruta (fotogramas a velocidad normal): L1 173, L2 161, L3 198, L4 135, L5 192 (a 1,5x: 90-132).

Reglas de la revisión de normas (nivel -500): choque con rebote suave, sonidos "boing"/"pop" (nunca "hit"), estrellas y pajaritos 22 fotogramas (< 24).

Escenario común: camino de tierra (franja + ensanche + manchas + guijarros), hierba redistribuida alrededor (sin briznas sobre el camino), banco de madera con veta, patas de hierro y respaldo, arbustos con florecitas, flores sueltas,
roca = ico_sphere deformada (superelipsoide con ruido) con pmat de piedra (relieve fuerte) y musgo; versión "espuma" amarilla de esponja para el 5200.

## Nivel 1 (-500)
- f1: de espaldas a la roca, inclinado hacia atrás con rodillas dobladas, ya empujando (acción desde el primer fotograma). Se ve el esfuerzo (pose de tres empujones, polvo flojo, roca inmóvil).
- f125: choque de frente con la roca tras correr (captura "correr", start 0,4 s para no empezar en T-pose); la roca se mece y el personaje rebota hacia atrás con brazos al aire; nubecita de polvo.
- f150: sentado de golpe en el camino, piernas al frente, con 3 estrellas y 2 pajaritos girando sobre la cabeza (pequeños pero legibles). Termina con parpadeo.
- Visto: sin atravesamientos; las estrellas son pequeñas en el plano general.

## Nivel 2 (-80)
- f1: corriendo hacia la roca (captura "correr"), ya en movimiento.
- f60: encima de la roca (salto con captura), rebotando con las rodillas para "empujar con su peso".
- f100 (plano medio): resbala por el frente y queda agarrado al borde, piernas colgando.
- f125/f150 (plano general): colgado de espaldas a cámara con la cabeza girada hacia el público, pataleando; la roca, impertérrita. Corregido: antes colgaba por detrás de la roca y se tapaba (la roca abombada y el plano de cámara); ahora cuelga por el lado de cámara y las manos se calculan sobre el borde.
- Limitación: roca subida a 1,5 m de alto para que haya sitio de colgar; las piernas están encogidas (si no, atravesarían el suelo).

## Nivel 3 (130)
- f1: ya empujando, de perfil, manos sobre la roca (captura "empujar" al 50 % + brazos a la altura del pecho porque el clip real empuja a nivel del suelo); en f60 se ve el avance por pasos con polvo y gotas de sudor.
- f105/f120: suelta la roca, se endereza jadeando, se da la vuelta y se aleja tambaleante (captura "caminar").
- f140-f195: tumbado de espaldas en el camino, respira hondo (pecho sube y baja), sudor, y levanta el puño orgulloso. Corregido: tumbarse junto a la roca se tapaba/salía de cuadro; ahora cae 1,5 m a la izquierda.

## Nivel 4 (900)
- f1: encorvado deslizando el tablón bajo la roca (acción desde f1). Tablón con veta, tronco como fulcro, clavos.
- f80: aterriza en el extremo alto del tablón (salto con captura), el tablón baja y la roca sube y se inclina.
- f125: la roca ha rodado ~0,5 m (salto lateral corto, con polvo) y él celebra (captura "contento"). La roca queda en el borde derecho del encuadre (visible a medias).
- Nota: el rodar es una trayectoria con S.key, sin física.

## Nivel 5 (5200)
- f1: mirando alrededor (captura "mirar") mientras la roca tiembla un pelo (siembra de la espuma).
- f95: cara de sorpresa a cámara tras tocar la roca con un dedo; la roca ya es de espuma (cambio a material amarillo de esponja, migajas, "boing").
- f150: lleva la roca sobre la yema del dedo (brazo en alto, la roca sigue la mano fotograma a fotograma), la deja detrás del camino y saluda a cámara (captura "saludar"). Final: parpadeo.
- Limitación: la roca se apoya sobre la mano justo a la altura del sombrero (casi lo roza).

## Pendiente / riesgos
- Ningún render completo hecho (solo fotogramas de prueba).
- El cambio piedra -> espuma es un corte de material con "pop"; si se quiere algo más suave haría falta una acción nueva reutilizable (mezcla de material).
- Los pajaritos y estrellas son pequeños en plano general; con --speed 1,5 duran ~0,6 s.
