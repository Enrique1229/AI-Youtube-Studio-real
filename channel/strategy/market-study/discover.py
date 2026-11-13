import sys, json, urllib.parse
from yt import *
qs = ["HFY stories", "HFY sci-fi stories", "sci-fi stories narrated", "space horror stories narrated", "sci-fi creepypasta",
      "HFY español", "historias de ciencia ficción narradas", "relatos de ciencia ficción", "relatos de terror narrados",
      "historias de misterio narradas", "creepypasta español", "relatos de terror para dormir", "historias HFY en español humanidad",
      "cuentos de ciencia ficción audiolibro", "historias de fantasía narradas"]
found = {}
for q in qs:
    try:
        d = data(get("https://www.youtube.com/results?search_query=" + urllib.parse.quote_plus(q) + "&sp=EgIQAg%3D%3D"))
    except Exception as e:
        print("fallo", q, e); continue
    for c in walk(d, "channelRenderer", []):
        h = text(c.get("subscriberCountText"))  # en este layout: el handle
        subs = num(text(c.get("videoCountText")) or "0")  # y aquí los suscriptores
        if h.startswith("@") and subs and subs >= 3000:
            found.setdefault(h, {"title": text(c.get("title")), "subs": subs, "q": q})
json.dump(found, open("candidates.json", "w"), ensure_ascii=False, indent=1)
for h, c in sorted(found.items(), key=lambda x: -x[1]["subs"]): print(f"{c['subs']:>9} | {h:32} | {c['title'][:34]:34} | {c['q']}")
