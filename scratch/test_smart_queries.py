import urllib.request
import urllib.parse
import json

recipes_to_test = [
    (16, 'Chana Masala', ['chana masala', 'chole masala']),
    (78, 'Pepper Chicken', ['pepper chicken indian', 'chicken sukka']),
    (89, 'Natu Kodi Fry', ['chicken fry indian', 'kodi vepudu']),
    (86, 'Prawn Fry', ['prawn fry indian', 'fried prawns']),
    (80, 'Prawn Curry', ['prawn curry indian', 'shrimp curry indian']),
    (9, 'Crab Curry', ['crab curry indian', 'crab masala']),
    (14, 'Baingan Bharta', ['baingan bharta', 'roasted eggplant curry']),
    (19, 'Tomato Rice', ['tomato rice indian', 'thakkali sadam']),
    (21, 'Tamarind Rice', ['tamarind rice', 'pulihora']),
    (23, 'Curd Rice', ['curd rice', 'thayir sadam'])
]

for rid, name, queries in recipes_to_test:
    matched = False
    for q in queries:
        url = 'https://api.openverse.org/v1/images/?q=' + urllib.parse.quote(q) + '&page_size=5'
        req = urllib.request.Request(url, headers={'User-Agent': 'TastioApp/1.0'})
        try:
            with urllib.request.urlopen(req, timeout=5) as resp:
                data = json.loads(resp.read().decode('utf-8'))
                for r in data.get('results', []):
                    title = (r.get('title') or '').lower()
                    if any(bad in title for bad in ['market', 'shop', 'street', 'crowd', 'store', 'sign', 'building']):
                        continue
                    print(f"{rid} ({name}) -> Matched on '{q}': {r.get('title')} | {r.get('url')[:65]}...")
                    matched = True
                    break
        except Exception as e:
            pass
        if matched:
            break
