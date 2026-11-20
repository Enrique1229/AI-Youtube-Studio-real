# anim-check — story-015 (ep012, "The Bench That Walked Away")

Archivo: anim/episodes/ep012.py. (Ronda final: ver la sección "Correcciones finales" al final; los tiempos F_B0/F_B1 pasan a 111/149 y el carril del hombre a x=-9,1.) Un único "nivel" `LEVELS = [(0, l1)]`, 263 fotogramas = 10,9 s a 24 fps (SPEED = 1.0).
Rótulo: `CAPTION = ONSCREEN = "POV: The bench has other plans"` -> render_episode usa `--caption` (caja blanca arriba durante todo el vídeo). No aparece "IQ".
Cámara CUSTOM_CAMERA keyeada CONSTANT, 10 planos de 0,5-2 s: general / medio / primer plano del banco (parpadeo) / primer plano de la cara (sorpresa) / medio (salto) / persecución lateral / carrera-frenada-caída / cara (enfado) / árbol con sombra / remate.
Renderizado: 270x480, 8 samples, fotogramas uno a uno, 2 rondas de corrección (hojas de 15 y 16 fotogramas + 7 de verificación).

## Fotogramas vistos (ronda 2 salvo indicación)
- f3, f12 (carrera, plano general): hombre corriendo sudando hacia el banco, de perfil, ~37 % de la altura; sol (disco), árbol con sombra oscura y banco al fondo; pies en el suelo. OK.
- f24, f40 (derrumbe): gira, se sienta de golpe; sentado en el asiento, pies en el suelo. OK.
- f66 (primer plano del banco): dos ojos grandes a ambos lados de los hombros (únicos ojos del banco, f58-75), cara del hombre aún neutra -> sorpresa justo después. OK.
- f85 (cara): sorpresa (cejas arriba, boca en O), afro con margen bajo la zona del texto. OK.
- f104, f112 (salto del banco): salta, el banco gira media vuelta sobre sus patas estiradas, el hombre arranca. OK.
- f135 (persecución lateral): hombre corriendo en profundidad hacia el banco y la sombra. Hombre pequeño (~15 %): plano de transición de 1 s. Se ve el horizonte con edificios del HDRI (aceptable).
- f150-f172 (carrera final, frenada, caída; ronda 3 con cámara más cerca): hombre ~35 % de la altura, frena fuera de la sombra, se va de espaldas, banco ya sentado a la derecha y disco de sombra visibles. f166 confirmado sin aviso de encuadre. OK.
- f178, f190 (cara tumbada): primer plano desde arriba, cara de enfado, tumbado al sol. OK.
- f205/f212 (hueco): el banco (1,7 m, de dos plazas) se corre 0,5 m; el hombre salta y se sienta en su mitad. OK.
- f225, f246 (remate): sentados a la sombra, de frente, hombre ~33 % de la altura, cara feliz con sacudidas de risa. OK. (El clip Laughing es de pie, por eso la risa son sacudidas de Sitting Idle.)
- Cambios de la ronda 1: motivo del banco/árbol visible desde el plano 1 (árbol de Poly Haven island_tree_01, disco de sombra y perro tumbado a la sombra, según la mejora del crítico); el banco pasa de 1 a 1,7 m para que haya sitio real; plano 7 más cerca; cámara de cara tumbada desde los pies para ver la cara.

## Comprobaciones obligatorias del Director
1. Pies en el suelo: `ground_feet()` baja la raíz en cada fotograma de carrera hasta que el punto más bajo (LeftFoot/RightFoot/ToeBase) queda a z = 0,015 m. Antes de compensar el mínimo oscilaba 0,010-0,123 m (fase de vuelo); después, medido (f 2,4,...,20 y 110-152): 0,015 m en todos (tolerancia +-3 cm cumplida). Sin arco de raíz añadido sobre un clip que ya salta (no se usa Jumping).
2. Zona del texto: proyectando coronilla+afro (Head + 0,25 m) en todos los fotogramas 1-263: máxima altura = 26,5 % desde arriba (f57), ningún fotograma dentro del 22 % ni fuera de cuadro. `run_level.py` no emite AVISO ENCUADRE (la ronda 2 lo daba en f165, x=0,02; corregido con lens 24 y objetivo y 8,9).
3. Hojas con carrera (f3, f12, f135, f150), salto/giro (f104, f112) y caída (f158-f172), además de poses quietas.

## Sonido (S.cue)
boing (derrumbe, levantarse, salto, pirueta, salto final), whoosh (arranque, levantarse, salto, carrera del banco y del hombre, deslizamiento), step (trote del banco, cada 3 fotogramas, y deslizamiento), hit (derrumbe, aterrizaje del banco, caída de culo f175), pop (aparición y parpadeo de los ojos, aterrizaje final), creak (el banco se levanta/desliza), clunk (banco se sienta), slide_down (decepción tras caer), tada (remate).

## ISSUES
- scripts/render_episode.py solo pasa ONSCREEN con IQ; para un nivel sin IQ hay que usar CAPTION (hecho aquí: CAPTION = ONSCREEN). Sin cambios necesarios.
- Falta un clip Laughing sentado: risa hecha con sacudidas de raíz. Si se quiere uno real, descargarlo de Mixamo.
- No se ha renderizado el vídeo completo ni el montaje (solo fotogramas de comprobación a 270x480).

## Correcciones finales (bugs vistos en el render completo + voces)
1. Pierna atravesando el banco (~0:04): el hombre saltaba al carril y=2,0 (dentro del asiento) y el banco, ya de 1,7 m, giraba sobre él. Ahora salta hacia delante-izquierda (arco de 0,30 m, sin pasar la cabeza al 22 % superior) y cae en un carril x=-9,1, a 0,75 m del extremo del banco; el banco no empieza a girar hasta f106 (hombre ya fuera) y sale al trote en f111. Vistos f100-f118: el hombre rodea el banco por fuera, sin contacto.
2. Sentado en el aire (~0:08): el cuerpo caído se quedaba en y=Y_STOP-0.9 y se fundía a Sitting Idle sin asiento. Ahora el clip Falling Back Death se queda tumbado en el suelo (cadera a 0,13-0,21 m, sin teletransporte de raíz), vuelve al banco con un salto en pose de carrera (clip Running, f202-214) y solo pasa a Sitting Idle cuando ya está sobre el asiento (f212). Vistos f192, f200 (tumbado en el césped), f204 (arranca del suelo), f207 (en el aire corriendo, no sentado), f212 y f230 (sentado en el banco).
3. Auditoría de TODOS los fotogramas (1-263, huesos Foot/ToeBase/Leg/Hand de ambos lados contra asiento, respaldo y patas del banco con margen de 3 cm, en coordenadas del banco): 0 intersecciones. Cadera entre 0,25 y 0,72 m sin banco debajo: solo f23-24 (giro corriendo antes de sentarse, cadera 0,65-0,67 en pose de carrera, delante del banco), f167-173 (la caída de espaldas: la cadera baja 0,71 -> 0,28 y queda en 0,13-0,21 desde f175) y f204 (primer fotograma del salto en pose de carrera, 0,42). Ninguno es una pose sentada sin asiento; el único "sentado" en el aire que quedaba (f103, inicio del salto) se acortó adelantando el fundido a Running (f98).
4. Pies: mínimo 0,015 m en todos los fotogramas de carrera (f2-20, f108-152). Cabeza (coronilla+afro): mínimo 26,5 % desde arriba en los 263 fotogramas, 0 fuera del 22 % ni del cuadro; `run_level.py` sin AVISO ENCUADRE.
5. Voces sin palabras (una a la vez, >= 0,5 s): sigh al sentarse (f31, expresión feliz suave), huh al parpadear el banco (f66, sorpresa 0,7), sorpresa 1,0 al levantarse (f79), hmm al perseguir (f114, enfado 0,8), oof al caer (f176, enfado 1,0) y wahwah (f189), laugh en el remate (f217, feliz) con el tada. Parpadeos del protagonista en f10, 66, 124, 183, 224, 262.
