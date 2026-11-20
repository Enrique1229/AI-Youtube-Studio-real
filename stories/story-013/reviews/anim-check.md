# anim-check — ep010 (story-013) "Every IQ Level Rings the Bell on a Tall Post"

Render de prueba: STUDIO_RES=270x480 STUDIO_SAMPLES=8, fotogramas en scratchpad/ep010/l<n>/ (2 rondas de correccion).
Duracion (fotogramas, 24 fps, antes del 1,5x): L1 116, L2 122, L3 128, L4 128, L5 150 = 644 (~17,9 s tras 1,5x).

Cambios por notas del Director (ronda 2): poste en x=-6,2 y camara mas cerrada (lente 44, a 6,5 m): el rio queda casi fuera; campana x1,3;
sin cuerda en niveles 1-4; en el 5469 la cuerda esta enrollada en el suelo detras del poste, hay plano corto (f12-30) y solo tras recogerla
queda unida a la campana y tensa. Mejora del critico aplicada: el 900 usa papelera (sin cuerda).

## Nivel -450 (116)
- f1: ya en el aire, brazos arriba bajo la campana, hueco claro hasta la campana. OK.
- f6/f27: saltos de 0,45 y 0,65 m; las manos quedan ~0,2-0,3 m bajo el borde. No llega. OK.
- f20: cuclillas al aterrizar. f100: brazos cruzados (Angry) mirando la campana, en cuadro. OK.
## Nivel -80 (122)
- f1: zapato en la mano. f33: el zapato (rebotado del poste) le da en la cabeza (corregido: antes pasaba por encima). f60: cae de espaldas. f105: tumbado con estrellitas, cabeza y campana en cuadro. OK.
## Nivel 120 (128)
- f1: ya trepando. f63: la mano llega al borde de la campana (dling debil, rayita pequena, cue bell a -15 dB). f80/f112: agarrado temblando, sudor y desliza un poco. Poste y cuerpo no se atraviesan (cuerpo a la izquierda del poste). OK.
## Nivel 900 (128)
- f1: empuja la papelera. f36: salto sobre ella. f48: encima. f61: manos en la campana, vaivén grande y rayas de sonido. f112: sonrie (Laughing) sobre la papelera. Sin cuerda. OK.
## Nivel 5469 (150)
- f1: mira alrededor, sin cuerda visible. f24: plano corto: el rollo de cuerda en el suelo junto al poste. f56: recoge el extremo, la cuerda ya une la campana con su mano. f86: tiron, campana a todo vaivén y rayas. f140: brazos arriba, cuerda tensa colgando hasta el suelo detras del poste. OK.

## Pendiente / limites
- El rio aun asoma un trozo pequeno al fondo derecha (L1-L5). Aceptable.
- El zapato lanzado es un objeto aparte (el personaje conserva sus zapatillas). Mixamo no permite quitarse un zapato.
- Cue "bell" anadido a scripts/audio_gen.py (sintetico); si hay assets/audio/sfx/bell*.wav se usa ese.
- Parches en anim/mixamo.py: prefijo de huesos autodetectado (mixamorig12:), play(start=), encadenado de >2 clips sin que la pista superior tape a las siguientes.
