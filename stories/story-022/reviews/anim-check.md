# anim-check — story-022 "Every IQ Level Catches the Drone" (anim/episodes/ep019.py)

Renders de prueba 270x480, 6 muestras Cycles, todos los fotogramas abiertos (`reviews/frames/`, 21 PNG). Cada nivel 4-6 s a velocidad normal (N = 150, 140, 135, 150, 190 fotogramas a 24 fps; con 1,5x el montaje queda en ~21 s). Cámara de seguimiento propia (CUSTOM_CAMERA), plano medio: personaje ~33 % del alto, pies al ~17 %, cabeza al ~50 %, dron a ~70 %. Nada de atrezo en el 15 % inferior. `run_level` no avisó de encuadre en ningún fotograma final. Clips solo de assets/mixamo/ (Jumping, Falling Back Death, Throw, Angry, Climbing Up Wall, Climbing A Rope, Laughing, Looking Around, Thinking, Button Pushing, Victory).

Escenario: azotea con HDRI rooftop_day, suelo PBR concrete_floor_worn_001 (losa con parapeto de obra, albardilla y barandilla de tubo), 15 piezas CC0 de Poly Haven repartidas en primer plano lateral, medio y fondo (2 aire acondicionado, conducto, tuberías, 2 cajas apiladas, 2 barriles, caja de cartón, caja de herramientas, escalera, maceta grande, 2 tiestos, mesa con sillas), más depósito de agua de madera con escalera de peldaños, caseta de acceso con puerta, tendedero con dos sábanas que se agitan, 3 antenas, 2 respiraderos, parches de brea, sumidero, charcos, hojas y cables; profundidad por DOF (f/2,8, foco en la cabeza). Nuevo `build_rooftop` en anim/env_real.py (ep016-018 intactos).

Mando: caja roja 36x22 cm (algo mayor que los 25x15 pedidos, para leerse en vertical) con pantalla, dos palancas amarillas, antena, luz que parpadea y cordón en V; colgado del cuello, muelle amortiguado calculado por fotograma sobre la aceleración del pecho. Visible en el pecho en el fotograma 1 de los 5 niveles. Dron: primitivas, ~70 cm, naranja y blanco, 4 hélices con disco difuminado girando, luces rojas/verdes parpadeando, patines.

## Nivel -450 (n1_*)
- a (f1): ya en el aire bajo el dron, mando rojo en el pecho, dron arriba a la izquierda. Se lee: salta para alcanzarlo.
- b (f66): segundo salto, mucho más alto, brazos abiertos, el dron justo encima de la cabeza (fuera de alcance).
- c (f150): tumbado de espaldas en el suelo, mando sobre el pecho, el dron sube hasta lo alto del cuadro. Remate legible.

## Nivel -80 (n2_*)
- a (f1): de pie con el zapato rojo en la mano derecha, dron en alto; se lee que va a lanzarlo.
- b (f36): el zapato (punto rojo) pega en el depósito, el dron esquiva girado (se ve la cara superior con las 4 hélices).
- b2 (f48): el zapato rebotado le da en la cabeza (rojo sobre el pelo), cara de sorpresa.
- c (f140): enfadado con brazos cruzados, el zapato en el suelo, el dron más alto. Límite: el zapato en la pared del depósito es pequeño (el depósito queda en el borde derecho).

## Nivel 120 (n3_*)
- a (f1): al pie de la escalera del depósito, mano en el peldaño, mando en el pecho.
- b0 (f40): a media escalera. b (f86): el dron pica casi sobre su cabeza (patines a un palmo), el mando se sacude. c (f135): agarrado, temblando, el dron vuelve a subir.
- Cambio durante la revisión: el clip Climbing Up Wall ya sube la cadera 1,2 m por sí solo, así que el depósito se hizo más alto (3,1 m) y no se añade elevación a la raíz. Límite: el personaje queda en ~30 % del alto, de tres cuartos (yaw 62) para que el mando se vea; el golpe del mando contra el peldaño se ve como sacudida más que como contacto claro.

## Nivel 900 (n4_*)
- a (f1): en el aire bajo el dron (arco), mando visible. b (f24): agarra el patín (manos arriba), el dron cae un poco por el peso.
- b2 (f62): colgado y arrastrado por la azotea con los pies a ras de suelo, las sábanas del fondo se agitan (gust en las bisagras). b3 (f100): sigue colgado delante del atrezo (cajas, aire acondicionado, caseta).
- c (f148): suelto y riéndose, el dron se aleja inclinado. Límites: el gag "tira de la barandilla" y el "pelo revuelto" no están (el pelo es del sistema de aspecto); las piernas apenas patalean (clip Climbing A Rope a 0,12x para fijar la cadera).

## Nivel 5469 (n5_*)
- a (f1): quieto, mirando alrededor, mando en el pecho, dron en alto.
- b (f108): plano más cerrado, mira abajo y sostiene el mando levantado a un lado; la palanca se empuja justo ahí (cara ~58 % del alto).
- b0 (f125): el dron desciende, la cámara empuja a primer plano (cara bajada, transición).
- b2 (f142): primer plano, brazos en alto con el dron posado sobre sus manos, mando de nuevo en el pecho; cara al ~62 % del alto. Remate (bell + tada + yay).
- c (f188): sigue con los puños arriba, el dron ya suelto y subiendo (bucle con el fotograma 1). Límite: el dron queda en la franja superior del 22 % durante el remate (los brazos en alto lo empujan allí; la cara sí está en el 55-65 %).

## Pendiente
- ISSUES: no hay un sonido de zumbido de dron con tono por nivel en audio_gen.py (se usa un cue "whoosh" repetido cada 9 fotogramas a -20 dB). Responsable: sound-designer / audio_gen.
- No se probó el render completo ni el montaje (render_episode.py), solo fotogramas sueltos.

## Ronda 2 (revisión del Director: azotea, dron, arrastre) — 21 fotogramas re-renderizados y vistos
- Fondo: la pared de lamas era el HDRI (aparcamiento nublado). HDRI girado a 90 grados (solo luz y reflejos) y, para la cámara, cúpula de cielo azul de día con nubes (solo rayos de cámara), skyline de 40 edificios lejanos de primitivas (copas 3-9 m, el cielo queda libre), calle lejana bajo el parapeto, sol 3,0. En todos los planos se ve ahora barandilla, ciudad al fondo y cielo azul.
- Dron: escala 1,45 (~1 m de envergadura) y vuelo a 2,4 m (antes 2,8): se ve con las 4 hélices, la cámara y las luces en todos los niveles; en el nivel 5 queda sobre las manos y la cabeza al ~60 %.
- Nivel 4: ahora cuelga del patín con los pies a ~0,4 m del suelo y balanceo de -24 grados mientras el dron lo arrastra; al soltar cae y se ríe (n4_b2, n4_b3).
- Límite: el skyline es una silueta gris de bloques (sin ventanas); el cielo cubre solo ~15 % superior en plano medio.
