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
