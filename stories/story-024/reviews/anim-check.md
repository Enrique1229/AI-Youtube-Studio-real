# anim-check — story-024 (ep022) "Every IQ Level Carries the Cake Through the Door"

Render de comprobación: 270x480, 6-8 muestras, CPU, envoltorio fakeblender (bpy del venv). Fotogramas en `stories/story-024/reviews/frames/` (a = f1, b = f41, c = f82 = último). Además se miraron hojas de 8-18 fotogramas por nivel (no solo 3), con atención a duplicados de personaje, cámara y transiciones. ep020.py no se ha tocado (se importa como módulo para reutilizar fachada, portal, hall, suelo, hombre fijo y utilidades).

Duración: 5 niveles x 82 fotogramas a 24 fps = 17,1 s a velocidad 1,0 (SPEED = 1.0; cumple <= 18 s).

## Comprobaciones de transiciones (bugs de ep020)
- UN solo actor visible en todos los fotogramas mirados de los 5 niveles; no hay protagonista duplicado (cada nivel instancia su propio hombre; los cortes/teletransportes del nivel 5 coinciden con el corte de cámara f49 -> f50).
- La cámara no se mueve de sitio: solo gira el objetivo (nivel 5) y nunca atraviesa al personaje (está a 2,6-4 m y 3 m de altura). Ningún primer plano de cara: la cara se ve a 3-4 m, pequeña, y solo en el nivel 1 (vuelta a cámara, ~1 s a distancia).
- Primeros fotogramas (a) y últimos (c) de cada nivel: hombre de pie, entero, en el cuadro; ningún objeto cruza la cámara.

## Nivel 1 (-400): portazo + nata en la cara
- n1_a (f1): el hombre llega con la tarta de nata grande con fresas (se lee de lejos), puerta abierta con el hall rojo/naranja detrás, farolillos inclinados por el viento.
- n1_x_f009: hoja cerrada de golpe (bang f8), la tarta pegada a la hoja, fresas por el aire.
- n1_b (f41): mancha blanca grande con 2 fresas y gotas en la puerta azul; tarta hecha torta en el suelo; hombre con nata en la cara (anillo blanco y fresa en el pelo) volviéndose a cámara.
- n1_c (f82): de frente, enfadado, nata en la cara, mancha y gotas en la puerta. Se lee sin sonido.

## Nivel 2 (-65): sujeta la hoja con la cadera
- n2_a: entra al hall con la tarta, hoja abierta. n2_x_f018: la hoja (bisagra derecha) apretada contra su cadera, él inclinado; hoja azul grande a la derecha.
- n2_b/c: moretón de nata blanco en la cadera derecha (visible), la tarta inclinada y una fresa cayendo. Lectura algo menos nítida que en los otros niveles (el hombre queda a la izquierda del hueco, en sombra suave).

## Nivel 3 (135): sujeta con el pie, el talon pillado
- n3_a: la tarta entrando al hall. n3_x_f022: hoja casi cerrada contra su pie/talon, él de lado con "ay" (Surprised) y la tarta tambaleando.
- n3_b/c: queda dentro, la hoja pegada a su espalda, tarta inclinada, una fresa se desprende (f52+). Es el nivel con la lectura mas floja (el pie no se ve claro: pose de Kicking vista desde atras y arriba); se acepta en esta ronda.

## Nivel 4 (1300): silla de tope + mantel
- n4_a: portazo (hoja cerrada ya en f5), tarta en el suelo despues. n4_x_f020: la silla agarrada y el mantel amarillo arrastrado con los vasos de colores volando.
- n4_b: hombre corriendo con la tarta apoyada en el suelo y la mesa ya sin mantel. n4_c: dentro del hall con la tarta intacta, silla calzando la hoja abierta, mantel hecho un monton y vasos por el suelo.

## Nivel 5 (9001): ventana oculta + cierre
- n5_a: portazo en f3; se queda quieto con la tarta. La ventana NO aparece en ningun fotograma hasta f26+ (fuera de plano: x 2,65-3,95; la fachada visible llega a x~1,7).
- n5_b (f41): la camara ha girado: ventana enorme con cortinas ondeando hacia fuera y la hoja abierta; el hombre llega corriendo (tarta ya dejada en la mesa a su paso, visible al borde en f30).
- f43-49: ventana cerrada de un golpe, cortinas caidas. n5_cut_f050: corte limpio a la puerta, sin viento, farolillos quietos, hombre con la tarta.
- n5_c (f82): ya dentro del hall con la tarta intacta (bell + tada). Sin Victory (subir la tarta la sacaba de cuadro).

## Escenario (detalle)
HDRI german_town_street + adoquin PBR + fachada de geometria con zocalo, pilastras, buzones, timbres, farol, maceteros, ventanas; atrezo Poly Haven (macetas, caja de luz, farola, boca de incendios, papelera, bolsa, banco, cajas, jardinera) en plano medio y fondo; fiesta con mesa de mantel y vasos, silla, 6 farolillos entre postes, confeti en el suelo, ventana grande con cortinas, hall interior con alfombra y cuadro, profundidad por DOF; nada importante en el 15 % inferior.

## Notas
- Sin ASSETS ni cambios de kit.py. Acciones nuevas: ninguna (todo con S.obj/S.key y clips Mixamo existentes).
- Las camaras de los niveles 2 y 3 (mas cerradas sobre el hall) y 4 estan keyadas por nivel; el nivel 1 y 5 usan el plano general.

## Correccion de intersecciones (2026-11-27) — anim/check_overlap.py
Queja del usuario: "se bugea y atraviesan cosas". Nueva herramienta `anim/check_overlap.py` (venv de blender-proto): recorre todos los fotogramas sin renderizar, evalua las mallas deformadas (armadura del actor, tarta, silla, mantel, vasos, hoja de puerta) con `mathutils.bvhtree`, encoge 1 cm las mallas animadas a lo largo de sus normales (contactos < 1 cm no cuentan), ignora suelo, alfombra, pies sobre escalones y parches de nata, y lista pareja de objetos + rango de fotogramas.
Uso: `/home/user/blender-proto/venv/bin/python anim/check_overlap.py -- anim/episodes/ep022.py <nivel|all> [--tol 0.01] [--step 1]`

**Antes** (detector, tol 1 cm): N1 11 parejas (tarta<->hoja f12-82, tarta<->zocalo f29-82, persona<->tarta f1-8, tarta<->silla/escalones...); N2 8 (persona<->tarta f1-82, hoja<->persona f5-82 con 7563 tri, tarta<->pared del hall); N3 11 (hoja<->persona, tarta<->pared izq., persona<->tarta); N4 58 (mantel<->vasos/mesa/zocalo/hoja, silla<->hoja, persona<->silla/mantel, tarta<->pared); N5 16 (tarta<->vasos/silla/persona, ventana<->persona).
Causas: tarta (r 0,575) agarrada a 0,26 m de las manos, dentro del torso; zocalo de ep020 cruzando el hueco de la puerta; hoja de 1,56 m cruzando al hombre cuando "la sujeta con la cadera/pie" (la cola de la hoja atravesaba el cuerpo); hall de 3 m con la tarta contra el fondo; tarta caida en el sitio donde queda el hombre; silla/mesa/mantel/vasos superpuestos; vasos que seguian avanzando tras aterrizar.

**Cambios en ep022.py** (solo este episodio): tarta mas pequena (CK 0,68) y a distancia constante de las manos (FWD) con `minf` (nunca a menos de X m de la raiz); zocalo partido en dos (hueco libre); hall reconstruido de 4,8 m (`deepen_hall`); mesa/silla recolocadas (TAB 1,45/1,05, silla 0,78/1,0), vasos sobre el mantel, mantel abierto por abajo; N1: tarta aplastada por delante de la manilla y cae a la IZQUIERDA (el hombre ya no pisa la nata), camara recentrada; N2/N3: la punta de la hoja toca la cadera/pie (hoja = 1,57 m, hombre a esa distancia de la bisagra), sin Angry (se queda en Pushing, el enfado va en la cara), camara baja (z 2,0) para ver la tarta por el hueco; N4 reescrito (108 fotogramas): tarta al suelo delante de el, silla llevada a la cara exterior de la hoja que se abre empujada por ella, mantel y vasos salen hacia el sur/este y aterrizan quietos, vuelve por la tarta y entra por el lado libre del hall; N5: vasos retirados de la mesa, tarta posada en el tablero, hombre empuja la hoja de la ventana desde su cara exterior (boca de incendios movida a x 4,30), cortinas menos hinchadas.

**Despues** (detector, tol 1 cm, todos los fotogramas): N1 0 · N2 0 · N3 0 · N4 0 · N5 0 ("OK: sin intersecciones" en los 5). Con tol 3 mm quedan restos puntuales de <= 56 tri en 1-2 fotogramas (N3 hoja~cuerpo f21-22; N4 mantel~silla f24 y fresa~cuerpo f62), no visibles.
Fotogramas revisados tras el cambio (324x576): N1 f1/f10/f82 (la tarta aplastada en la puerta y luego en el suelo a la izquierda, el hombre de pie sin tocarla), N2 f1/f30/f60/f82, N3 f1/f20/f45/f82, N4 f1/f22/f40/f62/f100 (silla calzando la hoja, mantel amarillo en el suelo, camara ancha ahora con tarta, mesa y hombre a la vez), N5 f1/f26/f41/f51/f70 (tarta en la mesa, hombre empujando la ventana, entra con la tarta). No hay personaje duplicado ni camara atravesando.
Nota: N4 dura ahora 108 fotogramas (4,5 s a velocidad normal) frente a 82 de los demas; render_episode/anim_build leen level.json, no hace falta tocar nada.
