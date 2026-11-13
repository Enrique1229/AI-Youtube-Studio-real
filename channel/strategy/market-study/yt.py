"""Lectura de páginas públicas de YouTube para el estudio de mercado (no es la API oficial)."""
import json, re, sys, urllib.parse, urllib.request
UA = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/126 Safari/537.36", "Accept-Language": "en", "Cookie": "CONSENT=YES+1; SOCS=CAI"}
def get(url):
    return urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=40).read().decode(errors="replace")
def data(html, var="ytInitialData"):
    m = re.search(r"(?:var |window\[\")?" + var + r"(?:\"\])? = (\{.*?\});(?:</script>|var |\s*if)", html, re.S)
    return json.loads(m.group(1)) if m else None
def text(o):
    if isinstance(o, str): return o
    if not isinstance(o, dict): return ""
    return o.get("simpleText") or o.get("content") or "".join(r.get("text", "") for r in o.get("runs", []))
def walk(o, key, out):
    if isinstance(o, dict):
        if key in o: out.append(o[key])
        for v in o.values(): walk(v, key, out)
    elif isinstance(o, list):
        for v in o: walk(v, key, out)
    return out
def num(s):
    m = re.search(r"([\d.,]+)\s*([KMB]?)", s.replace("\xa0", " "))
    if not m: return None
    v = float(m.group(1).replace(",", "")); return int(v * {"": 1, "K": 1e3, "M": 1e6, "B": 1e9}[m.group(2)])
