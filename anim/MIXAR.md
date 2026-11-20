# Modelos externos (Mixar u otra fuente) en episodios 9+

Probado el 2026-11-20 (sesión de Claude Code en el PC del usuario): Mixar 4.5.0 por MCP crea geometría
(`execute_bpy_script`), exporta a GLB (`export_scene`, con verificación) SOLO a Descargas/biblioteca, y Blender 5.3
importa ese GLB. Con 0 créditos NO funcionan: generación IA (model_3d, image_to_3d, tripo_rig, materiales IA).

## Flujo (sesión de Claude Code en el PC, con Mixar conectado)
1. En Mixar: crear/ajustar el modelo en una pestaña nueva (`mixar_scene_new`), nombrar los objetos, exportar GLB.
2. `python scripts/mixar_fetch.py ep009 roca roca.glb --objects Roca --dims 1.2,1,0.9 --animated`
   → copia de Descargas a assets/mixar/ep009/ y registra sha256 en manifest.json.
3. En el episodio: `ASSETS = "assets/mixar/ep009/manifest.json"` y `roca = use_asset(S, "roca", location=...)`;
   animarlo con `S.key(roca, …)` (o personajes del kit con captura de movimiento).
4. `python scripts/render_night.py ep009` → antes de renderizar comprueba archivos y huellas; tras montar cada
   nivel comprueba objetos, medidas y que lo marcado como animado se mueva. Si algo falla, se detiene.

## Garantías
- Episodios 1-8 protegidos: huellas en channel/locks/episodes-1-8.sha256; render_episode se niega a renderizarlos
  y avisa si su código cambió; mixar_fetch se niega a escribir en ellos.
- Nunca imágenes fijas: los modelos son mallas 3D importadas y animadas en Blender.
- Audio, montaje (anim_build) y control (qc_local) sin cambios.
