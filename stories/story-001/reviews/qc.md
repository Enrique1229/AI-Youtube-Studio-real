# QC story-001 (SHORT) - El botón sin número - 2ª revisión
VERDICT: REJECT
SCORE: 61/100

Entradas: final/ (edl, metadata, provenance, subtítulos), voice/timing.json, probe, chapters/ch01.md, reviews/ (continuity, policy PASS 2ª rev., critic, director-visual.md).

## Desglose
- Historia/giro: 17/20 - sin cambios: cierre limpio ("el edificio donde nunca nací"), pistas resueltas.
- Hook (3 s): 6/10 - la frase inicial engancha en texto/voz, pero el Director declara que no se reconoce el panel ni el botón sin número: el plano inicial no soporta el hook.
- Ritmo: 8/10 - 18 planos de 3-4 s, 55,3 s (<60 s), ~125 palabras; ajustado pero válido.
- Continuidad (guion y visual): 3/10 - guion consistente, pero el Director reporta FALLA en consistencia de personaje (cara, edad, peinado y ropa distintas por plano), de estilo (B/N, color realista y posterizado mezclados) y de fidelidad al guion (rellano por épocas indistinguible; solo cena y niña con trenzas coinciden).
- Audio: 7/10 - mean -16,0 dB, max -1,5 dB (sin clipping, cerca de 0). Sin música ni SFX (edl: music null, sfx []): plano sonoro, sin cambio.
- Vídeo técnico: 8/15 - 1080x1920, 30 fps, h264/aac, 55,33 s, placeholder_images=false (error 1ª ronda resuelto); pero posterización/bandas y escalado visible 512->1080 reportados por el Director.
- Subtítulos: 8/10 - sincronizados con timing.json, ortografía correcta; fragmentos de 2-3 palabras muy cortados (sin corregir); último termina 55,197 vs 55,333.
- Metadata: 4/5 - upload_checklist corregido, ai_use_disclosure=true, policy PASS.

## Errores técnicos (bloqueantes)
1. Veredicto visual del Director: NO PUBLICABLE (inconsistencia de personaje/estilo, imágenes no fieles al guion, bandas de color). Causa: SD 1.5 a 512 px y prompts demasiado largos, no el pipeline.
2. Estado: gates.policy y gates.qc siguen PENDING en state.json (policy ya está PASS en reviews/policy.md; actualizar con studio.py). fix_rounds=2 ya consumidas: según reglas duras, esta puerta pasa a BLOCKED si no se cambia el motor/estrategia (decisión del Director).

## Correcciones
- visual-prompt-writer / operador de imagen: regenerar las 18 imágenes con modelo superior (SDXL en GPU) y estilo de ilustración de visual.md v2, bloques visuales en inglés y cortos; mismo bloque de personaje (Lena) y un único estilo en todos los planos; panel del ascensor con botón liso sin número legible y 3 rellanos claramente distintos por época.
- editor: re-montar con imágenes nuevas, actualizar provenance.json/edl.json (licencias del nuevo modelo); añadir SFX/ambiente leve (ascensor, radio); agrupar subtítulos en 4-6 palabras.
- Director: actualizar engine.md con el nuevo motor probado antes de regenerar; re-pasar policy (licencia nuevo modelo) y QC.

## NO verificado (revisión humana)
No he visto ni oído el vídeo: me baso en el informe del Director para lo visual. Sin verificar: prosodia/calidad de la voz, mezcla subjetiva, sincronía audiovisual percibida, legibilidad de subtítulos quemados, encuadre en móvil, calidad del thumbnail.
