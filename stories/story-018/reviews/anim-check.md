# anim-check — story-018 "The Pool With a Secret" (anim/episodes/ep015.py)

Formato: un solo nivel `LEVELS=[(0, l1)]`, `CUSTOM_CAMERA`, SPEED 1.0, 324 fotogramas (13,5 s a 24 fps), 13 planos de 1-2 s con cortes CONSTANT.
CAPTION literal "POV: the pool is empty"; TITLE "The Pool With a Secret".

## Mejora del crítico aplicada
- 3-6 s: un solo Looking Around (f48-110, sin Thinking); voces huh (f74) y hmm (f92).
- Pausa de un beat (11 fotogramas, f135-146) con el fondo hundido al máximo antes del primer boing.
- Exactamente tres botes (f153, f189, f228), boing / boing_hi / boing_top con pitch ascendente (x1, x1,5, x2,1). `boing_hi` y `boing_top` se han añadido a scripts/audio_gen.py (mismo muelle, pitch mayor).
- El tercer bote aterriza (f252) en la misma posición del trampolín (x=-3,3) y con la cámara idéntica a la del fotograma 1 (plano 13 = plano 1): bucle.

## Escenario
Piscina exterior vacía (hueco 5x4,8 m, fondo a 1 m bajo la cubierta), azulejos azul claro con juntas (nodo Brick, 30 cm), albardilla de piedra, escalerilla cromada en la pared del fondo, trampolín de 1 m (tabla + base + pivote), losas de cubierta y césped (PBR). Cielo = HDRI greenwich_park. Sin río ni muelle (entorno "mesa" vaciado; no se construye nada del río).
La cubierta está en z=-1,0 para que la tabla quede en z=0 y los pies pisen z≈0 en el trampolín.
Fondo = rejilla 64x56 con shape key "dip" (membrana anclada a las paredes), animada fotograma a fotograma; los azulejos usan coordenadas generadas, así que se deforman con la malla. Squash and stretch del protagonista con S.key sobre la escala de la raíz.

## Comprobaciones numéricas (script de prueba en el scratchpad, todos los fotogramas)
- Pies: el punto más bajo (pie, puntera y punta de zapatilla) coincide con el objetivo en los 324 fotogramas (0 desvíos > 3 cm): z=0,015 en el trampolín; sobre el fondo, superficie hundida + 0,03.
- Colisiones: 0 huesos dentro de tabla, base, albardillas, paredes, escalerilla ni bajo el fondo (primera versión: 8 casos en fondo por mal centrado del shape key y 1 en la tabla por la punta de zapatilla; corregidos).
- Sin pose sentada. run_level.py: sin "AVISO ENCUADRE" (la cabeza no entra en el 22 % superior en ningún fotograma impar; antes había 76 avisos).

## Fotogramas revisados (270x480, 8 samples, renderizados de uno en uno)
Planos: 1 (f1-34) general; 2 (35-58) punta; 3 (59-82) primer plano; 4 (83-99) sobre el hombro; 5 (100-127) salto; 6 (128-140) hundimiento; 7 (141-156) pausa + boing 1; 8-12 botes; 13 (f253-324) = plano 1.
- f1: hombre con afro y camiseta naranja a rayas andando sobre el trampolín, piscina vacía con azulejos y juntas abajo a la derecha, césped y cielo HDRI al fondo. Se entiende en 1 s.
- f20/f40: sigue andando hacia la punta; f62/f70: primer plano de la cara mirando hacia abajo (huh), ojos y afro legibles.
- f90: plano sobre el hombro, de espaldas, la piscina vacía y la escalerilla a la vista.
- f106/f108/f112: antes de saltar, párpados apretados (casi cerrados; en este tamaño se leen como rendijas, no cerrados del todo).
- f116/f124: en el aire sobre la piscina, pies lejos del fondo; f128: caída.
- f136/f139/f141: el fondo cede, las líneas de azulejo se curvan, él agachado con los pies sobre la superficie hundida.
- f148/f150/f152: ojos abiertos, cara de sorpresa, despega hacia arriba (squash a stretch).
- f166/f185/f186/f192/f214: botes 1 y 2, plano ancho con la membrana abombada/hundida y escalerilla; sin penetraciones.
- f222/f226: tercer contacto, plano medio, fondo curvado, cara feliz.
- f238/f249/f250: vuelo hacia el trampolín, cabeza dentro de cuadro.
- f253/f256: aterriza agachado sobre la tabla (clunk, yay f255); f270/f285: Victory con los brazos arriba; f300/f314: brazos abajo, de pie en x=-3,3, igual que f1 (bucle).

## Pendiente / límites
- No se ha montado el vídeo con sonido (solo fotogramas): los cues están anotados (steps, huh, hmm, whoosh, creak, hit, boing x3, clunk, yay, tada) pero no se han escuchado.
- Render de prueba a 8 samples: el aspecto final con más samples no se ha visto.
- Los ojos cerrados al saltar no se leen con claridad a 270x480 (slits); a 1080x1920 deberían verse mejor.
