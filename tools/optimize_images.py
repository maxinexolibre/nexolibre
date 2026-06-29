#!/usr/bin/env python3
"""
Redimensiona y comprime las fotos de assets/parts/ para que carguen rápido.
- Máximo 1400 px del lado mayor (no agranda si ya es menor).
- JPEG calidad 82, progresivo, sin metadatos EXIF (respeta la orientación).
Sobrescribe el archivo manteniendo el nombre. Solo toca imágenes (.jpg/.jpeg/.png/.webp).
Uso:  python3 tools/optimize_images.py
"""
import os, glob
from PIL import Image, ImageOps

DIR   = "assets/parts"
MAXPX = 1400
Q     = 82
EXT   = (".jpg", ".jpeg", ".png", ".webp")

def optimize(path):
    try:
        before = os.path.getsize(path)
        im = Image.open(path)
        im = ImageOps.exif_transpose(im)          # respeta la orientación de la foto
        if im.mode in ("RGBA", "P", "LA"):
            im = im.convert("RGB")
        im.thumbnail((MAXPX, MAXPX))               # solo achica, nunca agranda
        im.save(path, "JPEG", quality=Q, optimize=True, progressive=True)
        return before, os.path.getsize(path)
    except Exception as e:
        print("  error en", os.path.basename(path), "->", e)
        return None

def main():
    if not os.path.isdir(DIR):
        print("No existe", DIR); return
    files = [f for f in glob.glob(os.path.join(DIR, "*")) if f.lower().endswith(EXT)]
    tb = ta = n = 0
    for f in sorted(files):
        r = optimize(f)
        if r:
            b, a = r; tb += b; ta += a; n += 1
            print(f"  {os.path.basename(f)}: {b//1024} KB -> {a//1024} KB")
    if n:
        ahorro = 100 - (ta * 100 // max(tb, 1))
        print(f"\n{n} fotos optimizadas · {tb//1024} KB -> {ta//1024} KB ({ahorro}% menos)")
    else:
        print("No hay imágenes para optimizar.")

if __name__ == "__main__":
    main()
