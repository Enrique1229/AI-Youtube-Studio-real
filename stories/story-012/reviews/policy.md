# Policy review — story-012 (Short anim niveles, "Every IQ Level ... Rain Cloud") — 2026-11-18
Veredicto: PASS (con condiciones OBLIGATORIAS: A, R1, R2, C1-C2)
Alcance: idea.json + diseño; no hay escenas, render ni metadata.json aún. Modelo: story-011/reviews/policy.md.

## Checklist (policy-checklist.md)
1. Similitud: `studio.py similar` = 0.14 (< 0.3; match léxico con el balancín). Concepto distinto (nube personal que persigue; remate de riego a flores). OK.
2. Valor original: gag propio (nube sedienta de ayudar a unas flores). OK.
3. Título: idea.json dice "Stays Dry", status muestra "Escapes a Rain Cloud". En -450 y -80 el personaje SE MOJA, así que "Stays Dry" promete algo que no se ve. Condición A: usar el título "Escapes" o similar, o uno honesto ("Every IQ Level vs a Personal Rain Cloud"). Revisar en metadata.json.
4. Ficción como ficción: animación no realista, nube de esferas. OK.
5. Personas reales/marcas/copyright: ninguno. OK.
6. Licencias: kit propio, SFX/música sintetizados, mocap CMU. Provenance y crédito CMU en descripción (condición B).
7. Divulgación AI: estilo animado no realista -> false defendible. Duda menor: `env_rio_real` es fotorrealista (cielo físico, hierba); ante la duda, true. Decisión del Director.
8. Apto anunciantes: solo se moja; sin sangre ni daño. OK.
9. No dirigido a niños: nube simpática, flores y final tierno atraen público infantil; sin canciones ni personajes infantiles. Duda abierta sobre la clasificación "made for kids"; decide el usuario en la subida (condición D).
10. Variedad: ver R1.
11. Tono: humor ligero, remate amable. OK.
12. Arco: gancho en el fotograma 1 (corriendo bajo la nube), escalada de 5 niveles, remate (riego/flores), bucle. OK.

## Daño / slapstick
- Solo agua; nada de rayos ni tormenta amenazante. Mantener la nube blanca/gris clara, no negra, y sin truenos (C2).
- C1 (obligatoria): -80 "cae al suelo con un charco": caída amable, de poca altura, sin sonido de golpe seco ni quejido; sonido tipo "splash/pof" suave; se levanta enseguida y vuelve a saltar con confianza (ya está en el guion). Sin cámara lenta ni zoom al impacto.
- C2: la lluvia no debe parecer castigo cruel; la nube no tiene cara de burla. Es insistente y luego cariñosa, coherente con el remate.

## Contenido repetitivo (R1, R2)
Riesgo medio-alto por acumulación. Con este habría 5 Shorts de niveles en el canal (008 pato, 009 sándwich, 011 roca, 012 nube, más el anterior del río). Es el punto sensible de "same situation over and over with the same outcome / templated storylines".
A favor: problema, escenario, gags y remate distintos en cada uno (alimentar, proteger, mover, escapar de lluvia); similitud léxica baja; FORMAT.md exige cambiar problema y al menos 3 de 5 soluciones (se cumple: ninguna solución se repite con 008/009/011).
En contra: misma estructura de 5 niveles, mismo rótulo, mismo patrón "el más listo hace lo fácil/ingenioso".
- R1 (Director, obligatoria): no publicar este Short seguido de otro de niveles; intercalar al menos 2-3 vídeos de otro formato (POV, objetos vivos, narrativo largo). Hoy 006, 007 y 010 no son de niveles: ordenar la cola para que 008, 009, 011 y 012 no vayan juntos. Si no se puede garantizar, pasa a FIX (no STOP). Duda: YouTube no publica un umbral numérico; es juicio del revisor sobre el canal entero.
- R2 (Production): FORMAT.md línea 32 pide que los niveles no vayan en orden ascendente. Aquí van -450, -80, 120, 900, 5400 (ascendente puro). Reordenar (p. ej. 120, -450, 5400, -80, 900) o justificar; además el remate no debe repetir "el más listo descubre un truco" ni "el obstáculo era ligero" (011). Aquí el remate es "el problema era otro/ayuda a las flores": distinto. OK. Variar también escenario/luz/vestuario respecto a los previos (`env: rio` repetido).
- Aplicar critic_improve (lluvia = un cylinder en bucle, nube = 3 esferas con un solo S.key, flores marchitas visibles desde el nivel 120 para sembrar el remate).

## Comparación con referencia (agbaps-bees-analysis.md)
La referencia usa abejas, chapuzón, cabeza de dibujo, rótulo "IQ:" blanco con número de color. Aquí: sin abejas, sin chapuzón en agua (solo lluvia/charco amable), personaje y gags propios, rótulo propio "IQ LEVEL". Solo se toma la fórmula genérica de niveles, ya declarada en FORMAT.md. Riesgo de copia: bajo. Cuidar que el charco del -80 no se convierta en un "chapuzón" calcado del plano de la referencia; no copiar música ni rótulo.

## Condiciones de entrega
A. metadata.json en inglés, honesto, sin promesas de viralidad; título coherente con lo que se ve (no "Stays Dry"). B. Descripción con crédito de mocap CMU; provenance "kit propio, SFX/música sintetizados". C1-C2 verificables en QC visual. D. Audiencia ("made for kids"): decide el usuario en la subida. R1: orden de publicación (Director). R2: orden de niveles (Production/Editor).
Responsables: Director (A, D, R1); Production/Editor (B, C1-C2, R2, critic_improve); QC (verificar C1-C2, R2).

## Continuidad (gate continuity)
Historia aislada, sin capítulos ni continuidad con otras historias. beats y levels idénticos, sin contradicciones. Verificar en producción: la nube mantiene tamaño y color en todos los niveles; el banco se arranca en 900 y debe estar de nuevo en su sitio (o visible) en 5400 para que el personaje se siente; las flores marchitas visibles desde el nivel 120 y floridas solo al final. PASS.
