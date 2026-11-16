# Policy review — story-005 (Short anim, "A Match Warms Up an Ice Cube (Together Forever)") — 2026-11-16
Veredicto: PASS (con 3 condiciones de entrega no bloqueantes)

## Checklist (policy-checklist.md)
1. Similitud: `studio.py similar` da 0.58, pero el único match es la variante v1 descartada de la misma idea (o03, ideas.json l.86) en el mismo lote, no un vídeo del canal. Contra vídeos entregados no hay coincidencia detectada por el filtro. Sin plantilla narrativa repetida. OK. (No he revisado el contenido de otras historias, por protocolo.)
2. Valor original: historia propia (frío, calor, derretido, abrazo, transformación en vapor). Arco completo: necesidad (0-2 s), intento, error trágico-tierno, giro, remate. OK.
3. Título/descripción/thumbnail vs vídeo: título "A Match Warms Up an Ice Cube (Together Forever)" coincide con lo que se ve. Pendiente verificar final/metadata.json cuando exista (no leído, no estaba en la entrada). Condición A.
4. Ficción como ficción: objetos animados con cara, nada que parezca real. OK.
5. Personas reales/marcas/copyright: ninguno. Cerilla y cubito genéricos. OK.
6. Licencias: todo propio (kit 3D del estudio, música y efectos sintetizados). Sin voz ni TTS. Sin pistas de terceros, sin atribución necesaria. OK. Condición B: dejar anotado en provenance.json/edl.json "música y SFX sintetizados por el estudio; kit propio".
7. Divulgación AI: estilo no realista (animación 3D de objetos con caras). El criterio del checklist permite false. Nota: el Director corrigió hielo/charco con transmisión real; sigue siendo claramente animación. Duda menor: si el render final luce muy fotorrealista (encimera "mesa"), valorar marcar true por prudencia. Decisión del Director; no invento regla.
8. Apto anunciantes: sin violencia, lenguaje ni temas sensibles. La "pérdida" es suave y se resuelve en transformación feliz. OK.
9. No dirigido a niños: personajes-objeto simpáticos pueden atraer a público infantil. Es riesgo de "made for kids" (decisión de YouTube/uploader). Condición C: en la subida declarar audiencia según criterio del usuario; el contenido no usa gancho infantil explícito (sin canciones infantiles ni personajes de dibujos conocidos). Duda: no sé cómo clasificaría YouTube este perfil.
10. Variedad de formato: formato "objetos vivos con mini-drama" distinto de IQ-niveles y POV. Se debe confirmar que no sea el mismo formato que el Short inmediatamente anterior (regla "nunca dos seguidos"); el Director lo controla con formats-mix.md.
11. Tono: dulce, sin manipulación ni angustia gratuita; la v2 suaviza el final trágico de v1. OK.
12. Arco narrativo: planteamiento, escalada, giro, remate propios. OK.

## Contenido repetitivo/inauténtico y reutilizado
- Guion y animación propios, generados por episodio (ep002.py); sin clips ajenos ni stock. Perfil "creative voice" del checklist. Riesgo bajo.
- Riesgo de canal (los revisores miran el canal entero): si se produce una serie de "objeto con cara + mini-drama" con el mismo desenlace, riesgo de plantilla. Mitigación existente: el formato exige cambiar escenario, protagonista y >=3 beats. Critic marca repetition_risk 3/10 y series 5. Vigilar en próximos episodios (no aquí).

## Comparación con la referencia R2 (cerillas vivas, agbaps-bees-analysis.md)
Referencia: cerillas con ojos/cejas/boca, humano gigante que enciende, contagio de llama a otras cerillas, pareja con peluca rubia, sustos, remate con emoji de calavera, cocina realista, música melódica 117 BPM.
Nuestro episodio:
- Protagonistas: cerilla + cubito de hielo (personaje inexistente en R2). Cubito = cubo + 2 esferas de ojos; no coincide con el diseño de cerilla de la referencia (idea.json "diferencia": cero contagio, pareja o peluca).
- Gags: sin contagio, sin humano gigante, sin peluca, sin sustos, sin calavera; remate propio de vapor con dos caritas. Premisa (calentar a un amigo que se derrite) distinta de R2.
- Rótulos: sin caption; solo "follow for more" al final, texto genérico de CTA, no una marca de la referencia. Sin rótulo "POV:" ni "IQ".
- Música/SFX: sintetizados por el estudio, melodía distinta por episodio; no se ha oído la referencia.
- Único elemento compartido: la fórmula "objeto vivo con cara + mini-drama sin diálogo", que FORMAT.md y el análisis declaran imitar explícitamente (fórmula, no contenido). Una cerilla con cara es un concepto genérico, no protegible por sí solo. Riesgo de copia: bajo (confirmado con idea.json y director-visual.md). Condición D: no añadir en producción contagio de llama, peluca, pareja ni calavera.
- Escenario "mesa" (encimera en penumbra) recuerda de forma genérica a una cocina; es un tipo de escenario común, no reconocible de la referencia. Aceptable.

## Condiciones de entrega (no bloquean este PASS)
A. Revisar final/metadata.json cuando exista: título/descripción en inglés, honestos, sin promesas de viralidad; hashtags relevantes.
B. provenance.json/edl.json con licencias: todo propio.
C. Decidir audiencia (made for kids o no) en subida; duda abierta.
D. Mantener las diferencias frente a R2 en el render final (QC visual).
E. Pendiente del Director: render completo y QC (según director-visual.md); esta revisión es sobre la idea y el diseño visual, no sobre el MP4 final.

Responsable de las correcciones: Director (A, C, D, E); Production/Editor (B).
