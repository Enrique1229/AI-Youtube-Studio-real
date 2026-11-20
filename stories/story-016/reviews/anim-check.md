# anim-check — story-016 (ep013, "Every IQ Level Gets a Snack From the Vending Machine")

Archivo: anim/episodes/ep013.py. LEVELS = -450, -80, 120, 900, 5469; LABEL_STYLE="big"; ONSCREEN = "Every IQ level gets the snack".
Duración (fotogramas a 24 fps, +10 de cola): 138 / 144 / 130 / 136 / ~160 = ~708 -> 29,5 s -> ~19,7 s con el montaje a 1,5x.
Render de comprobación: 270x480, 8 samples, de uno en uno (hojas de 5-12 fotogramas por nivel, 2-3 rondas de corrección) + run_level.py en 3 fotogramas por nivel (inicio, clímax, final): ningún "AVISO ENCUADRE" en los 5 niveles.

## Escenario (cambio de variedad)
Rincón pavimentado: baldosas grises de 45 cm (procedural, Brick), bordillo, seto, farola (izquierda, al fondo) y papelera (izquierda, a >1 m de quien empuja). Río y muelle ocultos (agua oculta, tapa de hierba), no se ven.
Máquina roja (carcasa brillante, cartel SNACKS, cristal con reflejos, 3 baldas con espirales y bolsas de colores, huecos con la espiral vacía, panel con pantalla, teclado, lector, ranura de monedas iluminada en ámbar, trampilla de humo con bahía iluminada detrás).
La bolsa amarilla colgada (ladeada) y su gemela detrás se ven desde el fotograma 1 en todos los niveles; la ranura ámbar está iluminada desde el fotograma 1 (mejora del crítico).

## Cambios del Director aplicados
1. -80: ya no hay zapato. Se inclina (Picking Up) de perfil con cara y afro a cámara ante la trampilla y mete el brazo IZQUIERDO de lado por ella (IK; trampilla basculante), tira dos veces, duda, cara de enfado, "hmm", y se suelta cayendo de espaldas ("oof"). "tonk" = cue hit flojo al topar.
2. 900: salta ENCIMA y aterriza pesado en el techo; la máquina retumba y la bolsa baja UN escalón (POSE_C) y sigue colgada: clunk grande sin premio, "wahwah"; se queda arriba con cara de fracaso. 5469 es el único que la hace caer (sus dos bolsas). Idea.json del 900 NO se ha editado (no es mi salida): hay que corregir su texto (ISSUES).
3. Sonido: -450 sin ningún cue; -80 hit flojo + hmm + oof; 120 clunk pequeño + huh; 900 hit + clunk grande + wahwah (+whoosh del salto); 5469 pop (idea y moneda) + doble clunk grande + hit + tada + yay.
4. Protagonista: klunk_toon (apply, expression, blink con parpadeos cada ~2-3 s); una expresión por emoción (enfado/sorpresa/feliz/neutra).

## Fotogramas vistos
- -450: f1 (ya empujando el lateral derecho con las dos manos, cara casi de perfil, enfado), f30/f60 (empuja más fuerte, la máquina quieta), f78-84 (rebote), f96/f128 (tumbado de espaldas, cabeza dentro del cuadro, lejos de la máquina). OK.
- -80: f1 (ya inclinado ante la trampilla), f12-24 (brazo hacia la trampilla), f44/f66 (brazo dentro, cabeza y afro delante de la ventana, sin tocarla, cara hacia la máquina de perfil), f86-92 (tirón), f100 (sale despedido), f134 (tumbado, trampilla cerrada). OK.
- 120: f1, f30 (empuja el lateral de la máquina con las manos; la papelera ya no está de ese lado), f43-52 (la máquina se bambolea 1,8 grados, la bolsa se tambalea y baja medio centímetro), f119 (congelado mirando, ojos muy abiertos, sin parpadear). OK.
- 900: f1 (de pie, duda), f8-14 (sin hundirse: pies en z=0), f26 (en el aire, cabeza fuera del 22 % superior), f34-41 (llega al techo), f45 (agachado en el techo, impacto), f52-124 (de pie sobre el techo, bolsa más baja y ladeada, aún colgada). Continuo: no vuelve al suelo. OK.
- 5469: f1 (moneda ámbar brillando en la mano, de cara a cámara pensando), f46-62 (se gira, mano con moneda hacia la ranura), f66 (destello de la ranura), f76-92 (espiral gira, la segunda bolsa empuja a la colgada, caen las dos y se ven en la bahía por la trampilla de humo), f98-125 (se gira a cámara con los brazos arriba). OK.

## Comprobaciones automáticas (scratchpad/shots.py, todos los fotogramas)
- Cuerpo contra la caja de la máquina (manos con 3 puntos, pies y punteras, cabeza con radio 0,17 m, antebrazos, brazos, cadera, columna) y contra la papelera: -450 0 violaciones; 120 0; 900 0; 5469 0.
- -80: 1 fotograma (f87) con el antebrazo a 1 cm sobre el borde superior de la trampilla (x=-8,02, z=0,69) al soltarse; el resto del brazo dentro de la trampilla es intencionado.
- Pies bajo z=-0,03: 0 fotogramas en los 5 niveles (corrige el -450, que se hundía 0,2 m en el rebote, con lift_feet). Carrera: no hay carrera ni andar; los pies del salto compensan la altura de la raíz con el pie más bajo (z entre 0,00 y 0,03 al despegar/aterrizar).
- Nunca sentado sin nada debajo: no se usa Sitting Idle; el "agachado" es Picking Up (de pie, inclinado) y la squat del 900 ocurre sobre el techo.

## ISSUES
- Falta un clip de arrodillarse: el -80 usa Picking Up (inclinado), con el brazo izquierdo de lado por la trampilla (el antebrazo entra, el hombro queda al borde).
- stories/story-016/idea.json (y ideas/20261120-4/ideas.json) dicen que en el 900 "la bolsa cae" y que lanza un zapato en el -80: actualizar texto (responsable: director/idea).
- El nivel 900 usa plano más abierto (dist 5,6) para el salto al techo: el personaje mide ~28 % de la altura en ese nivel, 35 % en los demás.
- No se ha renderizado el vídeo completo ni el montaje.
