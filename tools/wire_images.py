#!/usr/bin/env python3
"""
Completa el campo 'imagen' de cada pieza en parts.json a partir de los archivos
que estén en assets/parts/ nombrados con la 'ref' de la pieza.

Reconoce, para una ref como NX-CO-001:
  - NX-CO-001-1.jpg, NX-CO-001-2.jpeg, ...  (ordenadas por el número final)
  - NX-CO-001.jpg                            (una sola foto)
Ignora videos (.mp4, .mov) y cualquier archivo que no sea imagen.
Solo modifica las piezas que TENGAN archivos; el resto queda igual.
Usa el nombre exacto del archivo (respeta mayúsculas y extensión) — importante
porque el hosting (Donweb/Linux) distingue mayúsculas.

Uso:  python3 tools/wire_images.py
"""
import json, os, re, glob

IMG_EXT = (".jpg", ".jpeg", ".png", ".webp", ".gif", ".avif")
PARTS_DIR = "assets/parts"
JSON_FILE = "parts.json"

def order_key(fn):
    m = re.search(r'-(\d+)\.[^.]+$', fn)
    return int(m.group(1)) if m else 0

def main():
    if not os.path.isdir(PARTS_DIR):
        print("No existe la carpeta", PARTS_DIR); return
    data = json.load(open(JSON_FILE, encoding="utf-8"))
    files = [os.path.basename(f) for f in glob.glob(os.path.join(PARTS_DIR, "*"))
             if f.lower().endswith(IMG_EXT)]

    updated = 0
    for p in data:
        ref = (p.get("ref") or "").strip()
        if not ref:
            continue
        rl = ref.lower()
        matches = [f for f in files
                   if os.path.splitext(f)[0].lower() == rl or f.lower().startswith(rl + "-")]
        if not matches:
            continue
        matches = sorted(set(matches), key=order_key)
        nuevo = "; ".join(matches)
        if p.get("imagen", "") != nuevo:
            p["imagen"] = nuevo
            updated += 1
            print(f"  {ref}: {len(matches)} foto(s)")

    json.dump(data, open(JSON_FILE, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
    print(f"\nListo. Piezas actualizadas: {updated}")

    # avisos útiles
    pesadas = [f for f in files if os.path.getsize(os.path.join(PARTS_DIR, f)) > 500*1024]
    if pesadas:
        print(f"Aviso: {len(pesadas)} foto(s) pesan más de 500 KB — conviene optimizarlas (~800–1200 px, <300 KB).")
    refs_l = [(p.get('ref') or '').lower() for p in data if p.get('ref')]
    huerfanas = [f for f in files if not any(
        (os.path.splitext(f)[0].lower() == rl or f.lower().startswith(rl + "-")) for rl in refs_l)]
    if huerfanas:
        print(f"Aviso: {len(huerfanas)} foto(s) sin pieza coincidente (revisá el nombre/ref):")
        for f in huerfanas[:10]:
            print("   -", f)

if __name__ == "__main__":
    main()
