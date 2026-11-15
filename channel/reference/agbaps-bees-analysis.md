# Análisis de un Short de referencia (formato "cada nivel de IQ") — 2026-11-15

Vídeo aportado por el usuario (21,4 s, 720x1280, 30 fps). Solo se imita la FÓRMULA; no se copian personajes, gags,
música ni marca de agua.

## Imagen
- 4 niveles en 21 s (≈5 s cada uno). Cortes dentro del nivel (planos de detalle: chapuzón, primer plano).
- Transición entre niveles ≈1 s con barrido + "whoosh" (3,0–4,4 s y 11,6–12,6 s).
- Escenario realista: árboles con hojas, hierba en primer plano, hojas secas en el suelo, luz cálida, fondo desenfocado.
- Cámara baja (altura de la hierba), profundidad de campo.
- Personaje de proporciones normales con cabeza de dibujo animado; ropa realista (sudadera, vaqueros, zapatillas).
- Movimiento de captura humana (mocap): lanzar, agacharse, golpear.
- Rótulo: recuadro blanco "IQ:" y debajo el número con contorno, color según el nivel (rojo el peor, oro el mejor).

## Sonido (medido con librosa)
- Pulso ≈89 BPM (tranquilo). La música es un fondo ligero; mandan los EFECTOS.
- Zumbido de abejas casi continuo (fa#–la), barridos en las transiciones, golpes, chapuzón.
- Volumen alto y constante (≈ −14 a −18 dB RMS).

## Aplicado en el kit
- `env_rio_real`: cielo físico, suelo procedural, ~35 000 briznas, árboles con hojas, bosque de fondo, AgX, cámara baja con desenfoque.
- `anim_build.py`: rótulo nuevo, barrido `slideleft` + whoosh entre niveles, `sneaky_music` (84–94 BPM, pizzicato,
  chasquidos), ambiente de parque (aire + pájaros), efectos más altos, normalización a −14 LUFS.

## Pendiente
- Varios planos de cámara por nivel; ropa larga (sudadera/vaqueros); movimiento de captura real (mocap libre).
