# anim-check — ep011 (story-014) "Every IQ Level Reaches the Picnic Blanket"

Render de prueba: STUDIO_RES=270x480 STUDIO_SAMPLES=8, hojas en scratchpad/ep011/sheet_l1..l5.png (fotogramas en l<n>a/). 2 rondas de correccion + un ajuste menor del L2.
Duracion (fotogramas, 24 fps, antes del 1,5x): L1 138, L2 146, L3 152, L4 138, L5 160 = 734 (~20,4 s tras 1,5x).
Escenario: ENV parque, cámara fija elevada (lente 30, a 4,7 m, mirando algo hacia abajo); el río queda tapado (agua y muelle ocultos, suelo de hierba encima) y no se ve.
Barro: malla elíptica con relieve + material propio (marrón oscuro, rugosidad variable, capa húmeda, bump). Manta: cuadros rojo/blanco, esquina doblada levantada hacia el charco y cesta de mimbre, visibles desde el fotograma 1 en todos los niveles. Banco: tablas Poly Haven brown_planks_03 (coordenadas de objeto).

## Nivel -450 (138)
- f1: ya corriendo, entra por la izquierda; manta con esquina doblada y cesta, charco y banco en cuadro. OK.
- f30: en el aire con las piernas abiertas sobre el charco, corto de la manta. f44: aterriza en cuclillas en medio del barro (salpicadura de gotas, grumos, ondas). f62/f100: hundido hasta las rodillas, mira alrededor. OK.
## Nivel -80 (146)
- f1: coge la piedra. f22/f45/f72: la piedra vuela en arco y desaparece en el barro (ondas, sin cue de sonido); la 2ª y 3ª caen más cerca de la manta. f100/f142: brazos cruzados (Angry) mirando el barro; las ondas quedan dentro del charco. OK.
## Nivel 120 (152)
- f1: empuja el banco (de lado a cámara) hacia el charco. f30: el banco entra inclinado y se hunde con splash. f52: salto de un solo impulso hacia el banco. f66: sentado de cara a cámara en la barra del respaldo, que asoma del barro. f90: bombilla de gran idea. f148: se ha hundido unos 20 cm más con el banco. OK.
## Nivel 900 (138)
- f1: corriendo. f30: salto largo sobre el charco. f44: cae en el borde de la manta. f56: la manta resbala hacia el charco con él encima, se cae hacia atrás. f70/f100/f125: tumbado sobre la manta, que queda apoyada (z 0,03) sobre el barro, con splash y ondas; la cesta queda aparte de su cuerpo. OK.
## Nivel 5469 (160)
- f1: de pie en la orilla, esquina doblada visible. f36: piensa/mira. f55: agachado, la mano toca la punta de la esquina. f72: tira y da un paso atrás: la manta va pegada a la mano, inclinada, DESLIZANDO por encima del barro (sin atravesarlo), con la cesta encima. f88: la suelta y llega plana a su orilla. f110: saluda (Waving). f148: sentado sobre la manta limpia, charco vacío. OK.

## Pendiente / limites
- Fotograma 1 de L1/L4 el actor entra por el borde izquierdo (a medio cuadro): es correr dentro de cuadro.
- L5: el paso atrás es un desplazamiento de raíz mientras el clip Picking Up se incorpora (ligero patinaje de pies, no visible a la escala del cuadro).
- Barro: el relieve y el brillo se aprecian bien a 540x960; a 270x480 se ve más plano.
- Cues usados del catálogo: boing, splash, drain, hit, clunk, whoosh, slide_down, pop, tada (ninguno nuevo; las piedras del -80 caen sin cue a propósito).
- Hoja del L1..L5 en scratchpad/ep011/sheet_l<n>.png (6-7 fotogramas por nivel, inicio/clímax/final).
