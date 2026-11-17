# Policy review — story-011 (Short anim niveles, "Every IQ Level Moves a Boulder") — 2026-11-17
Veredicto: PASS (con condiciones OBLIGATORIAS de producción, ver C1-C3 y R1)
Alcance: idea.json + diseño; no hay escenas, render ni metadata.json aún. Modelo: story-008/reviews/policy.md.

## Checklist (policy-checklist.md)
1. Similitud: `studio.py similar` = 0.07 (< 0.3; match léxico: manzana/árbol). Concepto distinto (obstáculo pesado con remate de espuma). OK.
2. Valor original: gag propio (roca de espuma que pesa menos que el esfuerzo). OK.
3. Título "Every IQ Level Moves a Boulder": debe coincidir con lo que se ve (la roca sí se mueve en 130, 900 y 5200; en -500 y -80 no). Verificar en metadata.json. Condición A.
4. Ficción como ficción: animación no realista, roca de espuma. OK.
5. Personas reales/marcas/copyright: ninguno. OK.
6. Licencias: kit propio, música/SFX sintetizados, mocap CMU (sin restricciones; crédito sugerido). Condición B.
7. Divulgación AI: estilo animado no realista -> false defendible. Duda menor: `env_rio_real` es fotorrealista (cielo físico, hierba). Decisión del Director; ante la duda, true.
8. Apto anunciantes: comedia física sin sangre ni daño. Ver slapstick.
9. No dirigido a niños: slapstick con estrellas y roca de espuma atrae público infantil; sin canciones ni personajes infantiles. Duda abierta sobre la clasificación de YouTube. Condición D.
10. Variedad: ver repetición.
11. Tono: humor ligero. OK.
12. Arco: gancho (empujando en frame 1), escalada de 5 niveles, remate (espuma), bucle. OK.

## Violencia slapstick (punto crítico)
- Nivel -500: "se aleja corriendo y se estrella contra la roca; rebota y queda sentado con estrellas". Riesgo bajo si se hace amable, pero un choque a la carrera puede leerse como autolesión.
- C1 (obligatoria): el choque es contra una roca visiblemente blanda en el rebote (rebote elástico tipo cartoon, sin crujido ni golpe seco), sin gemido ni grito de dolor, sin sangre, sin cámara lenta ni zoom al impacto. Estrellas = convención cartoon, 1 s máximo; el personaje se incorpora sin quedar inmóvil. Sonido: "boing"/pof suave, no "thud" contundente.
- C2: nivel -80 (resbala y cuelga del borde): sin caída a gran altura ni sonido de dolor; el borde de la roca es bajo, el personaje queda a salvo.
- C3: nadie sale herido ni humillado con crueldad; el gag es la torpeza, no el sufrimiento. Esto refuerza el remate (la roca es de espuma, el choque siempre fue inofensivo): coherente.

## Contenido repetitivo (R1)
Riesgo medio. Con este habría 4 Shorts de niveles de IQ en el canal (río, pato, gaviota, roca): es el punto sensible de "templated storylines / same situation over and over with the same outcome". Argumentos a favor: cada uno tiene problema, escenario, gags y remate distintos (cruzar, alimentar, alcanzar, mover); similitud léxica 0.07; la fórmula IQ es genérica y el desenlace de este (obstáculo ligero) no repite el de los otros. Argumentos en contra: misma estructura de 5 niveles, mismo rótulo, mismo patrón "el más listo hace lo fácil".
- R1 (obligatoria para el Director): no publicar este Short de niveles seguido de otro Short de niveles; intercalar formatos distintos (POV, objetos vivos, narrativo largo) al menos 2-3 vídeos entre niveles. Variar el remate: "el más listo descubre un truco" ya aparece; aquí es "el obstáculo era ligero"; no reutilizar esa fórmula en los siguientes.
- Aplicar critic_improve (roca tiembla antes del dedo para sembrar la espuma; sustituir rodar por salto lateral de la roca). Mejora el arco y evita física nueva.
- Cambiar visiblemente escenario/luz/protagonista respecto a río, pato y gaviota (`env: rio` repetido: variar encuadre, hora o vestuario).
Si el Director no puede garantizar la intercalación, este punto pasa a FIX; no es STOP.

## Comparación con referencia (agbaps-bees-analysis.md)
La referencia usa abejas, chapuzón, personaje con cabeza de dibujo, rótulo "IQ:" blanco con número de color. Aquí: sin abejas, sin chapuzón, gag de roca/espuma propio, rótulo propio "IQ LEVEL". Solo se toma la fórmula genérica "niveles de IQ", ya declarada en FORMAT.md. Riesgo de copia: bajo. No copiar música, rótulo idéntico ni el aspecto del personaje.

## Condiciones de entrega
A. metadata.json en inglés, honesto, sin promesas de viralidad; título coherente con lo que se ve. B. Descripción con crédito de mocap CMU; provenance "kit propio, SFX/música sintetizados". C1-C3 verificables en QC visual. D. Audiencia: decide el usuario en la subida (duda abierta sobre "made for kids"). R1: orden de publicación.
Responsables: Director (A, D, R1); Production/Editor (B, C1-C3, critic_improve); QC (verificar C1-C3).

## Continuidad (gate continuity)
Historia aislada, sin capítulos ni continuidad con otras historias; personaje y escenario del kit. Sin contradicciones internas entre beats y levels (idénticos). PASS por indicación del Director; verificar que la roca mantiene tamaño, color y posición coherentes entre niveles (vuelve a su sitio en cada corte) y que, tras 5200, queda a un lado.
