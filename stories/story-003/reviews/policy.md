# Policy review (segunda revisión) — story-003 (SHORT derivado de story-002)

VERDICT: PASS

Condiciones no bloqueantes: ver "Pendientes". Esta revisión sustituye a la anterior (FIX).

## Checklist (channel/strategy/policy-checklist.md)
1. Similitud: OK. `studio.py similar` da 0.07 (mejor coincidencia: story-002). En concepto, contrastado con `stories/story-002/story-bible.md` (Giros, Clímax, Final): comparten el escenario (pozo, escalera de nombres, llama de carburo) pero no el protagonista ni el desenlace. Story-002: Mara, espeleóloga actual, descubre que fue la rescatista de su hermano y decide cómo grabar su peldaño; el final rompe el bucle con un peldaño "SALIDA". Story-003: Anselmo, buscador de pastores (años 60), encuentra su nombre ya grabado y tibio, y oye que alguien graba el siguiente. Giro y situación distintos. La lámpara de carburo y los años 60 encajan con el nivel II de story-002 (R3, nicho II), lo cual es coherencia de universo, no repetición de trama. Aviso: la comparación léxica solo ve story-002; el concepto con story-001 (ascensor entre épocas) no lo he podido leer (fuera de mi entrada). Solo comparten la etiqueta `bucle-temporal`; el escenario y el hook son distintos.
2. Valor original: OK. Historia propia, sin obra ni vídeo ajeno.
3. Título/descripción/thumbnail: OK en texto. Título y descripción cumplen lo que muestra el guion (nombre tibio, golpes abajo). Thumbnail fuera de mi entrada: debe mostrar solo lo que ocurre (escalera, nombre dorado). El título recomendado ("¿Por qué mi nombre ya estaba grabado en el pozo?") suena a testimonio real, pero la descripción declara la ficción desde la primera línea; aceptable.
4. Ficción como ficción: OK. La descripción dice "Historia de ficción original, generada con IA; no describe hechos reales". Nada parece noticia.
5. Personas, marcas, copyright: OK. "Anselmo" es genérico; sin marcas ni personajes ajenos.
6. Licencias: OK con una duda residual.
   - Kokoro-82M: Apache-2.0 (provenance).
   - Música y SFX: sintetizados por scripts/audio_gen.py, sin terceros.
   - SD 1.5 (CreativeML OpenRAIL-M) y LCM LoRA (OpenRAIL++): permiten uso comercial con restricciones de uso. Las notas del Director fijan la fuente (huggingface.co/stable-diffusion-v1-5/stable-diffusion-v1-5) y provenance dice "verificadas el 2026-11-13". No puedo contrastar el estado actual del repositorio; lo dejo como duda, no como bloqueo. Falta esa URL en provenance.json.
7. Divulgación: OK condicionado. `ai_use_disclosure: false` es válido solo si el render es ilustración claramente no realista. QC debe confirmarlo; si hay aspecto fotográfico, pasa a true. La descripción ya incluye el aviso de ficción y de IA.
8. Apto para anunciantes: OK. Sin violencia explícita, lenguaje ni temas sensibles.
9. No dirigido a niños: OK. Metadata marca "no es para niños". (`idea.json` tiene `audience: null`; cosmético.)
10. Variedad de formato: OK con vigilancia. Es una serie declarada, con protagonista, época, punto de vista y giro distintos (notas del Director + bible). No revela el final de story-002: solo plantea la pregunta de quién graba los nombres, que story-002 responde. Story-002 no pasó la puerta de mercado, así que el canal no tiene hoy otro vídeo publicable en el mismo pozo. Riesgo futuro: un tercer vídeo del pozo con la mecánica "encuentra su nombre" sería plantilla repetida (norma: "same situation over and over again with the same outcome"). `series_potential` dice "otro punto de vista del mismo pozo": cada entrega nueva debe cambiar mecánica y giro, no solo el personaje.
11. Tono: OK. Misterio inquietante, sin tragedia con apariencia real ni miedo gratuito.
12. Arco narrativo: OK. Planteamiento (baja al pozo), escalada (escalera, calor, su nombre, "mi sombra no habla") y final propio (graban el siguiente). No es una sucesión de imágenes.

## Mercado
`reviews/market.json` existe: verdict WEAK (Formato A: mucha oferta, poca tracción). Es un riesgo de percepción de "contenido inauténtico" a nivel de canal (market.md: clones intercambiables), no una infracción de este vídeo. Que WEAK cuente como paso de la puerta market lo decide el Director (las notas dicen "producir solo como experimento medible"). Política no afirma nada sobre monetización.

## Estado de las correcciones de la primera revisión
1. Giro vs story-002: resuelto (distinto; justificado en director-notes.md y verificado con la bible).
2. market.json: resuelto (existe).
3. Fuente del checkpoint: parcial (fuente en notas, no en provenance.json; verificación externa no posible desde aquí).
4. QC render no realista: sigue pendiente (puerta posterior).
5. `audience` en idea.json: opcional, sin cambios.

## Pendientes (no bloquean PASS)
- Director/provenance: añadir la URL de origen del checkpoint SD 1.5 a final/provenance.json.
- QC: confirmar render ilustrado no realista; si no, `ai_use_disclosure` = true.
- Director: no encadenar más entregas del pozo con la misma mecánica de "nombre grabado".
- Revisión periódica: repetir la lectura de políticas de YouTube cada 3 meses (checklist del 2026-11-13).
