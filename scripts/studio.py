#!/usr/bin/env python3
"""AI YouTube Studio - utilidades deterministas (0 tokens de LLM).

  new <short|long|relato> "<titulo>"   crea stories/story-NNN desde templates (relato = 25-60 min narrado, 16:9)
  select <batch> <idea-id> ["titulo"] [--force]   crea la historia desde una idea puntuada (exige VPS >= umbral y validación de mercado)
  derive <parent-id> "<titulo>"   crea un short derivado de una historia larga (hereda la puerta critic)
  close-batch <batch>           registra en el ledger como rechazadas las ideas no seleccionadas
  status [--brief]              estado de todas las producciones
  set <id> <clave> <valor>      actualiza state.json (stage, gates.qc, quality_score...)
  vps <scores.json>             calcula el Virality Potential Score y ordena
  ledger [--brief] | ledger add <id> "<logline>" <estado> [vps]
  similar "<texto>" | similar --story <id>   similitud con ideas previas (0-1)
  gate <id>                     falla si alguna puerta no es PASS
  probe <id>                    informe técnico (ffprobe) del vídeo final
  sheet <id>                    hoja de contactos de las imágenes (reviews/contact-sheet.png) para la revisión visual
  deliver <id>                  copia a shorts/ o long-videos/ SOLO si gate pasa
  analytics                     agregados de channel/analytics/videos.csv
"""
import _utf8  # noqa: F401  (primero: UTF-8 en Windows)
import csv, json, re, shutil, subprocess, sys, datetime, pathlib, statistics

ROOT = pathlib.Path(__file__).resolve().parent.parent
STORIES = ROOT / "stories"
LEDGER = ROOT / "channel" / "strategy" / "ideas-ledger.jsonl"
GATES = ["critic", "market", "continuity", "policy", "qc"]
# Pesos positivos (suman 100) y penalizaciones máximas.
W = {"hook": 20, "curiosity": 15, "retention": 15, "originality": 12, "visual": 8,
     "emotion": 8, "ending": 10, "series": 6, "differentiation": 6}
PEN = {"production_difficulty": 5, "repetition_risk": 10}
STOP = set("el la los las un una unos unas de del y o que en a con por para su sus se lo al es".split())


def die(msg):
    sys.exit(f"ERROR: {msg}")


def sdir(sid):
    d = STORIES / sid
    if not d.is_dir():
        die(f"no existe {d}")
    return d


def load_state(sid):
    return json.loads((sdir(sid) / "state.json").read_text())


def save_state(sid, st):
    st["updated"] = datetime.date.today().isoformat()
    (sdir(sid) / "state.json").write_text(json.dumps(st, indent=2, ensure_ascii=False) + "\n")


def cmd_new(fmt, title):
    if fmt not in ("short", "long", "relato"):
        die("formato debe ser short, long o relato")
    nums = [int(m.group(1)) for p in STORIES.glob("story-*") if (m := re.match(r"story-(\d+)$", p.name))]
    sid = f"story-{max(nums, default=0) + 1:03d}"
    d = STORIES / sid
    for sub in ["chapters", "scenes", "visual-prompts", "voice", "assets", "final", "reviews"]:
        (d / sub).mkdir(parents=True, exist_ok=True)
    for f in ["story-bible.md", "continuity.md"] + (["characters.md", "world.md"] if fmt in ("long", "relato") else []):
        src = ROOT / "templates" / {"characters.md": "character.md"}.get(f, f)
        if not (d / f).exists():
            (d / f).write_text(src.read_text() if src.exists() else f"# {f}\n")
    save_state(sid, {"id": sid, "format": fmt, "title": title, "stage": "created",
                     "gates": {g: "PENDING" for g in GATES}, "vps": None,
                     "quality_score": None, "fix_rounds": 0, "final_file": None})
    print(sid)
    return sid


def ledger_add(iid, logline, status, score=None):
    LEDGER.parent.mkdir(parents=True, exist_ok=True)
    with LEDGER.open("a") as f:
        f.write(json.dumps({"id": iid, "logline": logline, "status": status, "vps": score,
                            "date": datetime.date.today().isoformat()}, ensure_ascii=False) + "\n")


def batch(b):
    d = ROOT / "ideas" / b
    ideas = {i["id"]: i for i in json.loads((d / "ideas.json").read_text())}
    scores = {s["id"]: s for s in json.loads((d / "scores.json").read_text())}
    for s in scores.values():
        s.setdefault("vps", vps(s["scores"]))
    return d, ideas, scores


def cmd_select(b, iid, *rest):
    force = "--force" in rest
    rest = [x for x in rest if x != "--force"]
    d, ideas, scores = batch(b)
    if iid not in ideas or iid not in scores:
        die(f"{iid} no está en ideas.json y scores.json de {b}")
    idea, sc = ideas[iid], scores[iid]
    thr = json.loads((ROOT / "studio.config.json").read_text())["vps_threshold"][idea["format"]]
    if sc["vps"] < thr and not force:
        die(f"{iid}: VPS {sc['vps']} < umbral {thr} para {idea['format']} (usa --force solo con motivo)")
    mk = d / "market.json"
    market = {m["id"]: m for m in json.loads(mk.read_text())}.get(iid) if mk.exists() else None
    if not force and (not market or market.get("verdict") not in ("VALIDATED", "WEAK")):
        die(f"{iid}: sin validación de mercado (market-validator debe dar VALIDATED o WEAK en {mk.relative_to(ROOT)}); "
            f"veredicto actual: {market.get('verdict') if market else 'no evaluada'}")
    sid = cmd_new(idea["format"], rest[0] if rest else idea["logline"][:60])
    sd = sdir(sid)
    if market:
        (sd / "reviews" / "market.json").write_text(json.dumps(market, indent=2, ensure_ascii=False) + "\n")
    idea = dict(idea, vps=sc["vps"], batch=b, story_id=sid, critic_improve=sc.get("improve"))
    (sd / "idea.json").write_text(json.dumps(idea, indent=2, ensure_ascii=False) + "\n")
    (sd / "reviews" / "critic.json").write_text(json.dumps(sc, indent=2, ensure_ascii=False) + "\n")
    st = load_state(sid)
    st.update(vps=sc["vps"], stage="selected", idea_id=iid)
    st["gates"]["critic"] = "PASS"
    st["gates"]["market"] = "PASS" if market and market.get("verdict") in ("VALIDATED", "WEAK") else "PENDING"
    st["market_verdict"] = market.get("verdict") if market else None
    save_state(sid, st)
    sel = d / "selected.json"
    cur = json.loads(sel.read_text()) if sel.exists() else []
    sel.write_text(json.dumps([c for c in cur if c["id"] != iid] + [idea], indent=2, ensure_ascii=False) + "\n")
    ledger_add(iid, idea["logline"], "selected", sc["vps"])


def cmd_derive(parent, title):
    pst = load_state(parent)
    if pst["gates"]["critic"] != "PASS":
        die(f"{parent} no tiene la puerta critic en PASS")
    sid = cmd_new("short", title)
    st = load_state(sid)
    st.update(derived_from=parent, vps=pst.get("vps"), stage="selected")
    st["gates"]["critic"] = "PASS"
    st["gates"]["market"] = "PENDING"  # un short derivado es otro formato: necesita su propia validación de mercado
    (sdir(sid) / "reviews" / "director-notes.md").write_text(
        f"# Notas del Director — {sid}\n- Short derivado a propósito de {parent} (mismo universo, serie). "
        "Debe tener protagonista o punto de vista y giro distintos, y no revelar el final del original.\n")
    save_state(sid, st)


def cmd_close_batch(b):
    _, ideas, scores = batch(b)
    done = {r["id"] for r in read_ledger()}
    n = 0
    for iid, idea in ideas.items():
        if iid not in done:
            ledger_add(iid, idea["logline"], "rejected", scores.get(iid, {}).get("vps"))
            n += 1
    print(f"{n} ideas registradas como rechazadas")


def cmd_status(brief=False):
    rows = []
    for p in sorted(STORIES.glob("story-*/state.json")):
        s = json.loads(p.read_text())
        mark = {"PASS": "ok", "PENDING": "--", "FAIL": "FALLO", "STOP": "STOP"}
        g = " ".join(f"{k}:{mark.get(v, v)}" for k, v in s["gates"].items())
        rows.append(f"{s['id']} {s['format']:5} {s['stage']:12} [{g}] q={s.get('quality_score')} {s['title'][:40]}")
    if brief:
        rows = [r for r in rows if " delivered " not in r][-10:]
    print("\n".join(rows) if rows else "Sin producciones en curso.")


def cmd_set(sid, key, value):
    st = load_state(sid)
    try:
        value = json.loads(value)
    except ValueError:
        pass
    if key.startswith("gates."):
        g = key.split(".", 1)[1]
        if g not in GATES or value not in ("PENDING", "PASS", "FAIL", "STOP"):
            die("puerta o valor no válido")
        st["gates"][g] = value
    else:
        st[key] = value
    save_state(sid, st)


def vps(s):
    base = sum(w * s[k] / 10 for k, w in W.items())
    pen = sum(m * (s[k] - 1) / 9 for k, m in PEN.items())
    return round(base - pen, 1)


def cmd_vps(path):
    p = pathlib.Path(path)
    data = json.loads(p.read_text())
    for it in data:
        it["vps"] = vps(it["scores"])
    data.sort(key=lambda x: -x["vps"])
    p.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n")
    for it in data:
        print(f"{it['vps']:5}  {it['id']}")


def read_ledger():
    if not LEDGER.exists():
        return []
    rows = {}
    for l in LEDGER.read_text().splitlines():
        if l.strip():
            r = json.loads(l)
            rows[r["id"]] = r  # la última entrada de cada idea manda
    return list(rows.values())


def cmd_ledger(args):
    if args[:1] == ["add"]:
        ledger_add(args[1], args[2], args[3], float(args[4]) if len(args) > 4 else None)
        return
    rows = read_ledger()
    if "--brief" in args:
        rows = rows[-40:]
    for r in rows:
        print(f"{r['status']:9} {r['logline'][:110]}")


def toks(t):
    return {w for w in re.findall(r"[a-záéíóúñü]{4,}", t.lower()) if w not in STOP}


def cmd_similar(args):
    if args[0] == "--story":
        idea = json.loads((sdir(args[1]) / "idea.json").read_text())
        text, skip = idea["logline"], idea.get("id")
    else:
        text, skip = args[0], None
    a, best = toks(text), (0.0, "")
    for r in read_ledger():
        if r["id"] == skip:
            continue
        b = toks(r["logline"])
        j = len(a & b) / len(a | b) if a | b else 0
        best = max(best, (j, r["logline"]))
    print(f"{best[0]:.2f}  {best[1][:100]}")


def cmd_gate(sid, quiet=False):
    bad = {k: v for k, v in load_state(sid)["gates"].items() if v != "PASS"}
    if bad:
        die(f"{sid} no aprobado: {bad}")
    if not quiet:
        print(f"{sid}: todas las puertas PASS")


def cmd_probe(sid):
    st = load_state(sid)
    f = st.get("final_file") and ROOT / st["final_file"]
    if not f or not f.exists():
        die("final_file no definido o no existe")
    out = subprocess.run(["ffprobe", "-v", "error", "-show_entries",
                          "format=duration,size:stream=codec_type,codec_name,width,height,r_frame_rate",
                          "-of", "json", str(f)], capture_output=True, text=True, check=True).stdout
    vol = subprocess.run(["ffmpeg", "-i", str(f), "-af", "volumedetect", "-vn", "-f", "null", "-"],
                         capture_output=True, text=True).stderr
    info = json.loads(out)
    info["audio_levels"] = re.findall(r"(mean_volume|max_volume): (-?[\d.]+ dB)", vol)
    exp = (1080, 1920) if st["format"] == "short" else (1920, 1080)
    v = next((s for s in info["streams"] if s["codec_type"] == "video"), {})
    dur = float(info["format"]["duration"])
    checks = {"placeholder_images": (sdir(sid) / "assets" / "PLACEHOLDER").exists(),
              "resolution_ok": (v.get("width"), v.get("height")) == exp,
              "has_audio": any(s["codec_type"] == "audio" for s in info["streams"]),
              "duration_ok": {"short": dur <= 180, "long": 180 <= dur <= 1200, "relato": dur >= 1200}[st["format"]]}
    info["checks"] = checks
    print(json.dumps(info, indent=1))


def cmd_sheet(sid):
    d = sdir(sid)
    n = len(list((d / "assets" / "images").glob("*.png")))
    if not n:
        die("no hay imágenes")
    cols = 6 if n > 6 else n
    rows = -(-n // cols)
    w, h = (192, 336) if load_state(sid)["format"] == "short" else (336, 192)
    out = d / "reviews" / "contact-sheet.png"
    lst = d / "assets" / "sheet.txt"  # lista explícita: el ffmpeg de Windows no admite -pattern_type glob
    lst.write_text("".join(f"file '{p.as_posix()}'\nduration 1\n" for p in sorted((d / "assets" / "images").glob("*.png"))))
    subprocess.run(["ffmpeg", "-y", "-v", "error", "-f", "concat", "-safe", "0", "-i", str(lst),
                    "-vf", f"scale={w}:{h},tile={cols}x{rows}", "-frames:v", "1", str(out)], check=True)
    lst.unlink()
    print(out.relative_to(ROOT).as_posix())


def cmd_deliver(sid):
    cmd_gate(sid, quiet=True)
    st = load_state(sid)
    if (sdir(sid) / "assets" / "PLACEHOLDER").exists():
        die(f"{sid} usa imágenes de prueba (placeholder): no entregable")
    if not (st.get("final_file") and (ROOT / st["final_file"]).exists()):
        die(f"{sid} no tiene vídeo final")
    dest = ROOT / {"short": "shorts", "long": "long-videos", "relato": "relatos"}[st["format"]] / sid
    shutil.copytree(sdir(sid) / "final", dest, dirs_exist_ok=True)
    st["stage"] = "delivered"
    save_state(sid, st)
    print(dest.relative_to(ROOT))


def cmd_analytics():
    f = ROOT / "channel" / "analytics" / "videos.csv"
    if not f.exists():
        die(f"falta {f.relative_to(ROOT)} (ver templates/videos.csv)")
    rows = list(csv.DictReader(f.open()))
    num = ["views", "ctr", "avd_s", "pct_viewed", "likes", "comments", "shares", "subs_gained"]
    for fmt in ("short", "long", "relato"):
        rs = [r for r in rows if r["format"] == fmt]
        if not rs:
            continue
        print(f"## {fmt} (n={len(rs)})")
        for k in num:
            vals = [float(r[k]) for r in rs if r.get(k)]
            if vals:
                print(f"{k}: mediana={statistics.median(vals):.1f} media={statistics.mean(vals):.1f}")
        rs.sort(key=lambda r: -float(r["pct_viewed"] or 0))
        for label, grp in (("TOP", rs[:3]), ("BOTTOM", rs[-3:] if len(rs) > 3 else [])):
            for r in grp:
                print(f"{label} {r['story_id']} views={r['views']} ctr={r['ctr']} pct={r['pct_viewed']} tags={r.get('tags','')} | {r['title'][:50]}")


def main():
    a = sys.argv[1:]
    if not a:
        die(__doc__)
    c, r = a[0], a[1:]
    {"new": lambda: cmd_new(*r), "select": lambda: cmd_select(*r), "close-batch": lambda: cmd_close_batch(*r),
     "derive": lambda: cmd_derive(*r),
     "status": lambda: cmd_status("--brief" in r),
     "set": lambda: cmd_set(*r), "vps": lambda: cmd_vps(*r), "ledger": lambda: cmd_ledger(r),
     "similar": lambda: cmd_similar(r), "gate": lambda: cmd_gate(*r), "probe": lambda: cmd_probe(*r),
     "deliver": lambda: cmd_deliver(*r), "sheet": lambda: cmd_sheet(*r), "analytics": cmd_analytics}.get(c, lambda: die(__doc__))()


if __name__ == "__main__":
    main()
