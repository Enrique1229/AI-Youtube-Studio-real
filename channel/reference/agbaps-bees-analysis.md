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

# Dos referencias más del mismo canal (aportadas por el usuario, 2026-11-16)

## R2 — "cerillas vivas" (20,4 s)
- Objetos con cara (cerillas con ojos, cejas y boca) como protagonistas; un humano gigante aparece al principio (enciende).
- Mini-drama sin diálogo: una cerilla se enciende, contagia a otras, hay una "pareja" (una con peluca rubia), sustos, remate
  con emoji de calavera. Mucha cámara a la altura de los objetos, primeros planos de caras y llamas con brillo.
- Escenario realista de cocina (encimera, luz cálida). Música melódica ≈117 BPM (Fa mayor), golpes moderados.

## R3 — "POV: You Hop In A Kids Race Car" (9,3 s)
- Rótulo fijo arriba con la premisa "POV: …" (recuadro blanco, texto negro), sin niveles de IQ.
- Gag único y rápido: un adulto se sube al coche de juguete de un niño, nitro, sale disparado, el niño grita. Cierre con
  "follow for more". Música muy tonal ≈99 BPM y muchos efectos (7,6 golpes/s). Duración muy corta: 9 s.

## Conclusión para nuestro canal
El canal de referencia NO es solo IQ: alterna (1) escalera de IQ, (2) objetos vivos con mini-drama, (3) POV de 9-15 s.
Nuestro kit necesita: personajes-objeto con cara, fuego/brillo, rótulo de premisa "POV:" y formatos de 9-15 s.
Se imita la FÓRMULA, nunca los personajes, gags concretos, música ni rótulos idénticos.
