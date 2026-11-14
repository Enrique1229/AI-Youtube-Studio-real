# Estudio del formato "niveles de IQ" (canal de referencia: Agbaps Shorts) — 2026-11-14

Fuente: páginas públicas de YouTube y fotogramas automáticos (`channel/strategy/market-study/agbaps-fotogramas.jpg`).
No he podido ver los vídeos en movimiento ni oírlos.

## El canal de referencia
- 9,39 M de suscriptores, ~1.200 vídeos, se define como "comedy animation animator 3d".
- 48 Shorts recientes: mediana 2 M de vistas (mínimo 164.000, máximo 23 M).
- Avisa de que resubir su contenido o quitar su marca de agua conlleva reclamación de copyright.

## La fórmula
- Título fijo: "Low IQ vs High IQ…", "Every IQ level…", "How different IQ … [hacen X]".
- Un mismo problema físico y varias soluciones en escalera: de la más torpe a la más ingeniosa. Cada peldaño es un gag de pocos segundos.
- Rótulo arriba en todo momento: "IQ: 🧠" y una cifra que sube de negativa a muy positiva (-450 … +5469).
- Animación 3D hecha a mano, con el mismo personaje y los mismos escenarios en todas las escenas (Egipto y el faraón, soldados, pesca).
- Sin narración aparente: comedia visual. Marca de agua del canal.

## ¿La fórmula funciona fuera de ese canal?
Sí, en animación hecha a mano: Maizen (animación de Minecraft) tiene Shorts de "Low IQ vs High IQ" con 0,8 M, 3,6 M y 13 M de vistas;
también hay versiones con countryballs (1,3 M) y otras de 4,4 M y 20 M.
Con IA generativa, no encontré ningún caso con resultado: los canales que lo intentan tienen entre 2 y 376 suscriptores.

## Herramienta propuesta por el usuario: WanGP (Wan2GP)
Leído en su README, docs y licencia oficiales:
- "Low VRAM requirements: run select models with as little as 4 GB of VRAM". "8 GB of VRAM is enough to get started".
- Modo sin interfaz: `python wgp.py --process cola.zip|ajustes.json --output-dir carpeta`. También cola de trabajos y API. Es automatizable.
- Instalación en Windows: `scripts\install.bat` y `scripts\run.bat`.
- Licencia (WanGP Community License 2.0): uso gratuito; "you may sell or license those outputs", con crédito a WanGP al venderlos directamente.
  Los modelos que descarga conservan cada uno su propia licencia: hay que comprobar la del modelo concreto que se use.
- No probado: qué modelo de imagen-a-vídeo cabe en 6 GB, cuánto tarda y con qué calidad.

## Dificultades reales, de mayor a menor
1. Coreografía. El chiste depende de una acción física precisa (lanzar un imán y pescar, empujar una roca con un truco). Los modelos de imagen-a-vídeo mueven bien lo genérico, pero siguen mal una acción concreta de varios pasos en 5 segundos. Habrá que generar varias tomas por gag y elegir.
2. Mismo personaje en todas las escenas. Cada imagen de partida sale de un modelo que no recuerda al personaje. Hace falta una técnica de referencia (imagen de referencia o modelo de edición), que pide más memoria.
3. Ritmo cómico y sonido: sin efectos sonoros bien colocados, el gag no funciona.
4. Riesgo de política: es una serie con plantilla. La norma de YouTube cita "characters … in the same situation over and over … highly similar storyline template". Al canal original lo protege que su animación es propia y elaborada.

## Lo que sí encaja con lo ya construido
- No hay narración: desaparece el problema de la voz.
- El rótulo de IQ y el contador son texto superpuesto: trivial con FFmpeg.
- Ideas, crítico, puerta de mercado, continuidad, montaje, efectos, puertas finales: se reutilizan.

## Qué se puede imitar y qué no
Se puede: la fórmula de niveles, el ritmo, el tipo de rótulo, la comedia física.
No se puede: sus personajes, sus escenarios reconocibles, su marca de agua, sus gags concretos ni sus títulos literales.
