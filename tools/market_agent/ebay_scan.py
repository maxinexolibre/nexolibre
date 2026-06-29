#!/usr/bin/env python3
"""
Agente de oportunidades — Fase 1 (eBay).
Busca partes/bobinas MRI-CT en eBay (Browse API), filtra, descarta lo que ya está
en el catálogo (parts.json) y deja una lista de CANDIDATOS para revisión.

Credenciales (NO van en el código): variables de entorno
  EBAY_CLIENT_ID, EBAY_CLIENT_SECRET   (se guardan como GitHub Secrets)

Salida: tools/market_agent/out/candidates-AAAA-MM-DD.json  + resumen por consola.
Sin dependencias externas (solo stdlib).
"""
import os, json, re, base64, time, datetime, urllib.parse, urllib.request

HERE      = os.path.dirname(os.path.abspath(__file__))
ROOT      = os.path.abspath(os.path.join(HERE, "..", ".."))
CFG       = json.load(open(os.path.join(HERE, "queries.json"), encoding="utf-8"))
OUT_DIR   = os.path.join(HERE, "out")
TOKEN_URL = "https://api.ebay.com/identity/v1/oauth2/token"
SEARCH_URL= "https://api.ebay.com/buy/browse/v1/item_summary/search"

def _req(url, data=None, headers=None, method="GET"):
    r = urllib.request.Request(url, data=data, headers=headers or {}, method=method)
    with urllib.request.urlopen(r, timeout=40) as resp:
        return json.loads(resp.read().decode())

def get_token():
    cid = os.environ.get("EBAY_CLIENT_ID"); sec = os.environ.get("EBAY_CLIENT_SECRET")
    if not cid or not sec:
        raise SystemExit("Faltan EBAY_CLIENT_ID / EBAY_CLIENT_SECRET en el entorno.")
    auth = base64.b64encode(f"{cid}:{sec}".encode()).decode()
    body = urllib.parse.urlencode({
        "grant_type": "client_credentials",
        "scope": "https://api.ebay.com/oauth/api_scope",
    }).encode()
    tok = _req(TOKEN_URL, data=body, method="POST", headers={
        "Authorization": f"Basic {auth}",
        "Content-Type": "application/x-www-form-urlencoded",
    })
    return tok["access_token"]

def search(token, query):
    params = {
        "q": query,
        "limit": str(CFG.get("max_resultados_por_busqueda", 25)),
        "filter": f"conditionIds:{{{ '|'.join(_cond_ids()) }}},price:[{CFG.get('precio_min_usd',0)}..],priceCurrency:USD",
    }
    url = SEARCH_URL + "?" + urllib.parse.urlencode(params)
    headers = {"Authorization": f"Bearer {token}",
               "X-EBAY-C-MARKETPLACE-ID": CFG.get("marketplace", "EBAY_US")}
    try:
        return _req(url, headers=headers).get("itemSummaries", []) or []
    except Exception as e:
        print("  ! error en búsqueda", repr(query), "->", e); return []

_COND_MAP = {"USED": "3000", "SELLER_REFURBISHED": "2500",
             "FOR_PARTS_OR_NOT_WORKING": "7000", "NEW": "1000"}
def _cond_ids():
    return [_COND_MAP[c] for c in CFG.get("condiciones_ebay", ["USED"]) if c in _COND_MAP]

def norm(s):
    return re.sub(r"[^a-z0-9]+", " ", (s or "").lower()).strip()

def existing_signatures():
    """Firmas de lo que ya tenemos en el catálogo, para no duplicar."""
    sigs, parts = set(), []
    try:
        parts = json.load(open(os.path.join(ROOT, "parts.json"), encoding="utf-8"))
    except Exception:
        pass
    for p in parts:
        for k in ("nro_parte", "nombre"):
            v = norm(p.get(k, ""))
            if len(v) >= 5:
                sigs.add(v)
    return sigs

def excluded(title):
    t = (title or "").lower()
    return any(w.lower() in t for w in CFG.get("excluir_si_titulo_contiene", []))

def main():
    os.makedirs(OUT_DIR, exist_ok=True)
    token = get_token()
    queries = list(CFG.get("busquedas_extra", []))
    for m in CFG.get("marcas_modelos", []):
        for t in CFG.get("tipos_pieza", []):
            queries.append(f"{m} {t}")
    print(f"Consultas a correr: {len(queries)}")

    sigs = existing_signatures()
    seen, candidatos = set(), []
    for q in queries:
        for it in search(token, q):
            iid = it.get("itemId")
            title = it.get("title", "")
            if not iid or iid in seen or excluded(title):
                continue
            sig = norm(title)
            if any(s in sig for s in sigs):      # ya lo tenemos / muy parecido
                continue
            seen.add(iid)
            candidatos.append({
                "titulo": title,
                "precio_origen": (it.get("price") or {}).get("value"),
                "moneda": (it.get("price") or {}).get("currency"),
                "condicion": it.get("condition"),
                "ubicacion": (it.get("itemLocation") or {}).get("country"),
                "vendedor": (it.get("seller") or {}).get("username"),
                "imagen": (it.get("image") or {}).get("imageUrl"),
                "fuente": "eBay",
                "link_origen": it.get("itemWebUrl"),
                "ebay_id": iid,
                "encontrado": datetime.date.today().isoformat(),
                "estado": "Pendiente",
            })
        time.sleep(0.3)

    candidatos.sort(key=lambda c: (c.get("titulo") or "").lower())
    fecha = datetime.date.today().isoformat()
    path = os.path.join(OUT_DIR, f"candidates-{fecha}.json")
    json.dump(candidatos, open(path, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
    print(f"\nCandidatos nuevos: {len(candidatos)}  ->  {path}")
    for c in candidatos[:15]:
        print(f"  · {c['titulo'][:70]}  | {c['moneda']} {c['precio_origen']} | {c['ubicacion']}")
    if len(candidatos) > 15:
        print(f"  … y {len(candidatos)-15} más")

if __name__ == "__main__":
    main()
