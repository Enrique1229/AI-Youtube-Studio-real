#!/usr/bin/env python3
"""thumbnail.py <story-id>  —  final/thumbnail.json -> final/thumbnail.jpg

Imagen base: assets/images/thumbnail.png (gen_images.py --thumbnail) o, si no existe, el primer plano.
Superpone el texto del concepto elegido con Pillow. 1280x720 (long) o 1080x1920 (short).
"""
import sys
from PIL import Image, ImageDraw, ImageFont, ImageOps
from common import story, state, load, die, font_file


def main(sid):
    d = story(sid)
    th = load(d / "final" / "thumbnail.json", "lo escribe thumbnail-designer")
    c = th["concepts"][th.get("chosen", 0)]
    size = (1080, 1920) if state(sid)["format"] == "short" else (1280, 720)
    imgs = d / "assets" / "images"
    base = imgs / "thumbnail.png"
    if not base.exists():
        cands = sorted(p for p in imgs.glob("*.png"))
        if not cands:
            die("no hay imagen base para el thumbnail")
        base = cands[0]
    im = ImageOps.fit(Image.open(base).convert("RGB"), size)
    text = (c.get("text") or "").upper()
    if text:
        fp = font_file(bold=True)
        fs = size[1] // 6 if size[0] > size[1] else size[0] // 7
        draw = ImageDraw.Draw(im)
        while fs > 20:
            font = ImageFont.truetype(fp, fs)
            if draw.textlength(text, font=font) <= size[0] * 0.9:
                break
            fs -= 6
        x = (size[0] - draw.textlength(text, font=font)) / 2
        y = size[1] * (0.74 if size[0] > size[1] else 0.12)
        draw.text((x, y), text, font=font, fill=(255, 235, 59), stroke_width=max(fs // 10, 4), stroke_fill=(0, 0, 0))
    out = d / "final" / "thumbnail.jpg"
    im.save(out, quality=92)
    print(out.name, size, repr(text))


if __name__ == "__main__":
    main(*sys.argv[1:])
