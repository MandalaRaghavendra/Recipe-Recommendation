import urllib.request
import urllib.parse
import json

WIKI_HEADERS = {'User-Agent': 'TastioApp/1.0 (contact@tastio.org)'}

queries = {
    21: "Tamarind rice pulihora",
    22: "Coconut rice south indian",
    29: "Andhra chicken curry",
    53: "Grilled chicken breast lemon herb",
    91: "Gongura chicken andhra",
    111: "Tindora fry kundru",
    116: "Bitter gourd fry karela",
    118: "Snake gourd stir fry",
    126: "Gongura pachadi chutney",
    142: "Rava upma south indian",
    146: "Kaja sweet andhra",
    148: "Rava kesari halwa",
    156: "Murukku chakli south indian",
    161: "Sarson ka saag makki roti",
    180: "Sabudana khichdi maharashtrian",
    186: "Karimeen pollichathu fish",
    197: "Kothu parotta chicken"
}

def search_wiki(q):
    url = f"https://commons.wikimedia.org/w/api.php?action=query&format=json&generator=search&gsrnamespace=6&gsrsearch={urllib.parse.quote(q)}&gsrlimit=3&prop=imageinfo&iiprop=url|size"
    req = urllib.request.Request(url, headers=WIKI_HEADERS)
    try:
        with urllib.request.urlopen(req, timeout=8) as resp:
            data = json.loads(resp.read().decode('utf-8'))
            pages = data.get("query", {}).get("pages", {})
            res = []
            for pid, pdata in pages.items():
                title = pdata.get("title", "")
                info = pdata.get("imageinfo", [{}])[0]
                url = info.get("url")
                if url:
                    res.append((title, url))
            return res
    except Exception as e:
        return [("error", str(e))]

for rid, q in queries.items():
    results = search_wiki(q)
    print(f"Recipe {rid}: '{q}'")
    for t, u in results:
        print(f"   -> {t}")
