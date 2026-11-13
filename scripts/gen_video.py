#!/usr/bin/env python3
"""gen_video.py <story-id> [--test]  —  planos `type: "i2v"` de shots.json -> assets/clips/<shot>.mp4

Anima la imagen ya generada del plano (assets/images/<shot>.png) con un modelo de imagen-a-vídeo
en ComfyUI. Workflow por defecto: templates/comfy/i2v_wan22_5b.json, que reproduce nodo a nodo la
plantilla oficial de ComfyUI "video_wan2_2_5B_ti2v" (Wan 2.2 TI2V 5B, Apache-2.0).
Solo actúa si studio.config.json -> video_gen.enabled es true. Sin clips, assemble.py usa la imagen fija.
--test: genera solo el primer plano i2v e informa del tiempo (para medir si la máquina puede).
"""
import sys
import comfy
from common import CFG, story, state, load, die

V = CFG.get("video_gen", {})
NEG = "static, still frame, blurry details, subtitles, text, watermark, worst quality, low quality, jpeg artifacts, ugly, deformed, extra fingers, bad hands, bad face, fused fingers, cluttered background"


def main(sid, *flags):
    if not V.get("enabled"):
        print("video_gen desactivado en studio.config.json: no se generan clips")
        return
    d = story(sid)
    fmt = state(sid)["format"]
    shots = [s for s in load(d / "visual-prompts" / "shots.json", "lo escribe visual-director") if s.get("type") == "i2v"]
    if "--test" in flags:
        shots = shots[:1] or die("ningún plano tiene type i2v")
    outdir = d / "assets" / "clips"
    outdir.mkdir(parents=True, exist_ok=True)
    w, h = V["size"]["9:16" if fmt == "short" else "16:9"]
    made = 0
    for s in shots:
        out = outdir / f"{s['id']}.mp4"
        img = d / "assets" / "images" / f"{s['id']}.png"
        if out.exists():
            continue
        if not img.exists():
            die(f"falta la imagen de origen {img.name}: ejecuta antes gen_images.py")
        vals = {**V["params"], "image": comfy.upload_image(img), "prompt": s.get("motion_prompt") or s["prompt"],
                "negative": NEG, "seed": int(s.get("seed", 1)), "width": w, "height": h,
                "length": int(V["length"]), "fps": float(V["fps"])}
        secs = comfy.run_workflow(V["workflow"], vals, out, V["timeout_s"])
        made += 1
        print(f"{out.name}: {secs:.0f} s de generación, {V['length']} fotogramas a {V['fps']} fps, {w}x{h}")
    print(f"{made} clips nuevos, {len(shots) - made} ya existían")


if __name__ == "__main__":
    main(*sys.argv[1:])
