# Policy — story-022 "Every IQ Level Catches the Drone" (ep019) — VEREDICTO: PASS (con avisos para metadata y Director)
Similitud léxica (`similar`): 0.18 (< 0.3; el más parecido es una farola, no una historia IQ). Fuentes: idea.json, ep019.py, director-visual.md (ronda 2 PASA), LICENSES, studio.py status --brief.

| # | Punto | Resultado |
|---|-------|-----------|
| 1 | Similitud / plantilla | OK en léxico. DUDA de concepto (no bloqueante): es la 6.ª entrada de la serie fija "Every IQ Level..." (013, 014, 016, 017, 019, 022) con la misma estructura de 5 niveles (-450 / -80 / 120 / 900 / 5469). Es una serie con premisa, objeto y gag distintos por episodio, pero el checklist cita "mismo escenario repetido con el mismo resultado / plantilla de storyline similar". Mitigación: 020 y 021 (no IQ) rompen la racha, y el objeto, el entorno y los gags cambian. Recomendación al Director: no encadenar otro IQ inmediatamente tras 022. |
| 2 | Valor original | OK. Gags y personaje propios; el mando colgado del cuello es una idea original. Formato "IQ levels" es meme genérico, sin copiar un vídeo concreto. |
| 3 | Título/desc/thumb | OK con lo que muestra: dron, mando, 5 niveles. Metadata: no prometer más que comedia; el dron es naranja/blanco y el mando ROJO (idea.json dice amarillo: obsoleto, no público; no usar "yellow"). |
| 4 | Ficción | OK. Comedia física claramente ficticia. |
| 5 | Marcas/personas | OK. Dron de primitivas propias (ep019.py build_drone): cuerpo blanco, cúpula naranja, hélices, luces; sin logos ni texto. Mando propio (build_ctrl), sin texto ni marca. Revisar que el diseño no imite un modelo comercial concreto: es genérico (cuadricóptero). |
| 6 | Licencias | OK. Poly Haven CC0 en LICENSES.json: rooftop_day, concrete_floor_worn_001, brown_planks_03, beige_wall_001, plastic_crate_01 (verificados). Kenney CC0 (assets/audio/LICENSES.txt). Música/SFX sintetizados propios (scripts/audio_gen.py). Mixamo (Adobe): clips Jumping, Falling Back Death, Throw, Angry, Climbing Up Wall, Surprised, Climbing A Rope, Laughing, Looking Around, Thinking, Button Pushing, Victory. DUDA: no he releído los términos vigentes de Mixamo (uso comercial en proyectos propios según se anotó en story-020/021); crédito en descripción por precaución. Nota: ep019.py usa más assets de los listados en idea.json (clips); la lista final está en provenance.json. |
| 7 | Divulgación | ai_use_disclosure=false: protagonista de dibujo y dron/mando de primitivas, evento imposible, no confundible con realidad (entorno con HDRI/texturas realistas, mismo criterio que 021). Metadata: mantener false y mencionar herramientas con IA en la descripción. |
| 8 | Anunciantes | OK. Caídas y golpes de zapato en clave cartoon, sin sangre ni lenguaje. |
| 9 | No dirigido a niños | OK. Sin tags infantiles ni "made for kids". |
| 10 | Variedad vs 3 anteriores (019 tiovivo IQ, 020 alcantarilla, 021 bolardo) | OK parcial. Hook (dron arriba + mando rebotando) distinto. DUDA: giro "la solución estaba en él / a la vista desde el frame 1" repite el de 013 (cuerda a la altura de su mano). El tipo de giro coincide; el estilo de hook y el objeto no. Aviso para el siguiente IQ: usar otro tipo de giro. |
| 11 | Tono | OK. Ligero. |
| 12 | Arco | OK. Planteamiento (dron fuera de alcance), escalada en 4 intentos, remate con pista visible desde el f1, bucle. |

## Acciones
- Metadata (final/metadata.json aún no existe): título/descripción en inglés, crédito Mixamo/Kenney/Poly Haven, mención de IA, ai_use=false, sin "yellow". Responsable: metadata/Director.
- Director: planificar el siguiente vídeo fuera de la serie IQ y con otro tipo de giro.
