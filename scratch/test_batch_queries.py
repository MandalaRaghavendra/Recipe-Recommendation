import urllib.request
import urllib.parse
import json

headers = {'User-Agent': 'TastioApp/1.0 (contact@tastio.org)'}

def search_commons(query):
    url = f"https://commons.wikimedia.org/w/api.php?action=query&format=json&generator=search&gsrnamespace=6&gsrsearch={urllib.parse.quote(query)}&gsrlimit=3&prop=imageinfo&iiprop=url"
    req = urllib.request.Request(url, headers=headers)
    try:
        with urllib.request.urlopen(req, timeout=8) as r:
            data = json.loads(r.read().decode('utf-8'))
            pages = data.get('query', {}).get('pages', {})
            res = []
            for pid, p in pages.items():
                title = p.get('title', '')
                info = p.get('imageinfo', [{}])[0]
                res.append((title, info.get('url', '')))
            return res
    except Exception as e:
        return []

tests = [
    "Dal Makhani",
    "Undhiyu",
    "Methi Thepla",
    "Ragi Mudde",
    "Avial",
    "Chicken Ghee Roast",
    "Chholar Dal Luchi",
    "Thalassery Biryani",
    "Idli Sambar",
    "Ven Pongal"
]

for t in tests:
    res = search_commons(t)
    print(f"\n{t}:")
    for title, url in res[:1]:
        print(f"  {title}")
