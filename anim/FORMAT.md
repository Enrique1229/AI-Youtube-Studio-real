# Formato ANIMACIÓN — comedia física por niveles de IQ

Referencia de mercado (2026-11-14): la fórmula "distintos niveles de IQ ante el mismo problema" funciona en animación hecha a mano
(Agbaps Shorts, 9,39 M de suscriptores, mediana 2 M de vistas por Short, animado en Blender; Maizen en Minecraft; variantes con countryballs).
Detalle: `FORMAT-STUDY-AGBAPS.md`. Nosotros imitamos la FÓRMULA, no el contenido.

## Estructura de un episodio
- Short vertical sin diálogo ni narración, de 15-25 s. Decidido por el usuario (2026-11-15): la versión rápida es la buena. El montaje acelera 1,5x por defecto (`anim_build.py --speed`).
- El último plano debe poder enlazar con el primero (bucle).
- Un problema físico y 5 niveles, de la solución más torpe a la más ingeniosa.
- Rótulo fijo arriba: "IQ" y una cifra que sube de negativa (roja) a muy alta (verde).
- Sonido: efectos sincronizados con cada acción (aprobados por el usuario) y MÚSICA DE FONDO con ritmo en todos los vídeos (pedido por el usuario). La música es original, sintetizada por `audio_gen.comedy_music`, distinta en cada episodio (tempo, tonalidad y melodía). No imita la de ningún canal: no se ha podido oír la de referencia.
- Título: "Cada nivel de IQ [haciendo X]" / "IQ bajo vs IQ alto: [X]".

## Mundo y personajes propios
- Decidido por el usuario (2026-11-15): los personajes son HUMANOS y NO se repite el mismo en todos los Shorts.
- Decidido por el usuario (2026-11-16): proporciones como las del canal de referencia: larguiruchos, extremidades largas con codos y rodillas, cabeza proporcionada, ojos grandes y saltones con el párpado a media altura (cara de aburrido), cejas gruesas, labios marcados y pelo con textura. Diseño propio: no se copian sus personajes.
- Cada episodio tiene su propio protagonista humano, generado a partir del nombre del archivo del episodio (`kit.look_for`): 6 tonos de piel, 9 peinados (incluidos rizos con textura), 5 colores de pelo, 12 colores de camiseta, camiseta/tirantes/sin camiseta, pantalón corto o largo, 5 complexiones, gafas y sombrero opcionales. Dentro del episodio es SIEMPRE el mismo.
- Un episodio puede fijar su aspecto con `LOOK = {...}` si el gag lo pide. Las criaturas (`kind` distinto de "humano") siguen existiendo para secundarios o mascotas.
- La variedad de aspecto es aleatoria y no tiene relación con el nivel de IQ: el mismo personaje hace todos los niveles.
- Escenarios: `rio` (hecho). Por construir: desierto, castillo, mina, playa, aula.
- Prohibido: personajes, escenarios reconocibles, marcas de agua o gags concretos de otros canales.

## Qué NO hacemos
- Burlarnos de grupos de personas. El "IQ" es una escalera de ingenio del mismo personaje, no una etiqueta para nadie.
- Repetir el mismo problema con el mismo desenlace: cada episodio cambia el problema y al menos 3 de las 5 soluciones.

## Lo observado en 4 Shorts del canal de referencia (fotogramas, 2026-11-15)
`channel/strategy/market-study/agbaps-4-shorts-usuario.jpg`
- No todo son niveles de IQ: también sketches "POV: …" con un texto fijo arriba y objetos con vida propia.
- Personajes humanoides de cuerpo completo, recurrentes; escenarios detallados (aula, refugio de animales, calle).
- En el de IQ los niveles no van en orden ascendente (+1002, -234, +6070).
- Nuestro episodio 1 (una criatura sencilla en un prado) está por debajo de ese nivel de detalle. Siguiente mejora necesaria: personajes humanoides articulados y escenarios más ricos a partir de modelos 3D con licencia de uso comercial.
