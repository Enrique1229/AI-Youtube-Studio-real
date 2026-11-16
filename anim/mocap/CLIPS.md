# Clips de captura de movimiento

Fuente: CMU Graphics Lab Motion Capture Database (http://mocap.cs.cmu.edu/), conversión BVH de 2010
(B. Hahne), copia en github.com/una-dinosauria/cmu-mocap. Licencia: "CMU places no restrictions on the use of the
original dataset" — se permite uso comercial. La conversión BVH de B. Hahne (READMEFIRST.txt de la copia): "I (Bruce) place no additional restrictions on the use of this particular" conversión. Crédito sugerido en la descripción: "Motion capture: CMU Graphics Lab Motion Capture Database".

| Nombre en el kit | Archivo | Descripción CMU | Uso |
|---|---|---|---|
| caminar | 08_01 | walk | `walk_to` de humanos |
| correr | 02_03 | run/jog | disponible |
| saltar | 16_05 | forward jump | disponible |
| saltar_alto | 13_11 | forward jump | disponible |
| remar | 79_95 | rowing | disponible |
| contento | 79_69 | very happy | disponible |
| pensar | 77_01 (desde 1 s) | looking around | `think` de humanos |
| saludar | 13_26 | direct traffic, wave | disponible |
| empujar | 81_05 | push heavy object | disponible |

Uso: `a.mocap("contento", frames=48)` · `a.mocap("caminar", travel_to=1.6)` · `root=False` aplica solo la pose.
Desactivar: `STUDIO_MOCAP=0` (vuelve a la animación por código).
