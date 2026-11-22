# policy story-019 (ep016, "Every IQ Level Rides the Merry-Go-Round")

VEREDICTO: PASS (con 3 condiciones antes de `deliver`; ninguna bloquea el render)

Entradas leídas: final/metadata.json, anim/episodes/ep016.py (lín. 1-627 de 804; el resto solo por grep de cues), idea.json, reviews/*, assets/audio/LICENSES.txt, assets/polyhaven/LICENSES.json, channel/strategy/policy-checklist.md, `studio.py similar` (0.23).

## Checklist
1. Similitud: léxica 0.23 (< 0.3). Juicio de concepto: ver riesgo principal abajo. PASS con aviso.
2. Valor original: PASS. Tiovivo con centro fijo, pedal con causa visible, 5 gags propios; no reescribe obra ajena.
3. Título/descripción/thumbnail vs vídeo: PASS. Describe correctamente el vídeo mudo, los 5 niveles (-380..4800) y el centro quieto. Revisar de nuevo tras añadir caballitos (ver condición 2).
4. Ficción como ficción: PASS ("Fiction made with AI-assisted tools... nothing here is real footage"). Gags físicamente imposibles (disco arcoíris, barras-hélice).
5. Personas reales/marcas/copyright: PASS. Caballitos de carrusel estilizados, de primitivas, genéricos y sin marca: sin problema, siempre que no imiten un carrusel/personaje reconocible ni lleven logos o rótulos.
6. Licencias: PASS con anotaciones (sección Audio y activos).
7. Divulgación `ai_use_disclosure=false`: PASS con duda anotada (sección propia).
8. Apto anunciantes: PASS. Slapstick suave (peonza, caída rodando); sin sangre ni lenguaje. El clip se llama "Falling Back Death" pero solo es nombre interno; no se muestra muerte.
9. No dirigido a niños: DUDA. Declarado "not made for kids", pero parque infantil, tiovivo, colores vivos y dibujo atraen a público infantil. La designación final la decide YouTube/el creador; el canal ya mantiene el mismo criterio en las historias publicadas. Sin voz ni lenguaje dirigido a niños (CTA a adultos, tema IQ).
10. Variedad de formato: PASS con aviso. Los 3 anteriores publicados (story-016 vending IQ, story-017/ep014 bus IQ, story-018 piscina POV) incluyen 2 de 3 en plantilla IQ; ver riesgo.
11. Tono: PASS. Humor, sin angustia.
12. Arco narrativo: PASS. Planteamiento (disco girando, frame 1), escalada por niveles, final propio con causa visible (pedal, pilotos verdes) y cierre en bucle.

## Riesgo principal: contenido repetitivo / producido en masa
Frente a ep010 (campana), ep014 (autobús) y ep015 (piscina POV):
- ep016 comparte con ep010 y ep014 (y con ep008, 009, 011, 013) la misma estructura: 5 niveles rotulados en orden creciente de IQ, el primero falla de forma tonta, el último resuelve con la solución "lista" y remate de tada/yay en bucle. idea.json lo reconoce ("Plantilla repetible: 'Every IQ Level Gets On the ___'") y critic puntúa repetition_risk 4 y differentiation 6.
- El texto de la política que más se acerca: "characters are put in the same situation over and over again with the same outcome (i.e., using a highly similar storyline template across multiple videos)". Aquí la situación, el escenario, la física y los gags cambian de verdad (tiovivo con centro fijo, pedal, barras hélice), y el desenlace no es idéntico; por eso no lo considero incumplimiento. Pero el patrón (nivel bajo falla, nivel alto gana) sí es una plantilla; no puedo afirmar cómo la evaluaría YouTube (duda, no regla inventada). Los revisores miran el canal entero.
- Contra ep015 (piscina POV) no hay solape: formato, hook y giro distintos. Contra ep014 hay solape de estructura y de arquetipo del nivel 4800 (se sienta/queda quieto mientras el vehículo/disco hace de espectáculo); mismos clips Mixamo base (Running, Jumping, Sitting Idle) y mismos cues (tada, yay, clunk).
- Mitigación exigida: ver condición 1.

## Divulgación (ai_use_disclosure=false)
- Personaje de dibujo (klunk_toon) sobre rig Mixamo; parque con texturas fotográficas (Poly Haven aerial_grass_rock, HDRI greenwich_park) y docstring que lo llama "realista". Mismo criterio que story-013 y story-017, ya publicadas: acepto false.
- Razón: la escena no puede confundirse con real (protagonista de dibujo, disco que se vuelve arcoíris, barras como hélice, pilotos y pedal de dibujos animados). La regla del checklist exige true solo ante escena realista que no ocurrió.
- Duda honesta: el fondo fotográfico es lo que nos separa de "ilustración pura". No sé cómo lo interpreta YouTube en el límite; no es fallo del vídeo, pero queda anotado como decisión del canal. Si el caballito/estilo cambia y el personaje deja de verse de dibujo, revaluar a true.
- La descripción ya incluye aviso de ficción y "AI-assisted tools": coherente.

## Audio y activos
- LICENSES.txt: Kenney Impact/Interface Sounds, CC0. Cubre step, hit, clunk, creak, pop, tada (todos los usados de archivo). Sin atribución obligatoria.
- Resto de cues de ep016 (whoosh, huh, oof, hmm, wahwah, boing, bell, laugh, sigh, riser, yay): generados por `scripts/audio_gen.py` (síntesis propia; engine.md lo declara). Sin tercero. NOTA: LICENSES.txt no los lista; es una laguna documental, no de licencia.
- Música: assets/audio/music/ está vacío; no hay pista de música, luego no hay atribución CC que añadir. Si el montaje añadiera una, habría que anotarla y atribuirla.
- Poly Haven: CC0 (LICENSES.json). OK.
- Mixamo: no hay archivo de licencia en assets/mixamo/. La descripción acredita "Character animations: Mixamo." como en 013/017. No afirmo qué permiten los términos de Mixamo/Adobe para uso comercial en vídeo; sin verificar en este repo. Duda documental, igual que en las historias publicadas.
- final/provenance.json: no existe aún (final/ solo tiene metadata.json). Debe generarse antes de `deliver`.

## Condiciones (responsables)
1. Variedad entre publicaciones (Director): no publicar ep016 pegado a otro episodio IQ; intercalar un formato distinto (POV/objeto vivo) y vigilar la proporción de plantilla IQ en el canal. Si el siguiente lote vuelve a ser "Every IQ Level...", sustituir una idea por otro formato.
2. Caballitos (anim): al añadirlos, mantenerlos genéricos, sin marca, rótulo ni parecido con un carrusel/personaje reconocible, y sin cambiar la estética de dibujo. Re-pasar punto 3 (metadata) si cambian miniatura o descripción; esta puerta no cubre un diseño distinto del leído hoy (ep016 leído no los contiene).
3. Documentación (Director/qc): generar final/provenance.json con Kenney CC0, síntesis propia, Poly Haven CC0 y Mixamo; opcional añadir los cues sintéticos a LICENSES.txt. Marcar en metadata el punto "Music license" como "no music" una vez verificado.

No hay motivo de STOP/REJECT.
