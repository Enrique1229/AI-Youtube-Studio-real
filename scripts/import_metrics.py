#!/usr/bin/env python3
"""import_metrics.py [--days 90]  —  YouTube Analytics API -> channel/analytics/videos.csv

ESTADO: NO PROBADO (requiere tus credenciales de Google; no se pudo ejecutar al escribirlo).
Usa el informe "Top videos" de developers.google.com/youtube/analytics/channel_reports (consultado el 2026-11-13):
dimensión video, maxResults <= 200, orden -views. Métricas: views, averageViewDuration, averageViewPercentage,
likes, comments, shares, subscribersGained. Solo cubre los 200 vídeos más vistos del periodo.
El CTR de miniatura NO figura entre las métricas de ese informe: copia el CTR a mano desde YouTube Studio en la
columna ctr de videos.csv; este script lo conserva en cada importación.

Preparación (una vez, manual):
  1. Google Cloud Console: crea un proyecto, activa "YouTube Analytics API", crea credenciales OAuth
     de tipo "Desktop app" y guarda el JSON como channel/analytics/client_secret.json (está en .gitignore).
  2. pip install google-api-python-client google-auth-oauthlib
  3. Tras subir cada vídeo: python3 scripts/studio.py set <story-id> youtube_id <ID del vídeo>
Solo importa vídeos cuya historia tenga youtube_id. Alternativa sin API: rellenar videos.csv a mano.
"""
import csv, datetime, json, pathlib, sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
AN = ROOT / "channel" / "analytics"
COLS = "story_id,format,title,published,tags,views,ctr,avd_s,pct_viewed,likes,comments,shares,subs_gained".split(",")
BASE = "views,averageViewDuration,averageViewPercentage,likes,comments,shares,subscribersGained"


def main():
    days = int(sys.argv[sys.argv.index("--days") + 1]) if "--days" in sys.argv else 90
    stories = {}
    for p in (ROOT / "stories").glob("story-*/state.json"):
        st = json.loads(p.read_text())
        if st.get("youtube_id"):
            idea = p.parent / "idea.json"
            st["tags"] = " ".join(json.loads(idea.read_text()).get("tags", [])) if idea.exists() else ""
            stories[st["youtube_id"]] = st
    if not stories:
        sys.exit("Ninguna historia tiene youtube_id. Usa: studio.py set <story-id> youtube_id <ID>")
    from google_auth_oauthlib.flow import InstalledAppFlow
    from google.oauth2.credentials import Credentials
    from googleapiclient.discovery import build
    scopes = ["https://www.googleapis.com/auth/yt-analytics.readonly"]
    tok = AN / "token.json"
    if tok.exists():
        creds = Credentials.from_authorized_user_file(str(tok), scopes)
    else:
        creds = InstalledAppFlow.from_client_secrets_file(str(AN / "client_secret.json"), scopes).run_local_server(port=0)
        tok.write_text(creds.to_json())
    yt = build("youtubeAnalytics", "v2", credentials=creds)
    end = datetime.date.today()
    # Informe "Top videos" (channel_reports): dimensión video, maxResults <= 200, orden -views, sin filtro por vídeo.
    rep = yt.reports().query(ids="channel==MINE", startDate=str(end - datetime.timedelta(days=days)), endDate=str(end),
                             dimensions="video", maxResults=200, sort="-views", metrics=BASE).execute()
    names = [h["name"] for h in rep["columnHeaders"]]
    csvp = AN / "videos.csv"  # el CTR no está en este informe de la API: se conserva el que hayas puesto a mano
    old = {r["story_id"]: r.get("ctr", "") for r in csv.DictReader(csvp.open())} if csvp.exists() else {}
    rows = []
    for r in rep.get("rows", []):
        m = dict(zip(names, r))
        if m["video"] not in stories:
            continue
        st = stories[m["video"]]
        rows.append({"story_id": st["id"], "format": st["format"], "title": st["title"], "published": st.get("published", ""),
                     "tags": st["tags"], "views": m["views"], "ctr": old.get(st["id"], ""),
                     "avd_s": m["averageViewDuration"], "pct_viewed": m["averageViewPercentage"], "likes": m["likes"],
                     "comments": m["comments"], "shares": m["shares"], "subs_gained": m["subscribersGained"]})
    with (AN / "videos.csv").open("w", newline="") as f:
        w = csv.DictWriter(f, COLS)
        w.writeheader()
        w.writerows(rows)
    print(f"{len(rows)} vídeos importados")


if __name__ == "__main__":
    main()
