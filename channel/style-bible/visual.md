# Style Bible — Visual (v2, decidido por el usuario el 2026-11-13)
- Estilo: ILUSTRACIÓN / NOVELA GRÁFICA. Tinta con contorno marcado, color plano con sombras duras, textura de papel leve. No fotorrealismo.
- Paleta: azules y verdes fríos con UN acento cálido (ámbar o rojo) por plano.
- Encuadre: sujeto único, viñeta clara, composición centrada o regla de tercios. En 9:16 el sujeto ocupa el tercio central.
- Sufijo de estilo fijo (añadir literal al final de cada prompt): "graphic novel illustration, bold ink outlines, flat colors with hard shadows, teal and amber palette, subtle paper texture, dramatic lighting"
- Negativo fijo: "photo, photorealistic, 3d render, text, watermark, logo, speech bubbles, deformed hands, extra fingers, blurry, frame, border, poster, picture frame"
- Prohibido: caras de personas reales, marcas, gore, bocadillos o texto dentro de la imagen.
- Divulgación: al no ser realista, `ai_use_disclosure` puede ser false; si un vídeo concreto sale con aspecto fotográfico, true.
- Pendiente: validar el sufijo con el modelo que se instale en la GPU (el piloto story-001 se generó antes de esta decisión, con el estilo realista anterior).

## Escenario muy producido (usuario, 2026-11-23) — OBLIGATORIO en animación
Desde ahora todo episodio lleva un escenario y fondo muy producidos y con mucho detalle: HDRI acorde + suelo PBR + 8-15 piezas de atrezo
realistas CC0 (Poly Haven) en primer plano, medio y fondo, con variación y detalles pequeños, y profundidad. Nunca un suelo vacío con un HDRI.
El atrezo no tapa el gag ni la cara y no ocupa el 15 % inferior (interfaz de Shorts). Lo comprueba el Director en director-visual.md.
