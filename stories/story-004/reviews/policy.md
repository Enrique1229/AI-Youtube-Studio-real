# Policy Guardian — story-004 (ep001 "Cada nivel de IQ cruzando un río") — 2026-11-16

VEREDICTO: PASS (condicionado a las 4 correcciones de abajo antes de `deliver`; ninguna es bloqueante).

Entradas leídas: episode.md, reviews/director-visual.md, market.json, anim/mocap/CLIPS.md, channel/reference/agbaps-bees-analysis.md, scripts/audio_gen.py, channel/strategy/policy-checklist.md.
No ejecutado: `studio.py similar` (no estaba en las entradas). Con una sola historia de este formato no hay similitud interna que medir; se juzga abajo el riesgo de serie.

## Checklist (12 puntos)
1. Similitud con vídeos previos: sin dato léxico (no ejecutado). RIESGO DE SERIE: "niveles de IQ + 5 gags + remate ingenioso" es una plantilla. Si los siguientes episodios repiten estructura, tipo de giro y escenario, encaja en "same situation over and over with the same outcome" y "templated storylines". Ver condición C4.
2. Valor original: PASS. Gags propios (hundirse, quedarse en el aire, tablón, barca, vaciar el río), personaje por semilla, escenario procedural. Sin reescritura de obra ajena.
3. Título/descripción/thumbnail vs vídeo: pendiente (no hay final/metadata.json). Condición C1.
4. Ficción como ficción: PASS. Dibujo animado, gags imposibles (flotar en el aire, vaciar un río con una palanca).
5. Personas reales, marcas, personajes con copyright: PASS en lo declarado (humano de dibujo genérico). No verificado fotograma a fotograma, pero el Director revisó el v6 completo sin anotar nada de esto.
6. Licencias: PASS.
   - Mocap CMU: "CMU places no restrictions on the use of the original dataset"; uso comercial permitido. Conversión BVH de B. Hahne (2010), copia en github.com/una-dinosauria/cmu-mocap: la licencia de esa copia no consta en CLIPS.md. DUDA menor; la fuente primaria es CMU. Crédito en descripción: obligatorio por nuestra política aunque CMU no lo exija.
   - Música y efectos: sintetizados con numpy en scripts/audio_gen.py (`sneaky_music`, `ambience`, `sfx`). Sin grabaciones, samples ni modelos de terceros. Sin licencias que gestionar. La melodía es aleatoria por semilla (escala menor armónica sobre patrón de bajo caminante), sin citar obras existentes. Riesgo de Content ID: bajo, no nulo (los sistemas automáticos pueden dar falsos positivos con audio genérico; no es una regla, es una posibilidad).
7. Divulgación de IA: personaje y escena claramente no realistas (dibujo animado, mocap sobre rig 3D, gags imposibles) => `ai_use_disclosure` puede ser false según la checklist. DUDA: el entorno (`env_rio_real`: cielo físico, ~35 000 briznas, AgX, profundidad de campo) tiene aspecto fotorrealista. La escena no "ocurrió" ni es creíble como real, pero la política vigente no define el límite con precisión. Recomendación prudente: marcar true si el thumbnail o un fotograma puede leerse como imagen real. Decisión final del Director.
8. Apto para anunciantes: PASS. Comedia física sin sangre; "hundirse" y "cae al agua" son slapstick sin daño mostrado. Nivel de IQ -450 es burla de un número, no de personas.
9. No dirigido a niños: DUDA. Comedia de dibujo animado de estética amable puede ser percibida como contenido infantil. La política de "made for kids" es declaración del creador al subir; el audiovisual es de humor de memes (IQ), orientado a público general. Declarar "No, no está hecho para niños" es coherente con el público objetivo; no inventar consecuencias.
10. Variedad de formato: no evaluable (primer episodio del formato). Ver C4.
11. Tono: PASS. Sin angustia ni manipulación.
12. Arco narrativo: PASS. Escalada clara de nivel 1 a 5 y remate (vaciar el río y cruzar andando). Sin narración, pero la checklist exige arco, no voz.

## Comparación con la referencia (channel/reference/agbaps-bees-analysis.md)
Se imita solo la FÓRMULA (niveles de IQ, cortes, transición con barrido, música tranquila + efectos).
- Personajes: PASS. Referencia: personaje de proporciones normales con cabeza de dibujo, sudadera y vaqueros. Nuestro: humano de dibujo generado por semilla, distinto cada episodio. La ropa realista de sudadera/vaqueros figura como "pendiente" en el análisis: NO adoptarla si el resultado se parece al personaje de la referencia.
- Gags: PASS. Referencia: lanzar, agacharse, golpear, abejas. Nuestro: cruce de río con 5 soluciones propias. Sin coincidencia; no usar abejas ni su tema.
- Música: PASS. Síntesis propia, sin muestra. Coincidir en tempo (84-94 BPM) no es copia (el tempo no es un contenido protegido; es una decisión de estilo). Sin zumbido de abejas.
- Rótulo: RIESGO. El análisis dice que el kit usa un "rótulo nuevo" con recuadro blanco "IQ:" y número con contorno, color según el nivel (rojo el peor, oro el mejor): es la descripción del rótulo de la referencia. El formato "IQ" y los colores por nivel son un convenio genérico del género, pero un recuadro idéntico en composición, tipografía y colores podría leerse como imitación de la identidad visual de otro canal. Condición C2.
- Marca de agua: no hay constancia de que se copie la de la referencia. Condición C3 (verificar en el render v7).

## Condiciones antes de entregar
- C1 (metadata, responsable: metadata/publicación): descripción con crédito literal "Motion capture: CMU Graphics Lab Motion Capture Database" y nota de música/efectos propios; título y thumbnail que reflejen solo lo que se ve (gags de cruzar un río); sin prometer viralidad. Decidir `ai_use_disclosure` (ver punto 7) y "no para niños" (punto 9).
- C2 (animación/Director visual): rótulo distinto del de la referencia (otra tipografía, forma, paleta, posición). Mantener el número de IQ y el color por nivel si se quiere, pero con identidad visual propia del canal.
- C3 (QC): en el v7 comprobar que no hay marca de agua, logotipo ni texto de otro canal; que 20 s y -14/-16 LUFS se mantienen.
- C4 (Director, estrategia): market.json = WEAK (método 3D por código sin precedente medido; el formato se valida en animación a mano). No es un problema de política, pero el formato por niveles de IQ no debe convertirse en la única serie: varía el escenario, el número de niveles, el tipo de remate y el estilo de hook, y aporta en cada episodio un gag original. Los revisores miran el canal entero.

## Pendiente
- Re-render v7 con las correcciones del Director (borde del suelo, raya en la orilla, cámara, salpicadura). Esta revisión se basa en la descripción del v6 y el código de audio; el v7 debe pasar QC y revisión de C2/C3.
- Repetir `studio.py similar --story story-004` cuando existan más historias.

## Decisiones del Director (2026-11-16)
- Rótulo: rediseñado con identidad propia (banda oscura, "NIVEL DE IQ", número grande y barra de color) en scripts/anim_build.py.
- Licencia mocap: anotada la cesión de B. Hahne en anim/mocap/CLIPS.md. Crédito CMU en la descripción.
- Hashtags: quitados #ia y #ficcion (no describen el contenido); la descripción mantiene la transparencia ("generada con IA", "creada por código").
- Divulgación "contenido alterado o sintético": NO marcar — personajes de dibujo animado claramente no reales; YouTube la pide para contenido realista que pueda confundirse con real.
- "Creado para niños": declaración legal del usuario al publicar (COPPA). Recomendación: "No" si el canal se dirige a público general; decide el usuario.
- Marca de agua: no hay ninguna en nuestro montaje; verificar en v7 durante QC.
