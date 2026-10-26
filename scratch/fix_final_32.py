import os
import sys
import re
import json
import hashlib
import time
import urllib.request
import urllib.parse
from PIL import Image
import io
import glob

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding='utf-8')

PROJECT_ROOT = "d:/recipie/Recipe-Recommendation"
DATA_PATH = os.path.join(PROJECT_ROOT, "ai-service", "data.json")
STATIC_RECIPES_DIR = os.path.join(PROJECT_ROOT, "web-app", "static", "images", "recipes")

WIKI_HEADERS = {'User-Agent': 'TastioApp/1.0 (contact@tastio.org)'}
OPENVERSE_HEADERS = {'User-Agent': 'TastioApp/1.0 (contact@tastio.org)'}

NEGATIVE_KEYWORDS = [
    'market', 'building', 'shop', 'store', 'street', 'people', 'portrait', 
    'crowd', 'sign', 'board', 'vehicle', 'car', 'map', 'drawing', 'flag', 
    'diagram', 'poster', 'logo', 'factory', 'temple', 'monument', 'station',
    'road', 'statue', 'palace', 'man', 'woman', 'child', 'boy', 'girl', '.pdf'
]

TARGET_32 = [
    107, 108, 109, 111, 112, 113, 117, 118, 123, 124, 125, 127, 129, 130,
    138, 140, 142, 154, 155, 158, 162, 164, 165, 166, 171, 183, 185, 189,
    192, 194, 196, 198
]

# Track existing good hashes from recipes NOT in TARGET_32
active_hashes = set()
for p in glob.glob(os.path.join(STATIC_RECIPES_DIR, "recipe_*.jpg")):
    rid = int(os.path.basename(p).split("_")[1].split(".")[0])
    if rid not in TARGET_32:
        with open(p, "rb") as f_img:
            active_hashes.add(hashlib.md5(f_img.read()).hexdigest())

print(f"Loaded {len(active_hashes)} existing unique recipe hashes.")

QUERIES_32 = {
    107: ["Tamarind rasam", "Charu rasam", "Rasam soup"],
    108: ["Bitter Gourd Curry", "Karela sabzi", "Pavakkai kulambu"],
    109: ["Bottle Gourd Curry", "Lauki sabzi curry", "Doodhi sabzi"],
    111: ["Tindora fry", "Kundru sabzi", "Ivy gourd stir fry"],
    112: ["Arbi fry", "Colocasia fry", "Seppankizhangu roast"],
    113: ["Yam curry", "Suran sabzi", "Elephant Foot Yam"],
    117: ["Turai sabzi", "Ridge gourd curry", "Beerakaya kura"],
    118: ["Snake gourd poriyal", "Padavalanga fry", "Snake gourd curry"],
    123: ["Drumstick curry", "Murungakkai kulambu", "Drumsticks curry"],
    124: ["Bharali Vangi", "Stuffed Brinjal Curry", "Baingan masala"],
    125: ["Paneer Capsicum Curry", "Capsicum sabzi", "Bell pepper curry"],
    127: ["Tomato Chutney", "Thakkali chutney", "Roasted tomato chutney"],
    129: ["Ridge gourd chutney", "Peerkangai chutney", "Beerakaya pachadi"],
    130: ["Aubergine Chutney", "Baingan bharta", "Eggplant chutney"],
    138: ["Medu vada", "Vada sambar", "Dal vada"],
    140: ["Indian breakfast Poha", "Kanda poha", "Poha bowl"],
    142: ["Rava upma", "Upma semolina", "Sooji upma"],
    154: ["Nellori Chapala Pulusu", "Pulusu stew", "Andhra rasam"],
    155: ["Mutton sukka fry", "Spicy mutton fry", "Mutton roast indian"],
    158: ["Dal Makhani", "Maa ki dal", "Dal makhani black"],
    162: ["Chitra Rajma", "Rajma masala curry", "Punjabi rajma"],
    164: ["Masala thepla", "Methi thepla", "Thepla flatbread"],
    165: ["Undhiyu", "Surti undhiyu", "Gujarati undhiyu pot"],
    166: ["Gujarati Dal", "Toor dal sweet sour", "Khatti meethi dal"],
    171: ["Chana dal coconut", "Luchi with curry", "Bengali chana dal"],
    183: ["Malabar chicken biryani", "Kozhikode biryani", "Dum chicken biryani"],
    185: ["Avial", "Aviyal kerala", "Vegetable avial"],
    189: ["Chicken Ghee Roast", "Mangalore chicken roast", "Kori ghee roast"],
    192: ["Ragi mudde saaru", "Ragi sankati mutton", "Ragi ball curry"],
    194: ["Idli sambar plate", "Idli with sambar", "Steamed idli sambar"],
    196: ["Ven Pongal", "Khara pongal ghee", "Ghee pongal"],
    198: ["Tomato Rasam", "Thakkali rasam", "Tomato rasam fresh"]
}

def is_title_clean(title):
    t = title.lower()
    for neg in NEGATIVE_KEYWORDS:
        if re.search(r'\b' + re.escape(neg) + r'\b', t):
            return False
    return True

def fetch_wiki(query, seen_hashes):
    url = f"https://commons.wikimedia.org/w/api.php?action=query&format=json&generator=search&gsrnamespace=6&gsrsearch={urllib.parse.quote(query)}&gsrlimit=5&prop=imageinfo&iiprop=url|size"
    req = urllib.request.Request(url, headers=WIKI_HEADERS)
    try:
        with urllib.request.urlopen(req, timeout=8) as resp:
            data = json.loads(resp.read().decode('utf-8'))
            pages = data.get("query", {}).get("pages", {})
            for pid, pdata in pages.items():
                title = pdata.get("title", "")
                if not is_title_clean(title):
                    continue
                info = pdata.get("imageinfo", [{}])[0]
                img_url = info.get("url")
                size = info.get("size", 0)
                if not img_url or size < 6000:
                    continue
                try:
                    img_req = urllib.request.Request(img_url, headers=WIKI_HEADERS)
                    with urllib.request.urlopen(img_req, timeout=10) as img_resp:
                        raw = img_resp.read()
                        if len(raw) < 6000:
                            continue
                        h = hashlib.md5(raw).hexdigest()
                        if h in seen_hashes:
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
                        return img, h, title
                except Exception:
                    continue
    except Exception:
        pass
    return None, None, None

def fetch_openverse(query, seen_hashes):
    url = f"https://api.openverse.org/v1/images/?q={urllib.parse.quote(query)}&page_size=8"
    req = urllib.request.Request(url, headers=OPENVERSE_HEADERS)
    try:
        with urllib.request.urlopen(req, timeout=8) as resp:
            data = json.loads(resp.read().decode('utf-8'))
            for r in data.get("results", []):
                title = r.get("title") or ""
                if not is_title_clean(title):
                    continue
                img_url = r.get("url")
                if not img_url:
                    continue
                try:
                    img_req = urllib.request.Request(img_url, headers={'User-Agent': 'Mozilla/5.0'})
                    with urllib.request.urlopen(img_req, timeout=8) as img_resp:
                        raw = img_resp.read()
                        if len(raw) < 6000:
                            continue
                        h = hashlib.md5(raw).hexdigest()
                        if h in seen_hashes:
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
                        return img, h, title
                except Exception:
                    continue
    except Exception:
        pass
    return None, None, None

with open(DATA_PATH, "r", encoding="utf-8") as f:
    recipes_list = json.load(f)
recipes_by_id = {r["recipe_id"]: r for r in recipes_list}

success_count = 0
failed = []

for idx, rid in enumerate(TARGET_32, 1):
    r = recipes_by_id[rid]
    rname = r["recipe_name"]
    queries = QUERIES_32[rid]
    
    found_img, found_h, found_title = None, None, None
    for q in queries:
        img, h, title = fetch_wiki(q, active_hashes)
        if img:
            found_img, found_h, found_title = img, h, title
            break
        time.sleep(0.2)
        
    if not found_img:
        for q in queries:
            img, h, title = fetch_openverse(q, active_hashes)
            if img:
                found_img, found_h, found_title = img, h, title
                break
            time.sleep(0.2)
            
    if found_img and found_h:
        target_path = os.path.join(STATIC_RECIPES_DIR, f"recipe_{rid}.jpg")
        found_img.save(target_path, "JPEG", quality=85, optimize=True)
        with open(target_path, "rb") as saved_file:
            saved_hash = hashlib.md5(saved_file.read()).hexdigest()
        active_hashes.add(saved_hash)
        r["image_link"] = f"/static/images/recipes/recipe_{rid}.jpg"
        success_count += 1
        print(f"[{idx:2d}/32] Recipe {rid:3d} ({rname[:28]:28s}) -> '{found_title[:30]}' (Hash: {saved_hash[:8]})")
    else:
        print(f"[{idx:2d}/32] Recipe {rid:3d} ({rname[:28]:28s}) -> FAILED")
        failed.append(rid)

with open(DATA_PATH, "w", encoding="utf-8") as f:
    json.dump(recipes_list, f, indent=2, ensure_ascii=False)

print("\n" + "="*50)
print(f"Finished 32 batch! Success: {success_count}/32. Failed: {len(failed)}")
if failed:
    print(f"Failed RIDs: {failed}")
