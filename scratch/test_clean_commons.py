import urllib.request
import urllib.parse
import json
import sys

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding='utf-8')

headers = {'User-Agent': 'TastioApp/1.0 (contact@tastio.org)'}

NEGATIVE_WORDS = [
    'tree', 'plant', 'leaf', 'leaves', 'flower', 'branch', 'forest', 'garden',
    'agaric', 'fungi', 'fungus', 'wild', 'toxic', 'raw', 'nature', 'vine',
    'market', 'shop', 'bottle', 'can', 'packet', 'box', 'package', 'street',
    'people', 'portrait', 'man', 'woman', 'flag', 'map', 'diagram', '.pdf'
]

def search_clean_commons(term):
    url = f"https://commons.wikimedia.org/w/api.php?action=query&format=json&generator=search&gsrnamespace=6&gsrsearch={urllib.parse.quote(term)}&gsrlimit=6&prop=imageinfo&iiprop=url|size"
    req = urllib.request.Request(url, headers=headers)
    try:
        with urllib.request.urlopen(req, timeout=8) as r:
            data = json.loads(r.read().decode('utf-8'))
            pages = data.get('query', {}).get('pages', {})
            clean_results = []
            for p in pages.values():
                title = p.get('title', '')
                t_lower = title.lower()
                if any(bad in t_lower for bad in NEGATIVE_WORDS):
                    continue
                info = p.get('imageinfo', [{}])[0]
                url = info.get('url')
                size = info.get('size', 0)
                if url and size > 10000:
                    clean_results.append((title, url, size))
            return clean_results
    except Exception as e:
        return []

candidates = {
    5: ["Egg curry", "Muttai kulambu", "Egg masala"],
    11: ["Vegetable biryani", "Veg biryani handi"],
    15: ["Dal tadka", "Yellow dal tadka"],
    18: ["Mushroom masala", "Mushroom gravy indian"],
    19: ["Tomato rice south indian", "Thakkali sadam"],
    23: ["Curd rice", "Thayir sadam"],
    67: ["Tofu broccoli stir fry", "Tofu stir fry"],
    81: ["Crab masala", "Spicy crab curry"],
    82: ["Egg curry boiled", "Egg pulusu"],
    85: ["Anjal fish fry", "Tawa fish fry"],
    95: ["Fish curry indian", "Fish pulusu"],
    106: ["Spiced buttermilk", "Masala chaas"],
    111: ["Tindora fry", "Kundru sabzi"],
    113: ["Yam curry", "Suran sabzi"],
    122: ["Lauki curry", "Bottle gourd curry"],
    123: ["Murungakkai kulambu", "Drumstick curry"],
    125: ["Capsicum besan", "Shimla mirch besan"],
    128: ["Cucumber raita", "Yellow cucumber curry"],
    129: ["Ridge gourd curry", "Turai sabzi"],
    135: ["Chutney south indian", "Coriander chutney"],
    140: ["Poha indian", "Kanda poha"],
    151: ["Thalipeeth", "Akki rotti"],
    154: ["Tomato rasam", "Charu rasam"],
    155: ["Mutton sukka", "Mutton roast"],
    162: ["Rajma masala", "Rajma curry"],
    164: ["Thepla", "Methi thepla"],
    166: ["Gujarati dal", "Toor dal"],
    171: ["Luchi", "Cholar dal"],
    192: ["Ragi mudde", "Ragi kali"],
    196: ["Ven pongal", "Khara pongal"],
    198: ["Tomato rasam", "Thakkali rasam"]
}

for rid, queries in candidates.items():
    found = False
    for q in queries:
        res = search_clean_commons(q)
        if res:
            title, url, size = res[0]
            print(f"[{rid:3d}] Query '{q}' -> '{title[:45]}' ({size}B)")
            found = True
            break
    if not found:
        print(f"[{rid:3d}] FAILED TO FIND CLEAN FOOD IMAGE")
