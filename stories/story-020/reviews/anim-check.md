# anim-check — story-020 "The Manhole That Hiccuped" (anim/episodes/ep017.py)

Render de prueba: 216x384, 5 muestras Cycles, fakeblender.sh. Fotogramas en `reviews/frames/` (24 fps, 300 fotogramas = 12,5 s + 10 de cola, SPEED 1.0, un solo nivel).
Cámara baja fija por plano (z=0,5, picado inverso, lente 50, DoF f/1.4) con cortes; el plano final repite el del fotograma 1 (bucle).

## Escenario (regla de producción alta)
- `env_real.build_plaza` (nuevo): HDRI dresden_square + adoquín PBR cobblestone_floor_01 + 19 piezas de atrezo Poly Haven CC0 (farolas 01/02, jardineras 01/02,
  boca de incendio, banco, asientos modulares, mesa de terraza, barriles, barrera de hormigón, caja de servicio, maceta, planta, cajas, bolsa, señal de suelo mojado,
  papelera) en primer plano (hidrante), medio y fondo, con escala y giro variados; bordillo + calzada + paso de cebra, 6 bolardos, 5 charcos, ~70 hojas, 3 palomas de
  primitivas que huyen con el primer hipo. Profundidad por desenfoque (DoF, foco por plano). Sin césped.
- Nada importante en el 15 % inferior (solo adoquín y la base del hidrante). El atrezo queda a los lados y detrás; la franja detrás de la tapa y la cara están libres.
- Descargados con fetch_polyhaven (1k): street_lamp_02, fire_hydrant, modular_street_seating, painted_wooden_bench, planter_box_02, planter_pot_clay, potted_plant_01,
  utility_box_01, concrete_road_barrier, wooden_crate_01, WetFloorSign_01, outdoor_table_chair_set_01, wooden_barrels_01, plastic_crate_01, trashbag, cardboard_box_01.

## Beats (fotogramas mirados; todos abiertos y revisados)
| Beat | inicio / clímax / final | Qué se ve |
|---|---|---|
| B1 gancho (1-40) | b1_inicio, b1_climax, b1_final | f1: tapa grande inclinada en el aire (cara inferior con nervios y cubo amarillo, legible) sobre columna de vapor, en el tercio central; hombre agachado a la derecha (Sneaking). f24: la tapa cae y levanta una nube. f40: tapa asentada en su marco (elipse fina), vapor residual. |
| B2a hipo 1 + bota (60-100) | b2a_* | f70: tapa arriba, vapor, la bota sale por el borde de la boca; f76: bota roja volando (se lee como bota) y el hombre salta atrás; f94: la bota ha rodado lejos de él, tapa asentada. |
| B2b hipo 2 + patito (104-160) | b2b_* | f108: tapa arriba y el patito sale; f124: patito en arco y el hombre volviendo de un salto; f138: plano medio, lo caza (se lee sin palabras). |
| B3 susto (146-210) | b3_* | f150: se agacha tras la papelera con el patito; f185: brazos arriba con el patito, la tapa congelada en lo alto sobre el vapor; f206: tapa plana y vapor en polvo (platillo). |
| B4 alivio + hic + bucle (210-300) | b4_* | f218: asiente, aliviado, cara a ~60 % del alto; f243: salta unos cm (hic); f262: tapa sube de nuevo y se lleva el patito; f300: agachado, tapa arriba: igual que f1 sin el patito. |

- Personaje 30-45 % del alto en planos medios (más pequeño agachado en el general). Cara del remate (f218/243) en el 55-65 %. Cabeza dentro del 78 % superior.
- Aviso de run_level "la cabeza sale del cuadro" en f195-201: falso positivo del comprobador (usa la cámara del plano anterior; el fotograma 198/200 se miró y el hombre está en cuadro).
- Sin contacto complejo: la bota/patito siguen arcos analíticos; la bota sale por el borde derecho de la boca para no cruzar la tapa; el patito sigue las manos solo tras cazarlo.

## Sonido (cues)
clonk (tapa cae, assets/audio/sfx clunk*.mp3, Kenney CC0), hic (nuevo, sintetizado: cae de tono), whoosh, pop, hit (bota), squeak (nuevo, patito), oof/huh/sigh (voz),
cymbal (nuevo, platillo), hic propio y clonk burlón al final. Un tono por beat; el único squeak es el del patito. Sintetizados en scripts/audio_gen.py (kinds `hic`, `squeak`, `cymbal`).

## Clips Mixamo usados (todos existentes)
Sneaking Forward (agachado inicial y final), Surprised (cada hipo y el propio), Jumping (saltos atrás/adelante), Picking Up (caza, agacharse), Victory (brazos arriba), Head Nod Yes (alivio), Looking Around (solo aporta el personaje).

## Pendiente / límites
- Se probó solo con baja resolución/5 muestras; el ruido del vapor y el DoF pueden variar en el render final.
- Hic del hombre: se ve por el salto de ~16 cm y la expresión; en el fotograma 243 el gesto de cara es pequeño (plano medio).
- La papelera importada trae un cubo marrón adicional pegado (parte del asset); no estorba a la cara ni a la tapa.
- No se probó el render completo (render_episode.py) ni el montaje de audio.
