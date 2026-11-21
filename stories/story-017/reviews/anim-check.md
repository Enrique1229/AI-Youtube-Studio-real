# anim-check — story-017 (ep014, "Every IQ Level Stops the Bus")

Archivo: anim/episodes/ep014.py. TITLE "Every IQ Level Stops the Bus", ONSCREEN "Every IQ level stops the bus", LABEL_STYLE "big",
niveles -450, -80, 120, 900, 5469. Duración a velocidad normal (fotogramas con +10 de cola): 108 / 82 / 122 / 147 / 164 = 623 f = 26 s;
a 1,5x ≈ 17,3 s (objetivo 18 s; dentro de 15-25 s).
Render: de uno en uno, 270x480, 8 samples; hojas por nivel en el scratchpad (ep014/sheet_l*.png y ep014/rsheet_*.png). Dos rondas de
corrección de cámara/coreografía (L2 y L4 rehechos). Comprobación final con `python anim/run_level.py -- anim/episodes/ep014.py <n> <carpeta> <f>`
en 3 fotogramas por nivel: ningún "AVISO ENCUADRE".

## Escenario (todos los niveles)
Calle de las afueras: acera de baldosas, bordillo, asfalto con raya central discontinua y raya de borde, casas al fondo, cielo y árboles
lejanos del HDRI del parque. Río, muelle, orillas, hierba cercana y árboles cercanos eliminados (no se ve agua en ningún fotograma).
Cuadro amarillo "STOP" (x 0-3,4; y 1,8-3,3) visible en el fotograma 1 de los 5 niveles (en L3 asoma abajo a la derecha). Marquesina con
cristal, techo, barandillas y banco; poste con señal BUS STOP.
Bus rojo de 10 m x 2,5 m x ~3,1 m (cuerpo biselado), ventanas oscuras, faros, cartel ámbar, 4 ruedas con radios que giran (giro = x/0,5),
cabeceo al frenar, puertas dobles deslizantes (lado cercano). Entra por la izquierda y sale por la derecha con S.key LINEAL; frena con
ease-out cuadrático (stop_path). (El color pasó de azul a rojo tras ver f1 de L1: el azul quedaba lavado.)

## Sonido (cues)
Bocina (horn) cada nivel más cerca: -20, -14, -8, -3, 0 dB. Whoosh fuerte en L1 (0 dB). "door" (pssh) en frenada de L3 y apertura de
puertas en L5; "tada" + "yay" en L5; voces huh/oof/hmm/wahwah/laugh/sigh según el nivel. Se añadieron "horn" y "door" a scripts/audio_gen.py.

## Nivel -450 (hojas: ep014/l1, rl1)
- f1: de perfil 3/4, ya agitando la mano izquierda hacia el bus; cuadro amarillo en primer plano; morro del bus aún fuera.
- f28 (clímax): el bus cruza ocupando el fondo (ruedas girando, banda blanca) y él gira por el viento y empieza a caer.
- f70 (final): tumbado de espaldas en la acera, pies en el suelo; el bus ya salió. El cuadro sigue visible.
Auditoría: limpia (cuerpo vs bus/marquesina/banco/poste). Pies: punta mínima +0,017 m.

## Nivel -80 (ep014/l2, rl2)
- f1: corriendo (de perfil, brazo derecho a cámara) detrás de la trasera del bus que pasa por delante del cuadro.
- f26 (clímax): lanzamiento (zapato rojo agrandado x1,7 sale de la mano al armar y vuela a la trasera; tonk flojo en f30), bus ya saliendo del cuadro.
- f60 (final): parado delante del poste con los brazos cruzados y cara de enfado, mirando a cámara.
Auditoría limpia; pies +0,017 m. Ojo: el impacto del zapato dura 1-2 fotogramas con la cámara ya en el borde del bus; en la hoja no se ve el zapato en el aire con claridad (pequeño a 270x480).

## Nivel 120 (ep014/l3, rl3)
- f1: de pie en mitad de la calzada, cámara en el borde de la acera; el cuadro asoma abajo a la derecha; el bus aún no entra.
- f36 (clímax): el bus frena a su lado, morro con faro y parabrisas a ~25 cm de su cara; él con cara de susto (sorpresa).
- f90 (final): el bus parado lejos del cuadro (a la izquierda), él temblando y mirando; "wahwah".
Auditoría limpia tras separar el morro 0,62 m; pies +0,018 m. Tamaño del personaje ~33 % de la altura.

## Nivel 900 (ep014/l4, rl4)
- f1: trepando el lateral de la marquesina (barras), plano con la marquesina y el cuadro.
- f60 (clímax): en el aire sobre el hueco entre la marquesina y el bus (cámara más alta, cielo detrás), el bus llega por la izquierda.
- f110 (final): de pie sobre el techo del bus, de cara a cámara riendo, el bus lo lleva fuera de cuadro (cámara le sigue, lente 72).
Auditoría: trepada limpia (tol. 4 cm en manos); salto y paseo: 1 fotograma (f51) con la punta del pie a <3 cm del techo de la marquesina
(oculto desde la cámara, sin efecto visible). Los pies están sobre un techo (2,5 m / 2,99 m), no sobre el suelo: la regla de z≈0 no
aplica ahí; en la trepada el clip arranca con los pies a +0,18 m. Nunca hay pose sentada.

## Nivel 5469 (ep014/l5, rl5)
- f1: pensando con la mano en la barbilla junto a la marquesina, cuadro amarillo visible.
- f100: ya plantado sobre el cuadro; el bus ha frenado a su lado con ease-out (puerta delantera frente a él); puertas abriéndose, "pssh".
- f140: de cara a cámara con los brazos en alto, puertas abiertas con luz cálida; "tada" y "yay" suenan en f107-109.
Auditoría limpia; pies -0,010 m (mínimo, dentro del límite -0,03). Personaje ~34 % de la altura en el plano final.

## Pendiente / límites
- Los fotogramas son a 270x480 y 8 samples; el acabado final (432x768+) no se ha visto.
- El bus no tiene interior ni conductor visible; al abrirse las puertas se ve un panel luminoso plano.
- No sube al bus en el 5469 (levanta los brazos delante de la puerta abierta).
