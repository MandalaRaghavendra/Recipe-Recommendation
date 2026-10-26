import urllib.request
import urllib.parse
import json
import sys

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding='utf-8')

headers = {'User-Agent': 'TastioApp/1.0 (contact@tastio.org)'}

def search(q):
    url = f"https://commons.wikimedia.org/w/api.php?action=query&format=json&generator=search&gsrnamespace=6&gsrsearch={urllib.parse.quote(q)}&gsrlimit=5&prop=imageinfo&iiprop=url|size"
    req = urllib.request.Request(url, headers=headers)
    try:
        data = json.loads(urllib.request.urlopen(req, timeout=8).read().decode('utf-8'))
        pages = data.get('query', {}).get('pages', {})
        for p in pages.values():
            t = p.get('title', '')
            if not any(bad in t.lower() for bad in ['festival', 'singer', 'concert', 'rangoli', 'pot.', 'pot_', '.png', '.pdf']):
                info = p.get('imageinfo', [{}])[0]
                print(f"{q} -> {t} ({info.get('size')}B)")
    except Exception as e:
        print(f"Error for {q}: {e}")

search("Ven pongal dish")
search("Pongal sambar")
search("Gongura dal")
search("Andhra dal")
search("Yellow dal tadka")
