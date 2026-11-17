# Policy review — story-008 (Short anim niveles, "Every IQ Level Feeds a Duck") — 2026-11-17
Veredicto: PASS (con condiciones OBLIGATORIAS de producción, ver C1-C3)
Alcance: idea.json + diseño; no hay escenas, render ni metadata.json aún.

## Checklist (policy-checklist.md)
1. Similitud: `studio.py similar` = 0.16 (< 0.3; match: barquito/río). Mismo formato "niveles" que el Short de río ya publicado, pero distinto problema (alimentar a un animal), escenario de muelle y desenlace (torre de patitos). Sin plantilla narrativa idéntica. OK.
2. Valor original: gag propio (pan de sombrero + patitos). OK.
3. Título "Every IQ Level Feeds a Duck": debe coincidir con lo que se ve. Verificar en metadata.json. Condición A.
4. Ficción como ficción: animación no realista. OK.
5. Personas reales/marcas/copyright: ninguno. OK.
6. Licencias: kit propio, música/SFX sintetizados, mocap CMU (CLIPS.md: sin restricciones; crédito sugerido en descripción). Condición B.
7. Divulgación AI: estilo animado no realista -> false defendible. Duda menor: `env_rio_real` es fotorrealista (hierba, cielo físico). Decisión del Director; ante la duda, true.
8. Apto anunciantes: comedia física sin sangre. Ver maltrato animal.
9. No dirigido a niños: pato y patitos atraen público infantil; sin canciones infantiles. Duda abierta sobre la clasificación de YouTube. Condición D.
10. Variedad: formato niveles repetido respecto al río publicado; ver orden.
11. Tono: ternura/humor. OK.
12. Arco: gancho, escalada de 5 niveles, remate (patitos en torre), bucle. OK.

## Maltrato animal (punto crítico)
- Nivel IQ -420: "golpea al pato, que huye nadando indignado". Es el único punto de riesgo: un impacto sobre un animal real-like, aunque cómico, puede leerse como daño/humillación. C1 (obligatoria): la hogaza NO toca al pato; cae en el agua junto a él o pasa por encima, el pato se sobresalta y se aleja con dignidad, sin chillido ni animación de dolor. El humano es el torpe, no el pato.
- Nivel 850: el pato se sienta en el regazo por voluntad propia: OK.
- C2: el pato nunca cae al agua forzado, ni es atrapado, perseguido ni disfrazado. Patitos: aplicar critic_improve (3 patitos, torre estable, sin caída ni aplastamiento del de abajo).
- C3: el pato siempre "gana" o sale ileso; sin sonidos de dolor.

## Contenido repetitivo
Riesgo bajo-medio: dos Shorts de niveles con animal (008, 009) en `rio` y el río ya publicado. Mitigación: separarlos con otro formato y cambiar escenario visible (muelle/orilla distinta, luz, protagonista distinto: `kit.look_for` ya lo da por nombre de archivo). 3 de 5 soluciones distintas respecto al río: cumple.

## Comparación con referencia (agbaps-bees-analysis.md)
Sin abejas, sin gags ni personajes ni rótulos copiados; solo la fórmula genérica "niveles de IQ" (declarada en FORMAT.md). Rótulo propio "IQ LEVEL". Riesgo de copia: bajo.

## Condiciones de entrega
A. metadata.json en inglés, honesto, sin promesas de viralidad. B. Descripción con crédito de mocap CMU; provenance "kit propio, SFX/música sintetizados". C1-C3 verificables en QC visual. D. Audiencia: decide el usuario en la subida.
Responsables: Director (A, D); Production/Editor (B, C1-C3); QC (verificar C1-C3).
