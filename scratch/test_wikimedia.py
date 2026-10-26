import os
import re
import json
import urllib.request
import urllib.parse

with open(r"d:\recipie\Recipe-Recommendation\ai-service\data.json", "r", encoding="utf-8") as f:
    recipes = json.load(f)

def search_wikimedia(query):
    params = {
        'action': 'query',
        'format': 'json',
        'prop': 'imageinfo',
        'generator': 'search',
        'gsrnamespace': 6,
        'gsrsearch': f"{query} filetype:bitmap",
        'gsrlimit': 3,
        'iiprop': 'url',
        'iiurlwidth': 800
    }
    url = 'https://commons.wikimedia.org/w/api.php?' + urllib.parse.urlencode(params)
    req = urllib.request.Request(url, headers={'User-Agent': 'TastioApp/1.0 (contact@tastio.ai)'})
    try:
        with urllib.request.urlopen(req, timeout=5) as resp:
            data = json.loads(resp.read().decode('utf-8'))
            pages = data.get('query', {}).get('pages', {})
            results = []
            for p in pages.values():
                title = p.get('title', '')
                info = p.get('imageinfo', [{}])[0]
                img_url = info.get('thumburl') or info.get('url')
                if img_url:
                    results.append((title, img_url))
            return results
    except Exception as e:
        return [("error", str(e))]

# Check some recipe searches
for r in recipes[10:25]:
    name = r["recipe_name"]
    clean = re.sub(r'\(.*?\)', '', name).strip()
    res = search_wikimedia(f"{clean} food")
    print(f"Recipe {r['recipe_id']}: '{name}'")
    for title, url in res:
        print(f"   -> {title}")
