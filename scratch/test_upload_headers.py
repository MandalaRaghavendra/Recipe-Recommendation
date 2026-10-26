import urllib.request

headers_list = [
    {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'},
    {'User-Agent': 'TastioApp/1.0 (contact@tastio.org)'},
    {'User-Agent': 'Mozilla/5.0', 'Referer': 'https://commons.wikimedia.org/'}
]

url = 'https://upload.wikimedia.org/wikipedia/commons/6/68/Chicken_Sukka.jpg'

for h in headers_list:
    try:
        req = urllib.request.Request(url, headers=h)
        with urllib.request.urlopen(req, timeout=5) as r:
            data = r.read()
            print(f"Success with {h['User-Agent']}: {len(data)} bytes")
            break
    except Exception as e:
        print(f"Failed with {h['User-Agent']}: {e}")
