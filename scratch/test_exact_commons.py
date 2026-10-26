import urllib.request
import urllib.parse
import json

headers = {'User-Agent': 'TastioApp/1.0 (contact@tastio.org)'}

def search_files(term):
    url = f"https://commons.wikimedia.org/w/api.php?action=query&format=json&generator=search&gsrnamespace=6&gsrsearch={urllib.parse.quote(term)}&gsrlimit=3&prop=imageinfo&iiprop=url"
    req = urllib.request.Request(url, headers=headers)
    try:
        with urllib.request.urlopen(req, timeout=5) as r:
            data = json.loads(r.read().decode('utf-8'))
            pages = data.get('query', {}).get('pages', {})
            return [p.get('title') for p in pages.values()]
    except Exception as e:
        return []

tests = {
    5: "Egg curry",
    15: "Dal tadka",
    18: "Mushroom curry",
    19: "Tomato rice",
    23: "Curd rice",
    67: "Tofu broccoli",
    81: "Crab fry",
    82: "Boiled egg curry",
    85: "Anjal fish fry",
    95: "Fish pulusu",
    106: "Spiced buttermilk",
    111: "Kundru fry",
    113: "Suran curry",
    122: "Lauki curry",
    123: "Drumstick curry",
    125: "Capsicum besan",
    128: "Cucumber chutney",
    135: "Curry leaves chutney",
    140: "Poha",
    151: "Thalipeeth",
    154: "Rasam",
    155: "Mutton sukka",
    162: "Rajma masala",
    164: "Thepla",
    166: "Gujarati dal",
    171: "Cholar dal",
    192: "Ragi mudde",
    196: "Ven pongal",
    198: "Tomato rasam"
}

for rid, term in tests.items():
    res = search_files(term)
    print(f"[{rid:3d}] '{term}' -> {res[:2]}")
