import urllib.request
import urllib.parse
import json

headers = {'User-Agent': 'TastioApp/1.0 (contact@tastio.org)'}

queries_32 = {
    107: ["Tamarind rasam", "Rasam soup"],
    108: ["Bitter gourd curry", "Karela sabzi", "Pavakkai"],
    109: ["Bottle gourd curry", "Lauki sabzi"],
    111: ["Tindora", "Kundru", "Ivy gourd"],
    112: ["Arbi fry", "Colocasia", "Seppankizhangu"],
    113: ["Yam curry", "Suran sabzi"],
    117: ["Ridge gourd", "Turai sabzi"],
    118: ["Snake gourd", "Padavalanga"],
    123: ["Drumstick curry", "Murungakkai"],
    124: ["Brinjal curry", "Baingan fry"],
    125: ["Capsicum curry", "Shimla mirch"],
    127: ["Tomato chutney", "Tomato relish"],
    129: ["Ridge gourd chutney", "Chutney indian"],
    130: ["Eggplant chutney", "Baingan bharta"],
    138: ["Medu vada", "Vada indian"],
    140: ["Poha indian", "Kanda poha"],
    142: ["Upma breakfast", "Semolina upma"],
    154: ["Pulusu", "Rasam bowl"],
    155: ["Mutton sukka", "Mutton fry indian"],
    158: ["Dal makhani"],
    152: ["Bagara rice"],
    162: ["Rajma", "Rajma masala"],
    164: ["Thepla", "Methi thepla"],
    165: ["Undhiyu"],
    166: ["Gujarati dal", "Toor dal"],
    171: ["Luchi", "Chana dal"],
    183: ["Thalassery biryani", "Malabar biryani"],
    185: ["Avial"],
    189: ["Chicken ghee roast"],
    192: ["Ragi mudde"],
    194: ["Idli sambar"],
    196: ["Ven pongal", "Pongal"],
    198: ["Tomato rasam"]
}

for rid, qlist in queries_32.items():
    found = False
    for q in qlist:
        url = f"https://commons.wikimedia.org/w/api.php?action=query&format=json&generator=search&gsrnamespace=6&gsrsearch={urllib.parse.quote(q)}&gsrlimit=2&prop=imageinfo&iiprop=url"
        try:
            req = urllib.request.Request(url, headers=headers)
            with urllib.request.urlopen(req, timeout=5) as r:
                data = json.loads(r.read().decode('utf-8'))
                pages = data.get('query', {}).get('pages', {})
                for pid, p in pages.items():
                    title = p.get('title', '')
                    print(f"[{rid}] Query '{q}' -> {title}")
                    found = True
                    break
        except Exception:
            pass
        if found:
            break
    if not found:
        print(f"[{rid}] NOT FOUND in commons")
