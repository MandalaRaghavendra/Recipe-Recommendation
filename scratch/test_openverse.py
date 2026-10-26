import urllib.request
import urllib.parse
import json
import hashlib
from PIL import Image
import io

def get_openverse_food_image(query, seen_hashes):
    url = f"https://api.openverse.org/v1/images/?q={urllib.parse.quote(query)}&page_size=10"
    req = urllib.request.Request(url, headers={'User-Agent': 'TastioRecipeApp/1.0 (contact@tastio.ai)'})
    try:
        with urllib.request.urlopen(req, timeout=8) as resp:
            data = json.loads(resp.read().decode('utf-8'))
            results = data.get("results", [])
            for r in results:
                title = (r.get("title") or "").lower()
                # Skip non-food or undesirable images
                if any(bad in title for bad in ['market', 'shop', 'street', 'crowd', 'sign', 'board', 'building', 'store', 'people', 'box']):
                    continue
                img_url = r.get("url")
                if not img_url:
                    continue
                # Try downloading image
                try:
                    img_req = urllib.request.Request(img_url, headers={'User-Agent': 'TastioRecipeApp/1.0'})
                    with urllib.request.urlopen(img_req, timeout=8) as img_resp:
                        raw = img_resp.read()
                        if len(raw) < 5000:
                            continue
                        h = hashlib.md5(raw).hexdigest()
                        if h in seen_hashes:
                            continue
                        img = Image.open(io.BytesIO(raw))
                        img.verify()
                        return img_url, raw, h, r.get("title")
                except Exception:
                    continue
    except Exception as e:
        print(f"Error querying Openverse for '{query}': {e}")
    return None, None, None, None

seen = set()
test_items = [
    (89, "Natu Kodi Fry", "country chicken fry indian"),
    (78, "Kodi Vepudu", "andhra pepper chicken fry"),
    (16, "Chana Masala", "chana masala chickpea curry"),
    (86, "Royyala Vepudu", "crispy prawn fry indian"),
    (80, "Gongura Royyalu", "prawns curry indian"),
    (85, "Nellore Chepala Vepudu", "spicy fish fry indian")
]

for rid, name, q in test_items:
    url, raw, h, title = get_openverse_food_image(q, seen)
    if url:
        seen.add(h)
        print(f"Recipe {rid} ({name}) -> Matched: '{title}' ({len(raw)} bytes, Hash: {h[:8]})")
    else:
        print(f"Recipe {rid} ({name}) -> No unique image found")
