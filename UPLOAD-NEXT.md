# Próximos Shorts — renderizar, comprobar y subir SIN gastar uso (Klunk Studio)

Orden de publicación recomendado (no seguidos dos de objetos el mismo día): **huevo** → al día siguiente → **pompa**.

## 1. En PowerShell (uno detrás de otro; cada render tarda ~25-35 min)
```
cd C:\Users\enriq\AI-Youtube-Studio-real
git pull
python scripts/render_episode.py anim/episodes/ep003.py render/ep003
python scripts/render_episode.py anim/episodes/ep004.py render/ep004
python scripts/qc_local.py render/ep003/ep003.mp4 render/ep004/ep004.mp4
```
Si `qc_local` dice **OK** para cada uno, sube el archivo `*_SUBIR.mp4` que indica. Si dice **FALLO**, no lo subas.
Míralo antes de subir: si ves algo raro (algo atraviesa a otro objeto, una cara cortada…), no lo subas.

## 2. Ajustes comunes al subir
Made for kids: No (decisión tuya) · AI use: No · Category: Comedy · Language: English · License: Standard ·
Comments: On + "Hold potentially inappropriate comments" · Shorts remixing: permitido · Playlist: "Objects With Faces".

## 3. Huevo — `render\ep003\ep003_SUBIR.mp4`
**Title:** The Sleepwalking Egg Falls Off the Counter (Safely)
**Description:**
```
An egg walks in its sleep, eyes closed, straight toward the edge of the counter. A spoon tries to help, but the real rescue comes from somewhere else.
A silent 3D short. Fiction made with AI-assisted tools; nothing here is real footage or a real event.
Follow Klunk Studio for more silent gags with a twist.

Original animation, music and sound effects.
#shorts #silentcomedy #3danimation #objectswithfaces #funnyshorts
```
**Tags:** `sleepwalking egg, egg cup, objects with faces, silent comedy, 3D animation, funny shorts, breakfast comedy, cartoon comedy`

## 4. Pompa — `render\ep004\ep004_SUBIR.mp4`
**Title:** One Bubble Pops, the Sponge Makes Another
**Description:**
```
A bubble with a face drifts past a fork and a pencil toward the window. Not every bubble makes it, but the sponge has one more trick.
A silent 3D short. Fiction made with AI-assisted tools; nothing here is real footage or a real event.
Follow Klunk Studio for more silent gags with a twist.

Original animation, music and sound effects.
#shorts #silentcomedy #3danimation #objectswithfaces #funnyshorts
```
**Tags:** `bubble, sponge, objects with faces, silent comedy, 3D animation, funny shorts, kitchen comedy, cartoon comedy`

## 5. Después
Anota cada enlace publicado. Cuando vuelvas a tener uso, pásamelos junto con capturas de Analytics de los 4 vídeos
(visualizaciones, "Viewed vs. swiped away", duración media, me gusta, suscriptores) y ajusto la estrategia.
