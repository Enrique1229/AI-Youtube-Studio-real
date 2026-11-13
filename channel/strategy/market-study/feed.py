import sys, re, json, io, datetime, statistics, urllib.request, xml.etree.ElementTree as ET
from yt import *
from PIL import Image
NS = {"a": "http://www.w3.org/2005/Atom", "m": "http://search.yahoo.com/mrss/", "y": "http://www.youtube.com/xml/schemas/2015"}
PAT = {"IA": r"\bAI\b|artificial intelligence|\bIA\b|inteligencia artificial|ai[- ]generated|generad[oa]s? (con|por) (ia|inteligencia)|text[- ]to[- ]speech|voz sint|synthetic",
       "fuente/autor": r"reddit|r/hfy|r/nosleep|original (story|author)|autor(a)? original|written by|escrit[oa] por|story by|credit|crédit|author:",
       "propia": r"original stor(y|ies)|historias? original(es)?|written by (me|us|our)|de nuestra autoría|exclusive stor",
       "oyentes/real": r"env[ií]a(nos)? tu|manda tu|send (us )?your|submit your|relatos? real(es)?|historias? reales|hechos reales|true stor",
       "apoyo": r"patreon|membres[ií]a|become a member|join this channel|ko-fi|paypal|buymeacoffee|súper gracias",
       "capítulos": r"\b0?0:00\b"}
def run(h):
    html = get(f"https://www.youtube.com/{h}")
    cid = re.search(r'"externalId":"(UC[\w-]{22})"', html) or re.search(r'channel/(UC[\w-]{22})', html)
    xml = get("https://www.youtube.com/feeds/videos.xml?channel_id=" + cid.group(1))
    root = ET.fromstring(xml); es = root.findall("a:entry", NS)
    rows = []
    for e in es:
        g = e.find("m:group", NS); st = g.find("m:community/m:statistics", NS)
        rows.append({"id": e.find("y:videoId", NS).text, "title": e.find("a:title", NS).text, "date": e.find("a:published", NS).text[:10],
                     "views": int(st.get("views")) if st is not None else 0, "desc": g.find("m:description", NS).text or ""})
    ds = [datetime.date.fromisoformat(r["date"]) for r in rows]
    span = (ds[0] - ds[-1]).days or 1
    alltxt = "\n".join(r["desc"] for r in rows)
    flags = {k: sum(1 for r in rows if re.search(p, r["desc"], re.I)) for k, p in PAT.items()}
    print(f"\n### {root.find('a:title', NS).text} ({h}) — creado {root.find('a:published', NS).text[:10]}")
    print(f"últimos {len(rows)} vídeos: del {ds[-1]} al {ds[0]} → {len(rows) / span * 7:.1f} por semana | último hace {(datetime.date(2026, 11, 13) - ds[0]).days} días | mediana {int(statistics.median(r['views'] for r in rows))} vistas")
    print("descripciones que mencionan:", {k: f"{v}/{len(rows)}" for k, v in flags.items()})
    d0 = max(rows, key=lambda r: len(r["desc"]))["desc"]
    print("descripción tipo:", re.sub(r"\s+", " ", rows[0]["desc"])[:330])
    json.dump(rows, open(f"feed_{h.strip('@')}.json", "w"), ensure_ascii=False)
    # fotogramas automáticos (25 %, 50 %, 75 %) de 2 vídeos + miniatura
    tiles = []
    for r in rows[1:3]:
        for f in ("hqdefault", "hq1", "hq2", "hq3"):
            try: tiles.append(Image.open(io.BytesIO(urllib.request.urlopen(urllib.request.Request(f"https://i.ytimg.com/vi/{r['id']}/{f}.jpg", headers=UA), timeout=30).read())).convert("RGB").resize((320, 240)))
            except Exception: tiles.append(Image.new("RGB", (320, 240), (60, 0, 0)))
    sheet = Image.new("RGB", (1280, 480))
    for i, t in enumerate(tiles): sheet.paste(t, ((i % 4) * 320, (i // 4) * 240))
    sheet.save(f"frames_{h.strip('@')}.jpg", quality=80)
for h in sys.argv[1:]:
    try: run(h)
    except Exception as e: print("\n### fallo", h, str(e)[:120])
