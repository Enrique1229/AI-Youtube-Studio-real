#!/usr/bin/env python3
"""brand_text.py "<Nombre del canal>" — pone el nombre en el banner (channel/brand/banner_raw.png -> banner.png),
dentro de la zona segura de YouTube (1546x423 centrada) y deja una vista previa de la zona segura."""
import pathlib, sys
from PIL import Image, ImageDraw, ImageFilter, ImageFont
ROOT = pathlib.Path(__file__).resolve().parent.parent; B = ROOT / "channel" / "brand"
name = sys.argv[1] if len(sys.argv) > 1 else "The Wit Ladder"
FONTS = [ROOT / "models/fonts/InterDisplay-Bold.ttf", pathlib.Path("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"), pathlib.Path("C:/Windows/Fonts/arialbd.ttf")]
font_path = next(str(f) for f in FONTS if f.exists())
im = Image.open(B / "banner_raw.png").convert("RGB"); W, H = im.size
sx0, sy0, sw, sh = (W - 1546) // 2, (H - 423) // 2, 1546, 423
size = 150
while True:
    f = ImageFont.truetype(font_path, size); tw = f.getlength(name)
    if tw < sw * 0.52 or size < 60: break
    size -= 6
tx = sx0 + sw - tw - 40; ty = sy0 + (sh - size) // 2 - 10                        # a la derecha del personaje
shadow = Image.new("RGBA", im.size, (0, 0, 0, 0)); d = ImageDraw.Draw(shadow)
d.rounded_rectangle((tx - 40, ty - 30, tx + tw + 40, ty + size + 50), 40, fill=(15, 20, 25, 150))
im = Image.alpha_composite(im.convert("RGBA"), shadow.filter(ImageFilter.GaussianBlur(6)))
d = ImageDraw.Draw(im)
d.text((tx, ty), name, font=f, fill=(255, 224, 130), stroke_width=8, stroke_fill=(20, 20, 20))
sub = ImageFont.truetype(font_path, int(size * 0.32))
d.text((tx + 4, ty + size + 4), "every IQ level, one problem", font=sub, fill=(255, 255, 255), stroke_width=4, stroke_fill=(20, 20, 20))
im.convert("RGB").save(B / "banner.png")
pv = im.convert("RGB").copy(); ImageDraw.Draw(pv).rectangle((sx0, sy0, sx0 + sw, sy0 + sh), outline=(255, 0, 0), width=6)
pv.resize((W // 2, H // 2)).save(B / "banner_safe_zone_preview.jpg", quality=85)
print("OK", B / "banner.png")
