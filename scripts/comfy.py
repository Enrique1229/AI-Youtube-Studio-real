"""Cliente mínimo de ComfyUI (API HTTP oficial): /upload/image, /prompt, /history/<id>, /view."""
import json, time, urllib.error, urllib.parse, urllib.request, uuid
from common import CFG, ROOT, die

URL = CFG["image"]["comfy_url"]


def fill(node, vals):
    if isinstance(node, dict):
        return {k: fill(v, vals) for k, v in node.items()}
    if isinstance(node, list):
        return [fill(v, vals) for v in node]
    if isinstance(node, str) and node.startswith("{{") and node.endswith("}}"):
        if node[2:-2] not in vals:
            die(f"el workflow usa el marcador {node} y no está definido en studio.config.json")
        return vals[node[2:-2]]
    return node


def http(path, data=None, headers=None, timeout=120):
    if data is not None and not isinstance(data, bytes):
        data, headers = json.dumps(data).encode(), {"Content-Type": "application/json"}
    req = urllib.request.Request(URL + path, data=data, headers=headers or {})
    try:
        with urllib.request.urlopen(req, timeout=timeout) as r:
            return r.read()
    except urllib.error.HTTPError as e:  # ComfyUI devuelve 400 con node_errors si el workflow no valida
        die(f"ComfyUI {e.code} en {path}: {e.read().decode(errors='replace')[:1500]}")
    except urllib.error.URLError as e:
        die(f"ComfyUI no responde en {URL} ({e.reason})")


def upload_image(path):
    """Sube una imagen a la carpeta input de ComfyUI y devuelve el nombre que usa LoadImage."""
    b = uuid.uuid4().hex
    body = (f"--{b}\r\nContent-Disposition: form-data; name=\"image\"; filename=\"{path.name}\"\r\n"
            f"Content-Type: image/png\r\n\r\n").encode() + path.read_bytes() + (
            f"\r\n--{b}\r\nContent-Disposition: form-data; name=\"overwrite\"\r\n\r\ntrue\r\n--{b}--\r\n").encode()
    r = json.loads(http("/upload/image", body, {"Content-Type": f"multipart/form-data; boundary={b}"}))
    return f"{r['subfolder']}/{r['name']}" if r.get("subfolder") else r["name"]


def run_workflow(workflow_path, vals, out, timeout_s):
    """Ejecuta un workflow en formato API y guarda en `out` el primer archivo que produzca (imagen o vídeo)."""
    wf = fill(json.loads((ROOT / workflow_path).read_text()), vals)
    pid = json.loads(http("/prompt", {"prompt": wf, "client_id": uuid.uuid4().hex}))["prompt_id"]
    t0 = time.time()
    while time.time() - t0 < timeout_s:
        hist = json.loads(http(f"/history/{pid}"))
        if pid in hist:
            for node in hist[pid].get("outputs", {}).values():
                for key in ("images", "video", "videos", "gifs"):  # SaveVideo informa bajo "images" con animated=True
                    for f in node.get(key, []) if isinstance(node.get(key), list) else []:
                        q = urllib.parse.urlencode({k: f.get(k, "") for k in ("filename", "subfolder", "type")})
                        out.write_bytes(http(f"/view?{q}", timeout=600))
                        return time.time() - t0
            die(f"ComfyUI terminó sin archivos de salida: {json.dumps(hist[pid].get('status'))[:600]}")
        time.sleep(2)
    die(f"ComfyUI: tiempo de espera agotado ({timeout_s} s)")
