import os
import sys
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

# Target replacements for recipes that received plants, raw veggies, or wrong dishes
EXACT_TARGETS = {
    5: ("Egg Curry 2022.jpg", "Andhra Special Egg Curry"),
    11: ("Mixed vegetable biryani (top).JPG", "Andhra Special Veg Biryani"),
    15: ("Dal Tadka-Delhi.jpg", "Andhra Special Dal Tadka"),
    18: ("Mushroom Butter Masala (15914329462).jpg", "Andhra Style Mushroom Curry"),
    23: ("Curd Rice.jpg", "Andhra Special Curd Rice"),
    81: ("Butter naan,steam rice, spicy crab masal", "Peethala Vepudu (Crab Fry)"),
    82: ("Boiled Egg Curry.jpg", "Guddu Pulusu"),
    85: ("Anjal Fish Fry.jpg", "Nellore Chepala Vepudu (Fish Fry)"),
    95: ("Alappy Fish Curry.JPG", "Bommidala Pulusu (Fish Curry)"),
    106: ("Neer moru spiced buttermilk.jpg", "Menthi Majjiga (Spiced Buttermilk)"),
    113: ("Cooking of Yam curry.jpg", "Kanda Bachali Kura (Yam Curry)"),
    122: ("Lauki Kofta.JPG", "Sorakaya Palu Kura (Bottle Gourd Dish)"),
    123: ("Indian Bengali rice dish, with drumsticks curry and onion vada.jpg", "Munakkaya Kaju Kura (Drumstick Curry)"),
    125: ("Capsicum Aloo Tomato sabzi.jpg", "Capsicum Senagapindi Kura"),
    128: ("Cucumber-raita.jpg", "Dosakaya Pachadi (Cucumber Pachadi)"),
    140: ("Indian breakfast- Poha.jpg", "Atukula Upma (Andhra Poha)"),
    151: ("Bhajani Thalipeeth.jpg", "Telangana Sarva Pindi"),
    164: ("Local food thepla at Jamnagar railway st", "Gujarati Methi Thepla"),
    171: ("Alur dom & luchi.jpg", "Bengali Chholar Dal with Luchi"),
    196: ("Ven Pongal & sakkarai pongal with vada & bonda.jpg", "Ven Pongal & Coconut Chutney")
}

# Collect existing hashes to avoid
all_hashes = set()
for p in glob.glob(os.path.join(STATIC_RECIPES_DIR, "recipe_*.jpg")):
    rid = int(os.path.basename(p).split("_")[1].split(".")[0])
    if rid not in EXACT_TARGETS:
        all_hashes.add(hashlib.md5(open(p, "rb").read()).hexdigest())

print(f"Loaded {len(all_hashes)} existing hashes to preserve.")

def fetch_wiki_file_by_name(filename_fragment):
    url = f"https://commons.wikimedia.org/w/api.php?action=query&format=json&generator=search&gsrnamespace=6&gsrsearch={urllib.parse.quote(filename_fragment)}&gsrlimit=3&prop=imageinfo&iiprop=url|size"
    req = urllib.request.Request(url, headers=WIKI_HEADERS)
    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            data = json.loads(resp.read().decode('utf-8'))
            pages = data.get("query", {}).get("pages", {})
            for pid, pdata in pages.items():
                title = pdata.get("title", "")
                info = pdata.get("imageinfo", [{}])[0]
                img_url = info.get("url")
                size = info.get("size", 0)
                if img_url and size > 8000:
                    try:
                        img_req = urllib.request.Request(img_url, headers=WIKI_HEADERS)
                        with urllib.request.urlopen(img_req, timeout=10) as img_resp:
                            raw = img_resp.read()
                            img = Image.open(io.BytesIO(raw))
                            img = img.convert('RGB')
                            w, h_px = img.size
                            if w > 800:
                                new_w = 800
                                new_h = int(h_px * (800 / w))
                                img = img.resize((new_w, new_h), Image.Resampling.LANCZOS)
                            return img, title
                    except Exception as e:
                        print(f"  Error downloading {title}: {e}")
    except Exception as e:
        print(f"  Error searching for {filename_fragment}: {e}")
    return None, None

success_count = 0
for rid, (frag, dish_name) in EXACT_TARGETS.items():
    print(f"\nProcessing Recipe {rid:3d} ({dish_name}). Searching '{frag}'...")
    img, title = fetch_wiki_file_by_name(frag)
    if img:
        target_path = os.path.join(STATIC_RECIPES_DIR, f"recipe_{rid}.jpg")
        img.save(target_path, "JPEG", quality=85, optimize=True)
        h = hashlib.md5(open(target_path, "rb").read()).hexdigest()
        all_hashes.add(h)
        success_count += 1
        print(f"SUCCESS: Recipe {rid:3d} ({dish_name}) -> '{title}' (Hash: {h[:8]})")
    else:
        print(f"FAILED: Recipe {rid:3d} ({dish_name}) could not be downloaded")

print("\n" + "="*50)
print(f"Completed: {success_count}/{len(EXACT_TARGETS)} exact accurate food images updated!")
