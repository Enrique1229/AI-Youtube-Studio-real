# anim-check — story-024 (ep021) "Every IQ Level Carries the Cake Through the Door"

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
