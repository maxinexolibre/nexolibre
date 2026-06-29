#!/usr/bin/env python3
"""
Genera la imagen para compartir (assets/og-image.png, 1200x630) y el logo para
datos estructurados (assets/nexolibre-logo.png, 512x512), con la marca Nexolibre.
Usa el SVG de la marca si se puede rasterizar; si no, dibuja un chevron aproximado.
Uso:  python3 tools/make_og_image.py
"""
import os
from PIL import Image, ImageDraw, ImageFont

ORANGE = (241, 144, 0)
GRAY   = (98, 93, 87)
BG     = (250, 247, 242)
WHITE  = (255, 255, 255)
ARIAL_B = "/System/Library/Fonts/Supplemental/Arial Bold.ttf"
ARIAL   = "/System/Library/Fonts/Supplemental/Arial.ttf"

def font(path, size):
    return ImageFont.truetype(path, size)

def mark_png(h):
    """Devuelve la marca (swoosh naranja) como imagen RGBA de alto h, o None."""
    try:
        import cairosvg, io
        png = cairosvg.svg2png(url="assets/nexolibre-mark.svg", output_height=h)
        return Image.open(io.BytesIO(png)).convert("RGBA")
    except Exception:
        # fallback: chevron/flecha estilizada
        w = int(h * 2.3)
        im = Image.new("RGBA", (w, h), (0, 0, 0, 0))
        d = ImageDraw.Draw(im)
        d.polygon([(0, h*0.62), (w*0.62, 0), (w, h*0.16), (w*0.30, h),
                   (w*0.30, h*0.55)], fill=ORANGE)
        return im

def center_text(d, cx, y, text, fnt, fill):
    b = d.textbbox((0, 0), text, font=fnt)
    d.text((cx - (b[2]-b[0])/2, y), text, font=fnt, fill=fill)

def make_og():
    W, H = 1200, 630
    im = Image.new("RGB", (W, H), BG)
    d = ImageDraw.Draw(im)
    # banda naranja inferior
    d.rectangle([0, H-14, W, H], fill=ORANGE)
    # marca
    mk = mark_png(150)
    im.paste(mk, (int(W/2 - mk.width/2), 120), mk)
    # wordmark + tagline
    center_text(d, W/2, 300, "nexolibre", font(ARIAL_B, 120), ORANGE)
    center_text(d, W/2, 440, "Ingeniería médica multimarca · MRI / CT", font(ARIAL, 40), GRAY)
    center_text(d, W/2, 500, "Soporte · Repuestos recuperados · Software con IA", font(ARIAL, 34), GRAY)
    center_text(d, W/2, 558, "parte de Grupo Nexo", font(ARIAL, 26), (150, 145, 138))
    im.save("assets/og-image.png", "PNG", optimize=True)
    print("  assets/og-image.png", os.path.getsize("assets/og-image.png")//1024, "KB")

def make_logo():
    S = 512
    im = Image.new("RGB", (S, S), WHITE)
    d = ImageDraw.Draw(im)
    mk = mark_png(150)
    im.paste(mk, (int(S/2 - mk.width/2), 150), mk)
    center_text(d, S/2, 320, "nexolibre", font(ARIAL_B, 64), ORANGE)
    im.save("assets/nexolibre-logo.png", "PNG", optimize=True)
    print("  assets/nexolibre-logo.png", os.path.getsize("assets/nexolibre-logo.png")//1024, "KB")

if __name__ == "__main__":
    make_og()
    make_logo()
    print("Listo.")
