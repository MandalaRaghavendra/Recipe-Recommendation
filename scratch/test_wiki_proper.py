import urllib.request
import urllib.parse
import json
import time

headers = {
    'User-Agent': 'TastioRecipeAppBot/1.0 (https://example.com/bot; bot@example.com)'
}

def search_wikimedia(query):
    url = f"https://commons.wikimedia.org/w/api.php?action=query&format=json&generator=search&gsrnamespace=6&gsrsearch={urllib.parse.quote(query)}&gsrlimit=5&prop=imageinfo&iiprop=url|size|extmetadata"
    req = urllib.request.Request(url, headers=headers)
    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            data = json.loads(resp.read().decode('utf-8'))
            pages = data.get("query", {}).get("pages", {})
            results = []
            for pid, pdata in pages.items():
                title = pdata.get("title", "")
                imginfo = pdata.get("imageinfo", [{}])[0]
                img_url = imginfo.get("url", "")
                results.append((title, img_url))
            return results
    except Exception as e:
        return f"Error: {e}"

test_queries = [
    "Chicken sukka",
    "Chana masala",
    "Fish fry",
    "Prawn fry",
    "Mutton curry"
]

for q in test_queries:
    res = search_wikimedia(q)
    print(f"\nQuery: {q}")
    if isinstance(res, list):
        for title, url in res[:2]:
            print(f"  - {title}: {url}")
    else:
        print(f"  {res}")
    time.sleep(0.5)
