# Prototipo: comedia por niveles animada por código en Blender

Un personaje propio (modelo 3D construido por el script) intenta cruzar un río en tres niveles. Todo —escena, personaje,
animación y cámara— lo genera `gag.py`; no hay archivo .blend ni trabajo manual.

Ejecutar (Blender como módulo de Python 3.13: `pip install bpy`):
    python gag.py -- <nivel 1|2|3> <carpeta_salida> [fotograma_suelto]

Medido en CPU (4 núcleos, sin GPU): ~2,7 s por fotograma a 432x768 con Cycles a 10 muestras; 96 fotogramas (4 s) por nivel.
Con GPU debería ser mucho más rápido y a resolución completa; no medido.
Rótulos y sonido se añaden después con FFmpeg. Resultado: `pilot-output/prototipo-blender.mp4` (no versionado).
