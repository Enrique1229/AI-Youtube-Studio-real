#!/usr/bin/env python3
"""yt_lookup.py [--channels] "<búsqueda>"  —  cifras públicas de YouTube para la puerta de mercado.

Lee la página pública de resultados de YouTube (no es la API oficial: puede dejar de funcionar si
YouTube cambia la página; la vía estable es la YouTube Data API con una clave propia).
  por defecto   vídeos: vistas | antigüedad | duración | canal | título
  --channels    canales: suscriptores | nº de vídeos | nombre | id
Solo devuelve lo que YouTube muestra: no dice si un canal está monetizado.
"""
import _utf8  # noqa: F401  (primero: UTF-8 en Windows)
import json, re, sys, urllib.parse, urllib.request


def text(o):
    if not isinstance(o, dict):
        return ""
    return o.get("simpleText") or "".join(r.get("text", "") for r in o.get("runs", []))


def walk(o, key, out):
    if isinstance(o, dict):
        if key in o:
            out.append(o[key])
        for v in o.values():
            walk(v, key, out)
    elif isinstance(o, list):
        for v in o:
            walk(v, key, out)


def main():
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    channels = "--channels" in sys.argv
    if not args:
        sys.exit(__doc__)
    url = "https://www.youtube.com/results?search_query=" + urllib.parse.quote_plus(args[0]) + ("&sp=EgIQAg%3D%3D" if channels else "")
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)", "Accept-Language": "en"})
    try:
        html = urllib.request.urlopen(req, timeout=30).read().decode(errors="replace")
    except Exception as e:
        sys.exit(f"ERROR: no se pudo leer YouTube ({e})")
    m = re.search(r"var ytInitialData = (\{.*?\});</script>", html, re.S)
    if not m:
        sys.exit("ERROR: YouTube no devolvió datos legibles (página cambiada o bloqueo)")
    data, out = json.loads(m.group(1)), []
    if channels:
        walk(data, "channelRenderer", out)
        for c in out[:15]:
            print(f"{text(c.get('videoCountText')) or '?':>18} | {text(c.get('subscriberCountText')) or '?':>22} | {text(c.get('title'))} | {c.get('channelId')}")
    else:
        walk(data, "videoRenderer", out)
        for v in out[:20]:
            print(f"{text(v.get('viewCountText')) or '?':>18} | {text(v.get('publishedTimeText')) or '?':>14} | {text(v.get('lengthText')) or 'short?':>7} | "
                  f"{text(v.get('ownerText'))[:28]:28} | {text(v.get('title'))[:70]}")
        shorts = []
        walk(data, "shortsLockupViewModel", shorts)
        for sh in shorts[:20]:  # Shorts: YouTube solo da un texto de accesibilidad con título y vistas
            print(f"{'SHORT':>18} | {sh.get('accessibilityText', '')[:150]}")
        out += shorts
    if not out:
        print("sin resultados")


if __name__ == "__main__":
    main()
