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
from collections import defaultdict, Counter

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding='utf-8')

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(BASE_DIR)
DATA_PATH = os.path.join(PROJECT_ROOT, "ai-service", "data.json")
STATIC_RECIPES_DIR = os.path.join(PROJECT_ROOT, "web-app", "static", "images", "recipes")

WIKI_HEADERS = {'User-Agent': 'TastioApp/1.0 (contact@tastio.org)'}
OPENVERSE_HEADERS = {'User-Agent': 'TastioApp/1.0 (contact@tastio.org)'}

NEGATIVE_KEYWORDS = [
    'market', 'building', 'shop', 'store', 'street', 'people', 'portrait', 
    'crowd', 'sign', 'board', 'vehicle', 'car', 'map', 'drawing', 'flag', 
    'diagram', 'poster', 'logo', 'factory', 'temple', 'monument', 'station',
    'road', 'statue', 'palace', 'man', 'woman', 'child', 'boy', 'girl'
]

with open(DATA_PATH, "r", encoding="utf-8") as f:
    recipes_list = json.load(f)
recipes_by_id = {r["recipe_id"]: r for r in recipes_list}

# Target recipes to replace / fix:
PROBLEM_RIDS = [
    5, 7, 8, 9, 11, 14, 15, 16, 17, 18, 19, 21, 23, 24, 41, 56, 60, 67, 68, 70,
    71, 75, 78, 80, 81, 82, 83, 85, 86, 89, 94, 95, 103, 105, 106, 107, 108, 109,
    110, 111, 112, 113, 115, 117, 118, 122, 123, 124, 125, 127, 128, 129, 130, 135,
    138, 140, 141, 142, 144, 149, 151, 152, 154, 155, 158, 162, 164, 165, 166, 171,
    183, 185, 189, 192, 194, 196, 198
]

# Track existing good hashes from recipes NOT in problem list
active_hashes = set()
for r in recipes_list:
    rid = r["recipe_id"]
    if rid not in PROBLEM_RIDS:
        p = os.path.join(STATIC_RECIPES_DIR, f"recipe_{rid}.jpg")
        if os.path.exists(p):
            with open(p, "rb") as f_img:
                h = hashlib.md5(f_img.read()).hexdigest()
                active_hashes.add(h)

print(f"Loaded {len(active_hashes)} existing unique non-problem recipe hashes.")
print(f"Targeting {len(PROBLEM_RIDS)} recipes for distinct, authentic image download.")

DISH_QUERIES = {
    5: ["Andhra egg curry", "Egg curry indian", "Muttai kulambu", "Egg masala curry"],
    7: ["Andhra chicken fry", "Kodi vepudu", "Chicken fry indian", "Chicken 65"],
    8: ["Andhra mutton curry", "Mutton curry indian", "Spicy lamb curry indian"],
    9: ["Andhra crab curry", "Crab curry indian", "Nandu kulambu", "Crab masala"],
    11: ["Vegetable biryani handi", "Veg biryani indian", "Vegetable dum biryani"],
    14: ["Baingan bharta", "Smoky roasted eggplant curry", "Vankaya pachadi"],
    15: ["Dal tadka yellow dal", "Tadka dal", "Yellow lentil curry indian"],
    16: ["Chana masala chickpea", "Chole masala", "Punjabi chana masala"],
    17: ["Vegetable korma curry", "Mixed vegetable curry indian", "Navratan korma"],
    18: ["Mushroom masala curry", "Kalan curry", "Spicy mushroom gravy"],
    19: ["Tomato rice south indian", "Thakkali sadam", "Spiced tomato rice"],
    21: ["Tamarind rice pulihora", "Puliyodharai", "Chintapandu pulihora"],
    23: ["Curd rice thayir sadam", "Dahi chawal indian", "Tempered curd rice"],
    24: ["Bisi bele bath karnataka", "Bisi bele huliyanna", "Sambar sadam"],
    41: ["Ragi mudde", "Ragi sankati", "Finger millet balls"],
    56: ["Vegetable oats upma", "Oats upma indian", "Vegetable upma breakfast"],
    60: ["Quinoa salad bowl", "Mediterranean quinoa salad", "Quinoa vegetable bowl"],
    67: ["Tofu broccoli stir fry", "Tofu stir fry sesame", "Tofu vegetables stir fry"],
    68: ["Coastal prawn masala", "Prawns masala fry", "Spicy shrimp curry"],
    70: ["Yogurt berry parfait", "Greek yogurt fruit parfait", "Berry parfait glass"],
    71: ["Chicken clear soup bowl", "Chicken broth soup herbs", "Healthy chicken soup"],
    75: ["Peanut butter banana smoothie", "Protein banana shake", "Banana smoothie glass"],
    78: ["Pepper chicken fry", "Kodi vepudu pepper", "Kerala pepper chicken"],
    80: ["Gongura royyalu prawns", "Prawns curry indian", "Spicy shrimp curry indian"],
    81: ["Peethala vepudu crab fry", "Crab fry indian", "Spicy fried crab"],
    82: ["Guddu pulusu andhra", "Egg tamarind curry", "Spicy boiled egg stew"],
    83: ["Boti kura andhra", "Mutton boti masala", "Mutton dry fry indian"],
    85: ["Vanjaram fish fry", "Spicy tawa fish fry", "Crispy fish fry indian", "Nellore fish fry"],
    86: ["Crispy fried prawns indian", "Royyala vepudu", "Fried shrimp indian", "Golden fried prawns"],
    89: ["Country chicken fry indian", "Natu kodi fry andhra", "Spicy chicken dry roast"],
    94: ["Royyala pulao prawn", "Prawn biryani", "Shrimp pulao indian"],
    95: ["Bommidala pulusu fish", "Chepala pulusu andhra", "Tangy fish curry indian"],
    103: ["Miriyala chaaru pepper rasam", "Milagu rasam", "Pepper rasam south indian"],
    105: ["Kandi kattu dal broth", "Toor dal rasam", "Paruppu rasam clear"],
    106: ["Menthi majjiga buttermilk", "Spiced buttermilk indian", "Masala chaas tempered"],
    107: ["Pachi pulusu rayalaseema", "Raw tamarind rasam", "Charred onion pulusu"],
    108: ["Kakarakaya pulusu bitter gourd", "Pavakkai kulambu", "Bitter gourd tamarind stew"],
    109: ["Anapakaya pulusu bottle gourd", "Sorakaya pulusu", "Lauki tamarind curry"],
    110: ["Vankaya pulusu brinjal", "Ennai kathirikai", "Baby eggplant tamarind curry"],
    111: ["Dondakaya vepudu tindora fry", "Ivy gourd fry peanuts", "Kundru stir fry"],
    112: ["Chamadumpa vepudu arbi fry", "Crispy taro root fry", "Seppankizhangu roast"],
    113: ["Kanda bachali kura yam", "Suran saag curry", "Yam malabar spinach"],
    115: ["Andhra beetroot vepudu", "Beetroot poriyal stir fry", "Beetroot thoran"],
    117: ["Beerakaya fry ridge gourd", "Ridge gourd stir fry indian", "Turai sabzi fry"],
    118: ["Potlakaya fry snake gourd", "Snake gourd coconut stir fry", "Padavalanga thoran"],
    122: ["Sorakaya palu kura bottle gourd", "Doodhi curry milk", "Bottle gourd white gravy"],
    123: ["Munakkaya kaju kura drumstick", "Drumstick cashew curry", "Murungakkai masala"],
    124: ["Vankaya kothimeera karam brinjal", "Stuffed brinjal cilantro", "Baingan coriander masala"],
    125: ["Capsicum senagapindi kura", "Bell pepper besan sabzi", "Shimla mirch gram flour"],
    127: ["Tomato pachadi andhra chutney", "Rustic roasted tomato chutney", "Thakkali thogayal"],
    128: ["Dosakaya pachadi cucumber chutney", "Yellow cucumber chutney", "Dosakaya chutney"],
    129: ["Beerakaya pachadi ridge gourd", "Peerkangai thogayal", "Ridge gourd chutney"],
    130: ["Vankaya pachadi roasted eggplant", "Fire roasted brinjal chutney", "Baingan bharta chutney"],
    135: ["Karivepaku pachadi curry leaf", "Karuveppilai thogayal", "Curry leaves chutney south indian"],
    138: ["Alasanda vada black eyed peas", "Lobia vada fritters", "Masala vadai golden"],
    140: ["Atukula upma poha peanuts", "Andhra poha breakfast", "Kanda poha indian"],
    141: ["Crispy rava dosa", "Onion rava dosa hotel style", "Sooji dosa crispy lace"],
    142: ["Biyyam rava upma coarse rice", "Uppudu pindi andhra", "Arisi upma south indian"],
    144: ["Palathalikalu sweet noodle kheer", "Seviyan kheer vermicelli", "Rice noodle payasam"],
    149: ["Bellam paramannam sweet pongal", "Sakkarai pongal jaggery", "Chakkara pongal ghee"],
    151: ["Sarva pindi telangana pancake", "Thalipeeth crispy spiced", "Spicy rice flour pancake"],
    152: ["Hyderabadi bagara rice", "Bagara khana spiced rice", "Ghee rice cashews"],
    154: ["Telangana pachi pulusu", "Raw tamarind chili rasam", "Charred onion pachi pulusu"],
    155: ["Golichina mamsam telangana", "Mutton sukka dry roast", "Spicy browned lamb fry"],
    158: ["Dal makhani amritsari creamy", "Slow cooked black lentils dal", "Maa ki dal makhani"],
    162: ["Punjabi rajma masala red kidney", "Rajma curry gravy", "Rajma masala punjabi style"],
    164: ["Gujarati methi thepla", "Methi thepla flatbread", "Fenugreek flatbread thepla"],
    165: ["Undhiyu gujarati surti", "Authentic undhiyu pot", "Surti undhiyu mixed vegetable"],
    166: ["Gujarati khatti meethi dal", "Sweet and sour toor dal gujarati", "Gujarati dal peanuts"],
    171: ["Chholar dal with luchi", "Bengali chana dal coconut", "Luchi chholar dal"],
    183: ["Thalassery biryani kaima rice", "Malabar chicken biryani dum", "Thalassery chicken biryani"],
    185: ["Kerala avial sadya", "Authentic aviayal vegetables coconut", "Avial coconut oil curry leaves"],
    189: ["Mangalore chicken ghee roast", "Kori ghee roast spicy red", "Chicken ghee roast mangalorean"],
    192: ["Ragi mudde with nati koli saaru", "Ragi ball chicken curry saaru", "Ragi mudde chicken gravy"],
    194: ["Idli sambar soft steamed", "Idli with vegetable sambar", "South indian idli sambar plate"],
    196: ["Ven pongal with coconut chutney", "Khara pongal ghee black pepper", "Ghee ven pongal cashews"],
    198: ["Thanjavur tomato rasam", "Thakkali rasam fresh coriander", "Spiced tomato rasam soup"]
}

def is_title_clean(title):
    t = title.lower()
    for neg in NEGATIVE_KEYWORDS:
        # Match whole word or prominent substring
        if re.search(r'\b' + re.escape(neg) + r'\b', t):
            return False
    return True

def fetch_image_from_wikimedia(query, seen_hashes):
    url = f"https://commons.wikimedia.org/w/api.php?action=query&format=json&generator=search&gsrnamespace=6&gsrsearch={urllib.parse.quote(query)}&gsrlimit=6&prop=imageinfo&iiprop=url|size"
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
                if not img_url or size < 8000:
                    continue
                # Download and test
                try:
                    img_req = urllib.request.Request(img_url, headers=WIKI_HEADERS)
                    with urllib.request.urlopen(img_req, timeout=10) as img_resp:
                        raw = img_resp.read()
                        if len(raw) < 8000:
                            continue
                        h = hashlib.md5(raw).hexdigest()
                        if h in seen_hashes:
                            continue
                        img = Image.open(io.BytesIO(raw))
                        img = img.convert('RGB')
                        w, h_px = img.size
                        if w < 200 or h_px < 200:
                            continue
                        if w > 800:
                            new_w = 800
                            new_h = int(h_px * (800 / w))
                            img = img.resize((new_w, new_h), Image.Resampling.LANCZOS)
                        return img, h, title, "Wikimedia"
                except Exception:
                    continue
    except Exception:
        pass
    return None, None, None, None

def fetch_image_from_openverse(query, seen_hashes):
    url = f"https://api.openverse.org/v1/images/?q={urllib.parse.quote(query)}&page_size=8"
    req = urllib.request.Request(url, headers=OPENVERSE_HEADERS)
    try:
        with urllib.request.urlopen(req, timeout=8) as resp:
            data = json.loads(resp.read().decode('utf-8'))
            results = data.get("results", [])
            for r in results:
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
                        if len(raw) < 8000:
                            continue
                        h = hashlib.md5(raw).hexdigest()
                        if h in seen_hashes:
                            continue
                        img = Image.open(io.BytesIO(raw))
                        img = img.convert('RGB')
                        w, h_px = img.size
                        if w < 200 or h_px < 200:
                            continue
                        if w > 800:
                            new_w = 800
                            new_h = int(h_px * (800 / w))
                            img = img.resize((new_w, new_h), Image.Resampling.LANCZOS)
                        return img, h, title, "Openverse"
                except Exception:
                    continue
    except Exception:
        pass
    return None, None, None, None

# Run search and replacement
success_count = 0
failed_rids = []

for idx, rid in enumerate(PROBLEM_RIDS, 1):
    r = recipes_by_id[rid]
    rname = r["recipe_name"]
    queries = DISH_QUERIES.get(rid, [rname, f"{rname} Indian cuisine"])
    
    found_img = None
    found_hash = None
    found_title = None
    found_src = None
    
    # 1. Try Wikimedia Commons first
    for q in queries:
        img, h, title, src = fetch_image_from_wikimedia(q, active_hashes)
        if img:
            found_img, found_hash, found_title, found_src = img, h, title, src
            break
        time.sleep(0.3)
    
    # 2. Try Openverse if Wikimedia didn't find one
    if not found_img:
        for q in queries:
            img, h, title, src = fetch_image_from_openverse(q, active_hashes)
            if img:
                found_img, found_hash, found_title, found_src = img, h, title, src
                break
            time.sleep(0.3)
            
    if found_img and found_hash:
        target_path = os.path.join(STATIC_RECIPES_DIR, f"recipe_{rid}.jpg")
        found_img.save(target_path, "JPEG", quality=85, optimize=True)
        # Record new hash of the saved file to ensure no collisions
        with open(target_path, "rb") as saved_file:
            saved_hash = hashlib.md5(saved_file.read()).hexdigest()
        active_hashes.add(saved_hash)
        r["image_link"] = f"/static/images/recipes/recipe_{rid}.jpg"
        success_count += 1
        print(f"[{idx}/{len(PROBLEM_RIDS)}] Recipe {rid:3d} ({rname[:32]:32s}) -> [{found_src}] '{found_title[:35]}' (Hash: {saved_hash[:8]})")
    else:
        print(f"[{idx}/{len(PROBLEM_RIDS)}] Recipe {rid:3d} ({rname[:32]:32s}) -> FAILED TO FIND UNIQUE MATCH")
        failed_rids.append(rid)

# Save data.json
with open(DATA_PATH, "w", encoding="utf-8") as f:
    json.dump(recipes_list, f, indent=2, ensure_ascii=False)

print("\n" + "="*50)
print(f"Successfully replaced: {success_count}/{len(PROBLEM_RIDS)}")
print(f"Failed count: {len(failed_rids)}")
if failed_rids:
    print(f"Failed recipe IDs: {failed_rids}")
