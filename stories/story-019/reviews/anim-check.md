# anim-check story-019 (ep016, idea b20261122-3-i03)

Render de prueba: bpy del venv, CPU, 360x640, 10 muestras. `anim/run_level.py` ejecutado en los 5 niveles (fotograma climax): ninguna salida con "AVISO ENCUADRE". Comprobación de encuadre con el mismo criterio sobre todos los fotogramas (paso 2) en L2 y L5: sin aviso. Cabeza siempre bajo el 78 % superior y dentro de x 0.02-0.98 (máx. y medida 0.73).

Mejora del crítico aplicada: la aceleración tiene causa visible. El taburete del centro es un pedal: al sentarse la placa se hunde 3 cm (clunk), los 8 pilotos pasan de rojo a verde (ding), y solo entonces el disco acelera (riser); el banderín se agita. Banderín rojo/blanco (1,05 m) y pelota amarilla con cinturón negro (r 0,32) grandes, sobre un pescante en el eje; las barras rojas/blancas contrastan con el césped. Rotación con motion blur (arcoíris real en el pico), cámara fija.

## Auditoría automática por fotograma (dentro de ep016.py)
- Cuerpo (huesos con grosor) contra barras, asas, banco, taburete, poste y pelota, en cada fotograma: los 5 niveles "limpia". Roces permitidos y anotados: mano/brazo en la barra (L1 golpe, L3 pegado), cadera en banco y taburete al sentarse.
- Pies: sobre el suelo o el disco la punta/tobillo más bajo queda a +0.020 m sobre la superficie (z mundo mínima +0.020; en la placa hundida -0.005; límite -0.03). Tumbado (L2): hueso más bajo +0.014.
- Emparentado: la raíz va como hijo del disco; error en planta entre la ruta prevista en el mundo y la posición real tras girar el disco: 0.0000 m (L3 0.016 m por el temblor) con el disco girado 636-3227 grados.

## Fotogramas vistos (stories/story-019/reviews/frames/)
- L1 -380: f1 corre ya junto al disco, a la izquierda; f28 pasa junto a la barra que le llega por detrás, gira (peonza); f100 de pie, enfadado, mirando a cámara. Sin sentarse.
- L2 -70: f1 corriendo pegado a una barra; f52 colgado de la asa, cuerpo horizontal como bandera; f118 tumbado en el suelo fuera del barrido de las barras, dentro de cuadro.
- L3 200: f1 de pie fuera del disco; f44 sobre el disco, pegado a la barra, pie en el disco; f118 sigue pegado y temblando, el banderín casi quieto.
- L4 950: f1 corre al borde; f36 salto con aterrizaje; f114 sentado en el banco azul del disco (apoyo real), riendo.
- L5 4800: f1 mira el centro desde fuera; f124 sentado en el taburete-pedal, pilotos verdes, arcoíris fundido, barras abatidas como hélice; f182 el disco frena, barras de vuelta.

## Límites reconocidos
- La auditoría usa cápsulas de huesos, no la malla: un roce de ropa/pelo puede escaparse.
- L5: el disco gira a 0.7 de la velocidad de los otros niveles mientras espera, para que pueda cruzar entre barras sin atravesarlas (la entrada a pie sobre un disco a plena velocidad chocaba con las barras).
- Un solo frame de pose de Climbing Up Wall (L3), sin ayuda de pies en la pared; la pose se lee pero es pequeña en cuadro.
- Duración (24 fps): 4.7 / 5.2 / 5.2 / 5.0 / 7.8 s = 27.8 s, 18.5 s tras el montaje 1.5x. Sin "Victory" ni "Laughing" de pie: sentado no hay clip equivalente; se usan voces (laugh, yay) y expresiones.
- No se ha probado el montaje completo con música (anim_build), solo los niveles.

## Ronda 2 (revisión visual del Director): cámara rehecha
- Cámara de plano medio con seguimiento (`cam_follow`): posición y focal por claves, mirada que sigue a la cabeza suavizada. Personaje ~30-45 % del alto en los planos clave; empujes a cara en el remate de cada nivel (focal 75-85) y variedad de posición entre niveles (centro, izquierda, derecha, lateral). Nivel 5: medio en el pico (disco entero legible) y cierre en primer plano de su cara tranquila con banderín y pelota al viento (las barras quedan abatidas para no tapar).
- Césped ampliado a 4000 m: la costura recta del fondo desaparece; la picada mantiene el horizonte fuera de la franja del texto salvo en planos de cierre (se ve el fondo de árboles, sin línea de corte).
- Animación sin cambios (salvo que en el nivel 5 las barras ya no vuelven a subir al frenar). Auditorías repetidas: los 5 niveles "limpia", pies +0.020, emparentado 0.000 m; framing_check (mismo criterio que run_level, fotogramas con paso 2) sin AVISO ENCUADRE en los 5 niveles.
- Fotogramas regenerados (inicio, clímax, final) en frames/. Notas: los fotogramas iniciales siguen mostrando el personaje algo más pequeño (entra corriendo); L1 f100 y L5 f186 son planos cerrados.

## Ronda 3
- Plano final del nivel 5 reencuadrado (solo cámara del tramo f_peak+22 en adelante): cara tranquila hacia el 45 % del alto, banderín ondeando y pelota encima. framing_check sin aviso.
- Tiovivo clásico: de la cima de cada poste sale una barandilla curva de tubo (12 tramos, arqueada) hasta un cubo blanco en el eje; 4 banquetas bajas de colores (amarillo, cian, magenta, verde; 0,30 m) en el borde entre barras; todo gira con el disco. Sin techo cónico (tapaba al personaje desde la cámara alta). En L3 se omite la banqueta del sector del aterrizaje, en L4 la que solapa su banco y en L5 no hay banquetas (cruza el borde entre barras); las barandillas están en todos.
- Auditoría de cuerpo contra barras, asas, barandillas, banquetas, banco, taburete, pescante y pelota repetida en los 5 niveles: "limpia" (solo roces permitidos ya anotados). Sin cambiar animaciones. 15 fotogramas regenerados.
