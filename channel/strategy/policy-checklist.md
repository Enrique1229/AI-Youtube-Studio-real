# Checklist de política y monetización
Fuente: páginas oficiales de Ayuda de YouTube, leídas el 2026-11-13 (repetir la lectura cada 3 meses):
- Políticas de monetización del canal: support.google.com/youtube/answer/1311392
- Divulgación de contenido GenAI: support.google.com/youtube/answer/14328491
- Biblioteca de audio: support.google.com/youtube/answer/3376882

## Lo que dice YouTube (citas literales)
Contenido inauténtico (nombre desde el 15-07-2025; antes "repetitious content"):
- El contenido debe "Not be mass-produced, generic, repetitive, or manipulative."
- No monetizable: "Image slideshows, templated storylines, or scrolling text with minimal or no narrative, commentary, or educational value".
- No monetizable: "AI-generated content made with generic or unoriginal templates giving the impression of mass production without adding the creator's original, authentic insights or perspective".
- No monetizable: "Videos where characters are put in the same situation over and over again with the same outcome (i.e., using a highly similar storyline template across multiple videos)".
- No monetizable: "Content that lacks a clear narrative arc or logical progression, such as videos that stitch together unrelated or inconsistent AI clips to surprise or shock viewers".
- No monetizable: "Content that repeatedly uses disturbing themes (such as violence or loss) without building a cohesive narrative".
- SÍ monetizable: "Content that expresses your unique creative voice, like using AI to visualize a unique character and narrative you invented".
- "If you use automated tools or templates to help create your content, the final product must still demonstrate your creative vision and provide educational or entertainment value."
- Los revisores miran el canal entero: tema principal, vídeos más vistos, metadata.
Divulgación ("AI use" al subir):
- Obligatoria para contenido que "Generates a realistic scene that didn't actually occur."
- No hace falta para contenido no realista ni para ayuda de producción ("video outline, script, thumbnail, title").
- La página leída no detalla sanciones; no asumas cuáles son.
Biblioteca de audio: "copyright-safe"; las pistas con licencia Creative Commons exigen atribución en la descripción.

## Consecuencia para este canal
Imágenes fijas + voz sintética + estructura fija es el perfil que la norma describe como riesgo. Lo que nos separa de él es una narrativa propia con arco claro en cada vídeo y variedad real entre vídeos. El estilo del canal es ilustración (no realista): "AI use" no es obligatorio por realismo, pero márcalo si un vídeo sale con aspecto fotográfico.

## Puntos a comprobar en cada vídeo
1. Similitud con vídeos previos del canal: `studio.py similar --story <id>` < 0.3 (filtro léxico grueso: además juzga tú la similitud de concepto) y sin plantilla narrativa repetida.
2. Aporta valor original: historia propia, no reescritura de una obra o vídeo ajeno.
3. Título, descripción y thumbnail cumplen lo que el vídeo muestra.
4. Ficción presentada como ficción; nada que parezca noticia o hecho real.
5. Sin personas reales, marcas ni personajes con copyright.
6. Licencias: modelo de imagen/vídeo, voz TTS y música permiten uso comercial (anotadas en engine.md y edl.json).
7. Divulgación: si las imágenes son realistas, `metadata.ai_use_disclosure` debe ser true (escena realista que no ocurrió). Solo false con estilo claramente no realista (animación, ilustración).
8. Apto para anunciantes: violencia, lenguaje, temas sensibles.
9. No dirigido a niños.
10. Variedad de formato: el vídeo no repite la estructura, el tipo de giro ni el estilo de hook de los 3 anteriores del canal.
11. Tono: no busca angustiar ni manipular emocionalmente (miedo gratuito, tragedias con apariencia real).
12. Arco narrativo: el vídeo tiene planteamiento, escalada y final propios; no es una sucesión de imágenes llamativas.
