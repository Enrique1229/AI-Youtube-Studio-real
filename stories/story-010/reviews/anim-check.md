# anim-check — story-010 "The Butter Who Learned to Skate" (anim/episodes/ep007.py)

Render de prueba a 270x480, 8 muestras, fotogramas revisados uno a uno (24 fps, 408 fotogramas = 17,0 s a SPEED 1.0; remate = guiño en f375, ~1,4 s de cola).
Estructura: 1 nivel (iq 0), ENV="mesa", CUSTOM_CAMERA=True, cortes CONSTANT forzados por plano, CAPTION=None, CTA="follow for more".

## Plató y paleta (distintos de ep002/ep003)
Mañana fría: ventana con luz azulada al fondo, azulejos azul claro, encimera de cuarzo blanco-azulado, armario claro. Sartén oscura, mantequilla amarilla saturada, molinillo marrón, tortita dorada. Luces frías (sol, relleno, contra, focos). Visto en todos los fotogramas.

## Planos y fotogramas vistos
| Plano | Fotogramas | Visto |
|---|---|---|
| Gancho (f1-35) | 1, 18, 34 | f1: mantequilla en el aire, ojos enormes, boca "oh", brazos arriba, ya en acción; f18: aterriza/patina con estela de charquitos; f34: sonríe (happy_face) pasando delante del molinillo. Cara >1/3 del ancho, nada cortado. |
| Plano abierto (f36-62, 1,1 s) | 45, 58 | Sartén, molinillo, mantequilla y tortita; se entiende el escenario. |
| Esquiva (f63-96) | 64, 80, 96 | Orbita alrededor del molinillo (cara asustada, se balancea); en la pasada trasera queda parcialmente tapada ~0,3 s. Cada giro más pequeña (s 1,0 a 0,65). |
| Regreso (f97-130) | 100, 115, 129 | Mantequilla más pequeña, frena en derrape (squash). |
| Pose patinadora (f131-172, 1,7 s) | 131, 150, 171 | Brazos en alto, pie levantado (cuchilla visible a un lado), ojos entornados orgullosos, sonrisa. |
| Charco quieto (f173-224, 2,1 s, sin sonido) | 173, 200, 224 | Charco liso, cara tumbada sobre él SONRIENTE; molinillo preocupado detrás. Silencio. |
| Tortita (f225-258) | 226, 242, 257 | Primer plano de la tortita mirando de lado, ojos grandes, boca "oh". Cara ~60 % del ancho. |
| Extensión (f259-322) | 259, 285, 320 | El charco se desliza, trepa y cubre la tapa; gotas por el costado; tortita sorprendida. |
| Final (f323-408) | 324, 372, 398, 407 | Tortita sonríe dorada (happy_face), mantequilla encima sonriendo; guiño en el último fotograma (ojo derecho cerrado, pupila oculta). |

## Reglas
- Derretirse = siempre alegre: la mantequilla sonríe en el charco y al cubrir la tortita (nunca cara de dolor). Se corrigió un fallo inicial donde la sonrisa se desvanecía por interpolación.
- Cara en el f1, 15 % superior sin caras (salvo f1 con la cara en el 18-20 %; ver nota), planos cerrados, caras de la mantequilla 30-45 % del ancho en pose y final.
- Materiales: pmat mantequilla con brillo suave y ligero subsurface; estela con rugosidad alta (con rugosidad baja reflejaba el borde de la sartén en negro).
- Sin personajes con marca registrada (cubo mantequilla, molinillo, tortita de tres capas).

## Notas
- Fotograma 1: la cara llega a ~18 % desde arriba, justo en el límite del 15 %.
- Sizzle de sartén no existe en el kit; se usa boing + slide_down al caer. Posible acción de sonido nueva: "sizzle".
- No se hizo render completo.
