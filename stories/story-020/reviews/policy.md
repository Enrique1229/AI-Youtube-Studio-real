# Policy — story-020 "The Manhole That Hiccuped" (mini-historia muda, ep017)

VEREDICTO: PASS (con 3 avisos documentales no bloqueantes, responsable Director/qc)

Entradas leídas: idea.json, anim/episodes/ep017.py, reviews/director-visual.md (ronda 2 PASA), reviews/anim-check.md, market.json, `studio.py status --brief`, `studio.py similar`, assets/polyhaven/LICENSES.json, assets/audio/LICENSES.txt, policy-checklist.md. final/ está vacío (aún sin metadata.json ni provenance.json).

## Checklist
1. Similitud: `similar` = 0.13 (< 0.3; el vecino más cercano es la estatua de monedas, otro concepto). Concepto juzgado a mano: objeto urbano vivo + hombre que reacciona. Distinto de Bench (se aleja) y Pool (secreto). Sin plantilla repetida. OK.
2. Valor original: historia propia (tapa con hipo, susto que la cura, contagio al hombre). Arco claro. No reescribe obra ajena. OK.
3. Título/descripción/thumbnail: título "The Manhole That Hiccuped" coincide con lo que se ve. Metadata aún no existe: debe ser fiel (no prometer más de lo mostrado; el "objeto enorme" propuesto por el critic no está en ep017, solo bota y patito). PENDIENTE al crear metadata.
4. Ficción como ficción: cartoon toon con tapa viva. OK.
5. Sin personas reales, marcas ni personajes con copyright: bota, patito de goma, hidrante, papeleras, todo genérico/primitivas. OK.
6. Licencias:
   - Poly Haven: los 29 assets de LICENSES.json son CC0 (ninguna licencia distinta). Cubre HDRI dresden_square, cobblestone_floor_01 y el atrezo citado (street_lamp, planter, fire_hydrant, modular_street_seating, utility_box, etc.). OK.
   - Audio: clunk/hit/pop/step proceden de Kenney CC0 (LICENSES.txt, sin atribución obligatoria). Los cues hic, squeak y cymbal son síntesis propia (scripts/audio_gen.py, según anim-check). oof/huh/sigh/whoosh: no aparecen en LICENSES.txt ni en assets/audio/sfx (solo clunk, creak, hit, pop, step, tada); no he verificado su origen. DUDA documental, ver aviso A.
   - Mixamo: no hay archivo de licencia en el repo. provenance de story-019 afirma "uso libre en proyectos propios, comerciales incluidos; crédito en descripción", pero no lo he podido verificar aquí contra los términos de Adobe. Se trata como duda, igual que en 013/017/019. Mantener el crédito "Character animations: Mixamo." en la descripción.
   - Sin música (nada que licenciar).
7. Divulgación IA: estilo claramente no realista (toon, primitivas). ai_use_disclosure puede ser false; el escenario usa texturas/HDRI fotográficos CC0 pero la escena es evidentemente cartoon con tapa voladora. Si el render final sale fotográfico, marcar true (duda de criterio, no regla confirmada).
8. Apto para anunciantes: slapstick sin violencia, sin lenguaje. OK.
9. No dirigido a niños: humor slapstick con patito de goma; protagonista adulto, sin música infantil ni reclamo a niños. Riesgo bajo, pero no usar "kids/cartoon for children" en título, descripción ni hashtags. Duda: YouTube decide "made for kids" por señales propias; no inventó reglas.
10. Variedad: los 3 anteriores publicados son 017 (IQ), 018 (Pool, mini-historia), 019 (IQ). Este es mini-historia con escenario nuevo (plaza) y gag distinto; no repite hook ni giro (contagio del hipo). OK.
11. Tono: no angustia; humor ligero. OK.
12. Arco: planteamiento (hipo), escalada (bota, patito, susto), final propio (contagio + bucle). OK.

## Riesgo de contenido inauténtico a nivel de canal (vigilar, no bloquea)
- De los 10 Shorts del estado, 7 son "Every IQ Level ..." (011, 012, 013, 014, 016, 017, 019). Es una plantilla repetida: la política citada penaliza "highly similar storyline template across multiple videos". Story-020 reduce esa proporción, pero el canal en conjunto sigue sesgado. Recomendación al Director: no encadenar otro "Every IQ Level" justo después y alternar mini-historias con escenarios/personajes distintos.
- Mini-historias (015, 018, 020) comparten el esquema "objeto inanimado cobra vida + hombre Mixamo reacciona". Cuidar que la siguiente cambie de esquema (otro tipo de protagonista o giro).
- Mismo hombre y mismos clips Mixamo en todo el canal: aceptable como personaje recurrente, pero no es una variación visual.

## Avisos (no bloquean) y responsable
A. (qc/Director) Al generar final/provenance.json listar: Poly Haven CC0, Kenney CC0, síntesis propia (hic, squeak, cymbal) y declarar el origen real de whoosh, oof, huh, sigh (no figura en LICENSES.txt). Si alguno no es propio ni CC0, sustituirlo antes de entregar.
B. (Director/qc) Mixamo: duda documental sin verificar; incluir crédito en descripción.
C. (metadata) Descripción fiel a lo mostrado (tapa, bota, patito, hipo contagioso); sin afirmaciones de viralidad ni lenguaje infantil; ai_use_disclosure coherente con el aspecto del render final.
