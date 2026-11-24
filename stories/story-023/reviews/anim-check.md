# anim-check — story-023 (ep020), Every IQ Level Moves the Sofa Through the Door
Archivo: anim/episodes/ep020.py. 5 niveles x 72 fotogramas + 10 de cola = 3,4 s cada uno; total ~17 s con SPEED = 1.0 (<= 18 s).
Fotogramas (270x480, 8 muestras): stories/story-023/reviews/frames/ (n1_a_inicio ... n5_c_final, mas n5_b2_puerta_doble). Todos mirados.

## Escenario
Fachada de geometria (ocre/crema con textura PBR), portal de piedra con montante, escalones, buzones, timbres, farol, numero de casa, dos ventanas con maceteros y contraventanas, bajante, hall interior con alfombra y cuadro; suelo de adoquin PBR; HDRI german_town_street solo para luz (no se ve). Atrezo Poly Haven: 2 macetas (potted_plant_02) con arbusto denso de primitivas, power_box_01, utility_box_01, 3 cardboard_box_01, potted_plant_04, farola, hidrante, papelera, bolsa, banco, cajas. Camion de mudanzas de primitivas al fondo derecho. Profundidad: DOF f/3.5. Color: sofa rojo, puerta azul, fachada calida, camisa verde.

## Cambios clave
- Plano cercano: hombre ~50 % del alto, camara a 2,7 m con picado suave; pies al ~17 % del borde inferior, nada importante en el 15 % inferior.
- Fotograma 1 de cada nivel: sofa encajado (rojo, sofa_02 recoloreado) y hombre empujando.
- Solucion oculta: hoja izquierda fija, sin tirador, tapada por la maceta (arbusto la cubre; la barra no se ve en n1-n4). Maceta derecha a modo de pareja. La barra solo aparece en n5.

## Por nivel
- N1 (-300): a) sofa encajado, hombre empujando de espaldas. b) f25: sofa rebotado como muelle, hombre estampado contra la pantalla (cara aplastada, ojos grandes), desenfoque de cerca. c) f66: sofa de nuevo encajado, el hombre acaba de resbalar fuera del cuadro. Squash visible en sofa y hombre (cue hit/oof/slide_down). Aviso de encuadre solo en el vuelo (f13-19).
- N2 (-60): a) empuja. b) f24: astilla clara asoma del borde de la hoja fija, polvo, el hombre se inclina con el hombro. c) f66: brazos cruzados enfadado mirando a camara, sofa atascado.
- N3 (150): a) empuja. b) f40: sofa tumbado de lado dentro del hueco, hombre se echa hacia atras sorprendido mirando a camara (casi cae encima). c) f66: sofa dentro, hombre encogido de hombros.
- N4 (1200): a) empuja. b) f22: hombre agachado sacando la hoja abierta de las bisagras (pasadores dorados saltan). c) f66: hoja apoyada contra la pared, sofa dentro, el hombre mira el hueco de frente.
- N5 (7000): a) empuja. b) f46: macetas fuera, barra de laton grande con destello, el hombre tira de ella. b2) f57: las dos hojas abiertas de par en par, sofa entrando; ding (bell). c) f66: Victory mirando a camara.

## Avisos / limitaciones
- El hombre empuja de espaldas a camara (el sofa entra en el edificio); la cara se ve en las pausas y remates (n1 b, n2 c, n3 b, n4 c, n5 b2/c).
- Hoja izquierda abierta a 160 grados queda casi fuera de cuadro (borde izquierdo); camion al fondo apenas asoma por el borde derecho (la fachada lo tapa).
- Arbustos de las macetas son primitivas (aspecto de hojas lisas), aceptable a esta distancia.
- Efectos de sonido solo anotados con S.cue (huh, boing, hit, oof, creak, clunk, bell, tada, etc.). No se ha renderizado el montaje completo ni el audio.
