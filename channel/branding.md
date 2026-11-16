# Branding del canal — inglés (2026-11-16)

Explicaciones internas en español. Todo lo marcado como **[PÚBLICO]** va tal cual en inglés.

## NOMBRE ELEGIDO: Klunk Studio
- Nombre [PÚBLICO]: **Klunk Studio**
- @handle: **@KlunkStudio** (confirmado: primer Short publicado el 2026-11-16, https://www.youtube.com/shorts/Oj-6SQY_aiE).
- Formatos que cubre (no es un canal de IQ): mini-historias de humor físico con giro, POV de un gag, objetos vivos con cara (mini-drama), niveles (IQ y otras escalas) y mascota/bicho vs humano. Ver `anim/FORMAT.md`, sección "Formatos del canal".
- Sustituye como nombre oficial a "The Wit Ladder" y a las propuestas de la sección 1 (históricas).

Nota: no he podido comprobar el @handle en YouTube (no tengo acceso). Los prompts de imagen de abajo ya usan "Klunk Studio". Regenerar imágenes con `python3 scripts/brand_text.py "Klunk Studio"`.

---

## 1. Propuestas de nombre de canal — HISTÓRICO (2026-11-16, superado por NOMBRE ELEGIDO)

No se usan. Se conservan solo como registro de la decisión.

| # | Nombre [PÚBLICO] | @handle propuesto [PÚBLICO] | Idea |
|---|---|---|---|
| 1 | Oops & Eureka | @oopsandeureka | Descartado: existe "Eureka Oops" (@EurekaOops). |
| 2 | The Wit Ladder | @thewitladder | Histórico: era el favorito antes de elegir Klunk Studio. Sin canales con ese nombre en la búsqueda, pero el nombre describe solo el formato de niveles. |
| 3 | Brainstep Studio | @brainstepstudio | Descartado: existen "BrainStep" y "Brainstep AI". |
| 4 | Eureka Falls | @eurekafalls | Débil: varios canales "Eureka …". |
| 5 | Level Up Clumsy | @levelupclumsy | Débil: existe "Clumsy Ninja Shorts". |
| 6 | Smart Way Down | @smartwaydown | Alternativa sin coincidencias; descartada por el usuario. |

Criterio que ya no aplica como favorito: el nombre no debe atar el canal a "IQ" (ver `channel/strategy/formats-mix.md`, "Nombre del canal").

---

## 2. Descripción del canal [PÚBLICO] (inglés, 600-900 caracteres)

Klunk Studio makes short, silent 3D comedy: clumsy plans, quick physical gags and small stories that end with a twist. Our formats: one-level gags shot from a first-person POV, objects with faces (a match with a very big day), mini-dramas, IQ and other rating scales, and a creature-versus-human series. Nothing here is real footage or a real event. Every episode is original fiction: the characters, sets, music and sound effects are created for this channel. Transparency: the animation is built with code and AI-assisted 3D tools. Motion capture: CMU Graphics Lab Motion Capture Database. There is no dialogue, so every gag reads without subtitles. We do not mock real people or groups. We make no promises about views or results: we post, watch what works and keep the jokes that land.

Nota interna: descripción revisada para la mezcla de formatos. Sustituye a la versión de "The Wit Ladder" (histórica, centrada solo en niveles de IQ).

---

## 3. Palabras clave del canal [PÚBLICO] (14)

animated comedy, silent comedy, physical comedy, 3D animation, original animation, funny shorts, cartoon comedy, IQ levels, POV comedy, mini stories, objects with faces, clumsy vs genius, animated shorts, comedy fiction

---

## 4. Imágenes del canal

### 4a. Foto de perfil (se ve en 98 px, circular)
Prompt [PÚBLICO, para generador de imágenes]:
> Stylized 3D cartoon character, head and shoulders, centered, facing the viewer. Big expressive eyes, bushy curly blond hair with visible texture, a confident half-smile, slightly raised eyebrow. Simple, bold, high-contrast shapes that read clearly when very small. Vivid saturated colors (orange, teal, sky blue). Soft background of a park with a river, blurred. Large face, minimal detail. No text, no logos, no watermark, no border.

Nota: a 98 px sólo debe leerse la cara y el pelo. Sin texto en la foto. El nombre "Klunk Studio" no se dibuja en la foto: aparece en el banner y en el nombre del canal. Si se quisiera vincular la foto al nombre, se hace con el color o la forma del personaje, no con rótulos.

### 4b. Banner (2560x1440)
Zona segura central: 1546x423 px. Todo lo importante (personaje y nombre) va dentro de esa franja; los bordes solo llevan fondo.
Prompt [PÚBLICO, para generador de imágenes]:
> Wide channel banner, 2560x1440 pixels, landscape. Stylized 3D cartoon character with big expressive eyes and bushy curly blond hair, mid-action pose, in a sunny park with a river and trees behind, vivid saturated colors. Keep the character and the channel name fully inside the central horizontal band, centered, about 1546 by 423 pixels; the left and right edges contain only background scenery. Channel name "Klunk Studio" in bold, rounded, clean lettering, large and readable, in the center band. No other text, no logos, no watermark.

Nota: los generadores no siempre respetan el tamaño exacto; reescalar/recortar a 2560x1440 y comprobar la zona segura en la vista previa de YouTube Studio. Verificar que el rótulo "Klunk Studio" se lee bien a 1546 px de ancho.

---

## 5. Ajustes de subida por defecto

| Ajuste | Valor | Motivo |
|---|---|---|
| Categoría | Comedy | Encaja con el formato de humor de animación. |
| Idioma del vídeo y del título | English | `studio.config.json` "language": "en" (decisión del usuario, 2026-11-16). |
| Hecho para niños ("Made for kids") | Recomendación: **No** | El humor (ironía con números de IQ) está dirigido a público general, no a niños; el dibujo amable no lo convierte en contenido infantil. **Decide el usuario**: es una declaración legal al subir (COPPA). Si cambia, revisar también los comentarios y la personalización de anuncios. |
| Contenido alterado o sintético | **No** | Los personajes son dibujos 3D claramente estilizados y los gags son imposibles (flotar, vaciar un río, una cerilla con cara); ninguna escena puede confundirse con un hecho real. Revisar por vídeo si un plano se vuelve fotorrealista. |
| Licencia | Licencia estándar de YouTube | Mantenemos los derechos; no concedemos reutilización CC. |
| Comentarios | Activados, con "retener comentarios potencialmente inapropiados para revisión" | Permite interacción sin dejar pasar spam. |
| Insertar (embed) | Permitido | Sin motivo para bloquearlo. |

---

## 6. Listas de reproducción [PÚBLICO] (una por formato)

Crear cada lista cuando haya al menos 2 vídeos en ella. Los vídeos de niveles usan rótulo "IQ LEVEL" o la escala que corresponda.

1. **Rating Levels** [PÚBLICO]
   Description: "Same problem, several levels: from the worst idea to the most brilliant one. IQ and other rating scales."
2. **POV Gags** [PÚBLICO]
   Description: "One moment, one point of view, one gag. Short first-person sketches where the plan goes wrong."
3. **Objects With Faces** [PÚBLICO]
   Description: "Everyday objects with faces and very small problems. Mini-dramas with no dialogue."
4. **Mini Stories With a Twist** [PÚBLICO]
   Description: "Short physical-comedy stories with a twist at the end, including the creature-vs-human series."

Histórico (no crear): "Every IQ Level", "Oops Moments", "Eureka Moments" (listas del nombre The Wit Ladder y de la versión anterior).

---

## 7. Sección destacada y trailer

- Vídeo de presentación para no suscriptores: **el episodio completo que mejor muestra la mezcla de formatos** (un nivel, un POV o una mini-historia con remate claro), una vez publicado y con QC aprobado. No un montaje de gags que no aparecen en ningún vídeo.
- Ahora mismo no hay ningún vídeo publicado: dejar la sección vacía hasta tener al menos 3 episodios publicados. Candidato inicial anterior: story-004 "Every IQ Level Tries to Cross a River" (solo como referencia; revisar si encaja con la nueva presentación).
- Texto de la sección [PÚBLICO] (cuando exista): "New here? Start with a silent gag, then five levels of IQ crossing a river."

---

## 8. Calendario de publicación sugerido (sin promesas)

- Empezar con 2 Shorts por semana durante 4 semanas, en dos franjas fijas (por ejemplo, martes y sábado), para que el público aprenda el horario.
- Mirar "Cuándo están tus espectadores en YouTube" en Analytics y ajustar la franja tras 4 semanas de datos.
- No publicar más rápido de lo que pase el QC y las 5 puertas: calidad antes que cadencia.
- Mezcla de formatos: nunca dos Shorts seguidos del mismo formato; cada episodio cambia problema, escenario y al menos 3 de 5 soluciones (anim/FORMAT.md, `channel/strategy/formats-mix.md`).
- Ningún resultado de visualizaciones está garantizado; el calendario se revisa con datos reales, no con expectativas.

---

## Comprobación de nombres — HISTÓRICO (2026-11-16, búsqueda con scripts/yt_lookup.py)

Resultados de la búsqueda de las propuestas de la sección 1. Superados por NOMBRE ELEGIDO: Klunk Studio. No se ha buscado "Klunk Studio" con la herramienta; el usuario confirma que el canal ya está creado.
- "Oops & Eureka": existe "Eureka Oops" (@EurekaOops). Descartado.
- "Eureka Falls": varios canales "Eureka …". Débil.
- "Brainstep Studio": existen "BrainStep" (@brainstepofficial) y "Brainstep AI". Descartado.
- "Level Up Clumsy": existe "Clumsy Ninja Shorts". Débil.
- "The Wit Ladder": sin canales con ese nombre en la búsqueda. Histórico.
- "Smart Way Down": sin coincidencias.
