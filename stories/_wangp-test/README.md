# Prueba de WanGP: ¿sirve imagen-a-vídeo para comedia física por niveles?

Objetivo: decidir con hechos si el formato "niveles de IQ" (ver `FORMAT-STUDY-AGBAPS.md`) es viable en esta máquina (RTX 4050, 6 GB).
Personaje y gag propios, no copiados de ningún canal. Tres niveles del mismo problema (cruzar un río).

## Pasos (los ejecuta Claude Code en el PC)
1. Con ComfyUI abierto: `python scripts/gen_images.py _wangp-test` → 3 imágenes en `stories/_wangp-test/assets/images/` (n1, n2, n3).
2. Cierra ComfyUI (los dos programas no caben a la vez en 6 GB).
3. En WanGP, con el modelo **Wan 2.2 TI2V 5B** (el pequeño), genera un clip por imagen usando como texto el `motion_prompt` de `visual-prompts/shots.json`.
   Ajustes de partida: 480p vertical, ~5 s, los pasos por defecto del modelo o su perfil acelerado. Si hay error de memoria, baja resolución o duración UNA vez.
   Modo sin interfaz, si se prefiere: exportar los ajustes desde la interfaz ("Export Settings") y lanzar `python wgp.py --process ajustes.json --output-dir <carpeta>`.
4. Guarda los clips como `stories/_wangp-test/assets/clips/n1.mp4`, `n2.mp4`, `n3.mp4`.
5. Escribe `stories/_wangp-test/reviews/resultado.md` con: modelo y ajustes exactos, tiempo por clip, memoria (¿error?), y por cada clip:
   - ¿hace la acción pedida? (sí / a medias / no) y qué hace en realidad
   - ¿el personaje se mantiene igual que en la imagen de partida?
   - defectos visibles
   Extrae 4 fotogramas de cada clip con ffmpeg y míralos antes de responder. No declares nada que no hayas visto.
6. Monta los tres clips seguidos con un rótulo arriba ("NIVEL 1", "NIVEL 2", "NIVEL 3") en `final/prueba.mp4` y cópialo al Escritorio del usuario.

## Qué decide la prueba
- Si la acción no se cumple en al menos 2 de 3 clips → el formato no es viable con esta herramienta tal cual.
- Si el personaje cambia entre las tres imágenes → hace falta un modelo con imágenes de referencia (p. ej. Qwen Image 2.1 en WanGP) antes de seguir.
- Si cada clip tarda más de ~15 min → un Short de 5 niveles no es práctico en esta tarjeta.
