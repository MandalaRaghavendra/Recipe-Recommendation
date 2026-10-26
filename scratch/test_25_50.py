import urllib.request
import urllib.parse
import json
import sys

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding='utf-8')

headers = {'User-Agent': 'TastioApp/1.0 (contact@tastio.org)'}

queries = {
    25: ["Ven Pongal", "Khara Pongal", "Pongal dish"],
    26: ["Dal fry", "Tarka dal", "Yellow dal bowl", "Toor dal"],
    27: ["Pesarattu", "Moong dal dosa", "Green gram dosa"],
    28: ["Bharli Vangi", "Stuffed brinjal curry"],
    29: ["Andhra chicken curry", "Chicken curry indian"],
    30: ["Uttapam", "Thick dosa", "Minapa rotti"],
    31: ["Pulihora", "Tamarind rice south indian"],
    32: ["Tomato dal", "Tomato pappu"],
    33: ["Aloo fry", "Potato fry indian"],
    34: ["Coconut chutney", "Kobbari pachadi"],
    35: ["Lemon rice", "Chitranna"],
    36: ["Punugulu", "Mysore bonda"],
    37: ["Mango dal", "Kacha aam dal"],
    38: ["Mirchi bajji", "Mirapakaya bajji"],
    39: ["Sunnundalu", "Laddu indian sweet", "Urad dal laddu"],
    40: ["Hyderabadi chicken biryani", "Andhra chicken biryani"],
    42: ["Bhindi fry", "Bendakaya fry", "Okra stir fry"],
    43: ["Rasam bowl", "South indian rasam"],
    44: ["Puran poli", "Bobbatlu sweet"],
    45: ["Chicken liver fry", "Liver fry indian"],
    46: ["Masala vada", "Paruppu vadai"],
    47: ["Raw banana fry", "Plantain fry", "Vazhakkai fry"],
    48: ["Kollu rasam", "Ulavacharu soup"],
    49: ["Chicken vepudu", "Kodi vepudu"],
    50: ["Semiya payasam", "Vermicelli kheer", "Seviyan kheer"]
}

for rid, qlist in queries.items():
    found = False
    for q in qlist:
        url = f"https://commons.wikimedia.org/w/api.php?action=query&format=json&generator=search&gsrnamespace=6&gsrsearch={urllib.parse.quote(q)}&gsrlimit=3&prop=imageinfo&iiprop=url|size"
        try:
            req = urllib.request.Request(url, headers=headers)
            with urllib.request.urlopen(req, timeout=5) as r:
                data = json.loads(r.read().decode('utf-8'))
                pages = data.get('query', {}).get('pages', {})
                for p in pages.values():
                    t = p.get('title', '')
                    if any(bad in t.lower() for bad in ['market', 'shop', 'building', 'street', 'rangoli', 'concert', 'singer', 'stage', 'leaf', 'tree', '.pdf']):
                        continue
                    print(f"[{rid:2d}] Query '{q}' -> {t}")
                    found = True
                    break
        except Exception:
            pass
        if found:
            break
    if not found:
        print(f"[{rid:2d}] NOT FOUND")
