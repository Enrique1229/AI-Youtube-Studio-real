# anim-check story-021 (ep018) — fotogramas de prueba 270x480 en reviews/frames/ (01..15, orden de la historia)
Rótulo fijo (CAPTION): "POV: the bollard wants pie". Duración: 312 fotogramas = 13 s. Renderizado con multi.py (una escena, varios fotogramas), no con run_level.py.

Lectura SIN sonido, fotograma a fotograma:
- 01/02 (1, 32): hombre sentado en el bolardo (1 m, acero verde botella con banda roja y franjas blancas reflectantes); DOS ojos pequeños con párpados y cejas en la banda miran arriba-derecha a la tarta (tarta inclinada sobre tabla, con vapor en espiral) en la ventana. Se lee el deseo.
- 03 (62) estirón 1: anillos telescópicos oscuros suben bajo el hombre sentado. 04 (92): se queda corto, la tarta sigue más arriba; los ojos miran hacia arriba. 05 (112): hace fuerza (ojos entornados, cejas hacia dentro; el temblor se aprecia poco en fotograma fijo, sí en movimiento).
- 06/07 (138, 152): 2.º estirón, llega al alféizar; el hombre gira hacia la ventana. 08 (168): tarta en sus manos, el alféizar queda con la tabla vacía. 09 (184): baja con la tarta.
- 10 (204) CORTE a primer plano: hombre de pie con la tarta (cara al ~55 % del alto), bolardo a su lado. 11 (224): la tapa se abre como boca con dientes y el bolardo se inclina hacia la tarta. 12 (239): tapa cerrada, tarta desaparecida (el bocado dura ~5 fotogramas: es rápido). 13 (252): él mira sus manos vacías (Shrugging). 14 (264): ojos entornados satisfechos.
- 15 (296) general: bolardo mirando otra vez a la ventana, OTRA tarta humeante (bucle con 01).

Avisos / límites (honestos):
- Sin clip Surprised sentado: el hombre usa Sitting Idle durante todo el estirón (agarrado a las rodillas) más cara "sorpresa" y temblor de raíz; no hay clip de sentado agarrándose. Standing Up de assets/mixamo parte del suelo, no sirve: el paso de sentado a de pie se oculta con un CORTE (fotograma 196), por lo que en el plano final no se repite la pose sentada del plano 1 (sí el bolardo, la ventana y la tarta).
- La boca: abre la tapa con dientes, pero el interior rojo se ve poco; el bocado es breve. Revisar en vídeo.
- Al inicio del Shrugging (f 246) el brazo queda extendido un instante (mezcla de clips).
- El hombre ocupa ~30-35 % del alto en generales (~25 % en el final, solo medio cuerpo); ojos del bolardo justo sobre el 15 % inferior.
- Escenario: fachada de geometría con muro PBR beige_wall_001 (descargado), ventana abierta con marco blanco, alféizar con goterón, contraventanas con lamas, maceta de geranios, interior con estantería y luz cálida, cornisa, zócalo, puerta, farol, bajante, hiedra, banderines, letrero, + 15 modelos Poly Haven (cajas, jardineras, barriles, farolas, hidrante...), HDRI dresden_square, adoquín PBR, profundidad con f/3.2. El suelo apenas se ve en generales por el encuadre vertical.

Ronda 2 (rediseño por riesgo de marca): bolardo verde/rojo/blanco sin amarillo, dos ojos con cejas (antes: amarillo y negro con un ojo). Mirada más hacia arriba. Bocado ~10 fotogramas con tapa abierta y el interior rojo con dientes visible; la tarta entra entera.
Corrección del brazo: las manos se mantienen en la pose de sujetar (Picking Up estirado, speed 0.35) hasta F_SHRUG+10 y luego funde a Shrugging con blend de 10; el hueco sin clip causaba la pose en T. Verificados 12-15 (f 238, 244, 252, 266) y 258: ningún brazo horizontal. Ya no se usa Head Nod Yes.
