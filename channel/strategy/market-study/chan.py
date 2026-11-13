import sys, json, re, statistics
from yt import *
h = sys.argv[1]
base = f"https://www.youtube.com/{h}" if h.startswith("@") else f"https://www.youtube.com/channel/{h}"
html = get(base + "/videos"); d = data(html)
meta = (walk(d, "channelMetadataRenderer", []) or [{}])[0]
hdr = " | ".join(t for t in (text(x) for x in walk(d.get("header", {}), "metadataParts", [[]])[0:1] for x in []) )
subs = re.search(r'"([\d.,]+[KMB]?) subscribers"', html); vids = re.search(r'"([\d.,]+[KMB]?) videos"', html)
rows = []
for v in walk(d, "lockupViewModel", []):
    if v.get("contentType") not in (None, "LOCKUP_CONTENT_TYPE_VIDEO"): continue
    blob = json.dumps(v, ensure_ascii=False)
    title = text(v.get("metadata", {}).get("lockupMetadataViewModel", {}).get("title", {}))
    parts = walk(v.get("metadata", {}), "metadataParts", [])
    parts = parts[0] if parts else []
    vtxt = text(parts[0].get("text")) if parts else ""; atxt = text(parts[1].get("text")) if len(parts) > 1 else ""
    vm = re.match(r"[\d.,]+[KMB]?$", vtxt); ag = re.match(r".*ago$", atxt)
    class _M:  # adaptador mínimo
        def __init__(s, t): s.t = t
        def group(s, i): return s.t
    vm = _M(vtxt) if vm else None; ag = _M(atxt) if ag else None
    ln = re.search(r'"thumbnailBadgeViewModel": \{"text": "([\d:]+)"', blob)
    rows.append({"id": v.get("contentId"), "title": title, "views": num(vm.group(1)) if vm else 0,
                 "age": ag.group(1) if ag else "", "len": ln.group(1) if ln else ""})
seen = set(); rows = [r for r in rows if not (r["id"] in seen or seen.add(r["id"]))]
def mins(l):
    p = [int(x) for x in l.split(":")] if l else [0]
    return (p[-1] + 60 * (p[-2] if len(p) > 1 else 0) + 3600 * (p[-3] if len(p) > 2 else 0)) / 60
vw = [r["views"] for r in rows if r["views"] is not None]; ln = [mins(r["len"]) for r in rows if r["len"]]
out = {"handle": h, "title": meta.get("title"), "subs": subs.group(1) if subs else None, "videos": vids.group(1) if vids else None,
       "desc": (meta.get("description") or "")[:300].replace("\n", " "), "n": len(rows),
       "median_views": int(statistics.median(vw)) if vw else None, "max_views": max(vw) if vw else None, "min_views": min(vw) if vw else None,
       "median_min": round(statistics.median(ln), 1) if ln else None, "oldest_in_page": rows[-1]["age"] if rows else None,
       "join": bool(walk(d, "sponsorButton", [])) or '"Join"' in html, "rows": rows}
json.dump(out, open(f"ch_{h.strip('@')}.json", "w"), ensure_ascii=False, indent=1)
print(f"{out['title']} | subs {out['subs']} | vídeos {out['videos']} | muestra {out['n']} (hasta {out['oldest_in_page']}) | mediana {out['median_views']} vistas (min {out['min_views']}, max {out['max_views']}) | duración mediana {out['median_min']} min | membresías: {out['join']}")
for r in rows[:6]: print("   ", f"{r['views']:>9} | {r['age']:>13} | {r['len']:>8} | {r['title'][:85]}")
