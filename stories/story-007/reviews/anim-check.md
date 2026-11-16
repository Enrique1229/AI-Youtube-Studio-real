# anim-check — story-007 "The Little Bubble Who Stayed" (anim/episodes/ep004.py)

Formato: objetos vivos, ENV="mesa", CUSTOM_CAMERA, SPEED=1.0, sin rótulo, CTA "follow for more". 400 fotogramas = 16,7 s. Un nivel.
Fotogramas de prueba a 270x480 / 8 muestras (render completo NO hecho). Todos mirados.

## Planos (cortes CONSTANT) y qué se ve
| Fotograma | Plano | Visto |
|---|---|---|
| 1 | A (0-1,2 s) | Esponja amarilla con poros y base verde, cara "wide"; la pompa ya emerge encima, pequeña. Tenedor con puntas arriba y ventana al fondo. Nada cortado. |
| 12 | A | Pompa grande, translúcida con tinte rosa/azul/verde, sonrisa (happy_face), flota sobre las puntas. Esponja preocupada mirándola. |
| 36 | B (tenedor) | Pompa sonriente a 1/3+ del ancho, justo sobre las puntas. |
| 46 | B | Roce: pompa aplastada sobre las puntas, cara asustada (wide). |
| 60 / 80 | C (lápiz) | Aparece el lápiz amarillo con punta; la pompa asustada tiembla. |
| 88 | C | Casi-roce: la punta toca el borde derecho de la pompa y esta se aplasta. |
| 112 | D | Esponja en plano cerrado, cara preocupada mirando a la derecha. |
| 150 | E | Pompa feliz delante de la ventana, mira a cámara (pausa antes del fracaso). Lápiz esperando. |
| 184 | E | Clímax: la punta del lápiz entra en la pompa, que sigue sonriendo. |
| 200 | E | Silencio: gotitas translúcidas esparcidas, lápiz quieto. Sin pompa. |
| 240 | F | Esponja con ojos caídos y cejas tristes, quieta, cara de pena. |
| 300 | F | Fin del único estrujón; asoma la pompita sobre la esponja. Esponja ya con sonrisa (happy_face). |
| 330 | F | Pompita sonriente posada en la cabeza de la esponja; ambas sonríen. |
| 360 / 389 | F | Guiño de la pompita (ojo cerrado con pestaña) mantenido hasta el último fotograma (~1,7 s de final). |

## Calidad
- Caras de pompa/esponja >= 1/3 del ancho en los momentos clave; 15 % superior sin caras; planos cerrados; el plano abierto no se usa (solo A, ~1,2 s, ya cerrado).
- Pompa: Principled con Transmission 0,85, IOR 1,08, tinte arcoíris suave (pmat), película fina si la versión de Blender la ofrece. Nunca blanca opaca.
- Esponja: S.pmat con bump + poros + base verde. Sonrisas con happy_face; cejas neutras/preocupadas según el gag.
- Se reutiliza el cambio de cara por swap (cara móvil / cara feliz) para no reactivar la boca oculta.

## Observaciones / límites
- Se baja la energía de los 3 focos de la mesa (14) para que la pompa se vea contra la pared; la ventana es un panel azul con emisión 1,4. Sin acción nueva en kit.py.
- Con luz de ventana detrás, la mitad inferior de la pompa refleja el azul del cristal (aceptable, la lee como pompa).
- La pompita final usa escala 0,6 (no 0,4) para que su cara y el guiño se lean en el plano.
- Sin audio revisado; cues: boing, pop (nacimiento), boing (roce), whoosh, creak, pop (estallido), splash suave, slide_down, pop+tada (pompita).
