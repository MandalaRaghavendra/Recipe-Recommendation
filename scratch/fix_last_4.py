import os
import sys
import re
import json
import hashlib
import urllib.request
import urllib.parse
from PIL import Image
import io
import glob

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding='utf-8')

PROJECT_ROOT = "d:/recipie/Recipe-Recommendation"
STATIC_RECIPES_DIR = os.path.join(PROJECT_ROOT, "web-app", "static", "images", "recipes")
WIKI_HEADERS = {'User-Agent': 'TastioApp/1.0 (contact@tastio.org)'}

all_hashes = set()
for p in glob.glob(os.path.join(STATIC_RECIPES_DIR, "recipe_*.jpg")):
    rid = int(os.path.basename(p).split("_")[1].split(".")[0])
    if rid not in [83, 109, 118, 129]:
        all_hashes.add(hashlib.md5(open(p, "rb").read()).hexdigest())

print(f"Existing hashes to avoid: {len(all_hashes)}")

def search_and_download(queries, rid, dish_name):
    for q in queries:
        url = f"https://commons.wikimedia.org/w/api.php?action=query&format=json&generator=search&gsrnamespace=6&gsrsearch={urllib.parse.quote(q)}&gsrlimit=10&prop=imageinfo&iiprop=url|size"
        req = urllib.request.Request(url, headers=WIKI_HEADERS)
        try:
            with urllib.request.urlopen(req, timeout=8) as resp:
                data = json.loads(resp.read().decode('utf-8'))
                pages = data.get("query", {}).get("pages", {})
                for pid, pdata in pages.items():
                    title = pdata.get("title", "")
                    if any(bad in title.lower() for bad in ['market', 'shop', 'building', 'street', 'people', 'box', 'sign', '.pdf']):
                        continue
                    info = pdata.get("imageinfo", [{}])[0]
                    img_url = info.get("url")
                    if not img_url:
                        continue
                    try:
                        img_req = urllib.request.Request(img_url, headers=WIKI_HEADERS)
                        with urllib.request.urlopen(img_req, timeout=10) as img_resp:
                            raw = img_resp.read()
                            if len(raw) < 5000:
                                continue
                            h = hashlib.md5(raw).hexdigest()
                            if h in all_hashes:
                                continue
                            img = Image.open(io.BytesIO(raw))
                            img = img.convert('RGB')
                            w, h_px = img.size
                            if w < 180 or h_px < 180:
                                continue
                            if w > 800:
                                new_w = 800
                                new_h = int(h_px * (800 / w))
                                img = img.resize((new_w, new_h), Image.Resampling.LANCZOS)
                            target_path = os.path.join(STATIC_RECIPES_DIR, f"recipe_{rid}.jpg")
                            img.save(target_path, "JPEG", quality=85, optimize=True)
                            new_h = hashlib.md5(open(target_path, "rb").read()).hexdigest()
                            all_hashes.add(new_h)
                            print(f"Recipe {rid:3d} ({dish_name}) -> '{title}' (Hash: {new_h[:8]})")
                            return True
                    except Exception:
                        continue
        except Exception:
            pass
            
        # Try openverse as fallback
        url = f"https://api.openverse.org/v1/images/?q={urllib.parse.quote(q)}&page_size=8"
        req = urllib.request.Request(url, headers={'User-Agent': 'TastioApp/1.0 (contact@tastio.org)'})
        try:
            with urllib.request.urlopen(req, timeout=8) as resp:
                data = json.loads(resp.read().decode('utf-8'))
                for r in data.get("results", []):
                    title = r.get("title") or ""
                    if any(bad in title.lower() for bad in ['market', 'shop', 'building', 'street', 'people', 'box', 'sign', '.pdf']):
                        continue
                    img_url = r.get("url")
                    if not img_url:
                        continue
                    try:
                        img_req = urllib.request.Request(img_url, headers={'User-Agent': 'Mozilla/5.0'})
                        with urllib.request.urlopen(img_req, timeout=8) as img_resp:
                            raw = img_resp.read()
                            if len(raw) < 5000:
                                continue
                            h = hashlib.md5(raw).hexdigest()
                            if h in all_hashes:
                                continue
                            img = Image.open(io.BytesIO(raw))
                            img = img.convert('RGB')
                            w, h_px = img.size
                            if w < 180 or h_px < 180:
                                continue
                            if w > 800:
                                new_w = 800
                                new_h = int(h_px * (800 / w))
                                img = img.resize((new_w, new_h), Image.Resampling.LANCZOS)
                            target_path = os.path.join(STATIC_RECIPES_DIR, f"recipe_{rid}.jpg")
                            img.save(target_path, "JPEG", quality=85, optimize=True)
                            new_h = hashlib.md5(open(target_path, "rb").read()).hexdigest()
                            all_hashes.add(new_h)
                            print(f"Recipe {rid:3d} ({dish_name}) [Openverse] -> '{title}' (Hash: {new_h[:8]})")
                            return True
                    except Exception:
                        continue
        except Exception:
            pass
    print(f"FAILED for Recipe {rid} ({dish_name})")
    return False

# 83: Boti Kura
search_and_download(["Mutton curry indian", "Lamb curry", "Bhuna gosht", "Mutton masala"], 83, "Boti Kura")
# 109: Anapakaya Pulusu
search_and_download(["Lauki sabzi", "Doodhi curry", "Bottle gourd curry indian"], 109, "Anapakaya Pulusu")
# 118: Potlakaya Fry
search_and_download(["Padavalanga thoran", "Snake gourd recipe", "Snake gourd fry"], 118, "Potlakaya Fry")
# 129: Beerakaya Pachadi
search_and_download(["Green chutney indian", "Coriander mint chutney", "Pachadi south indian", "Chutney bowl"], 129, "Beerakaya Pachadi")
