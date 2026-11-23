# anim-check — story-020 "The Manhole That Hiccuped" (anim/episodes/ep017.py) — ronda 3 (QC: rehacer la lectura)

Render de prueba 270x480, 8 muestras Cycles. 294 fotogramas a 24 fps = 12,3 s (+10 de cola), SPEED 1.0. Fotogramas en `reviews/frames/` (16, numerados por beat).
Escenario (plaza, alcantarilla a ras del suelo, atrezo) y cámara general se mantienen. CAPTION = "POV: the manhole has hiccups" (rótulo fijo arriba, como ep015).

## Qué cambia respecto a la ronda anterior
1. Hipo legible: cada hipo = saltito seco de la tapa (0,85 m, sube 7 f y cae 6 f con clonk) + 4 puffs breves de vapor (ya NO hay columna continua) + sonido "hic" 2 f antes. Tapa quieta >= 12 f (0,5 s) entre hipos: hic en f22, 48, 74, 100 (cada 26 f) = ritmo regular.
2. Susto legible: el hombre deja el patito en el suelo (f96), se aleja agachado (Sneaking Forward, de espaldas, f100-136), vuelve cargando (Charge) y salta ante la tapa con los brazos arriba de cara a ella (Victory, f150). La tapa, a medio hipo, se queda congelada y temblando 14 f (0,6 s) y cae plana en SILENCIO (f177; no hay cue de sonido). Plano medio.
3. Remate en primer plano: cámara baja a 4 m, personaje ~55 % del alto, cara a ~58-60 % del alto. Alivio (Head Nod Yes + suspiro), pausa de ~1 s, hic del hombre (f212): saltito de 16 cm, Surprised y puff de vapor por la boca (3 esferas); la tapa detrás hace un saltito de 0,55 m y cae con clonk (f233).
4. Bucle: corte a general (f236), la tapa hace otro hic (f286) y queda en lo alto con él agachado a la derecha, igual que el fotograma 1. La bota desaparece en el corte a general (f100) y el patito en el corte a plano medio (f134).

## Fotogramas mirados (todos abiertos) y qué se entiende sin sonido
| Fotograma | Beat | Lectura |
|---|---|---|
| 01 (f1) | gancho | tapa grande tilteada en el aire sobre un puff, agujero negro en el suelo, hombre agachado a su lado: "algo sale de la alcantarilla" |
| 02 (f30) | hic 1 | la tapa salta de nuevo; sale una bota roja; el hombre salta hacia atrás |
| 03 (f60) / 04 (f74) | hic 2 | patito en arco; el hombre vuelve de un salto y lo caza |
| 05 (f96) | deja el patito | se agacha y lo deja en el suelo |
| 06 (f120) | se aleja | agachado de espaldas hacia el fondo, patito en el suelo, tapa quieta |
| 07 (f145) | carga | corre de vuelta hacia la tapa |
| 08 (f155) | susto | brazos arriba delante de la tapa, que sube con un puff |
| 09 (f165) | congelada | la tapa queda inclinada en el aire; él, con los brazos arriba, de cara a ella |
| 10 (f178) | cae plana | tapa asentada, él de pie en primer plano |
| 11 (f195) | alivio | pose relajada de perfil (asiente) |
| 12-13 (f214, f218) | hic | salta y suelta un puff gris por la boca |
| 14 (f226) | la tapa se ríe | la tapa asoma saltando detrás de sus piernas |
| 15 (f250) / 16 (f294) | general / bucle | mismo encuadre que f1; f294 = tapa en lo alto + hombre agachado |

## Límites / pendiente
- El puff de la boca se ve como un disco gris suave (sobre cielo blanco) y el "mano a la boca" del clip Surprised se queda en brazos al frente, no llega a la boca. La premisa se lee por el puff + el salto + el hic.
- No se probó el montaje de audio ni el render completo (render_episode.py). El comprobador de run_level puede avisar de cabeza fuera de cuadro por usar la cámara anterior (falso positivo conocido).
- El hombre en el primer plano está de perfil mirando a la tapa (no a cámara).

## Ronda 4 (revisión del Director: remate y bota)
- Remate de frente: yaw del hombre a 37 grados (hacia la cámara del primer plano) de f176 a f232; cara visible al ~50 % del alto (cámara a z=1,5 mirando a z=1,8, personaje ~45-50 %). La tapa queda detrás, a la izquierda: el aro se ve en el suelo y en f226 la tapa asoma saltando (0,85 m) con clonk. Alivio de frente (Head Nod Yes, f178-215).
- Hic enorme: salto de 42 cm (f212-220) y nube BLANCA opaca (3 esferas de 0,28-0,42 m de radio, 2-3 veces la cabeza) junto a su boca, delante de la fachada, que se disipa en 10 fotogramas (0,4 s). Justo después, Surprised de frente (f215+).
- Bota (f30): ahora sale por el lado izquierdo de la tapa y cae a la izquierda, lejos del hombre; ya no se solapa con él.
- Fotogramas regenerados: 02, 10, 11, 12, 13, 14 (270x480, 8 muestras). Límite: la parte alta de la nube cae sobre el cielo claro.
