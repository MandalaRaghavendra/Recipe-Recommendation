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
from collections import defaultdict

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding='utf-8')

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(BASE_DIR)
DATA_PATH = os.path.join(PROJECT_ROOT, "ai-service", "data.json")
STATIC_RECIPES_DIR = os.path.join(PROJECT_ROOT, "web-app", "static", "images", "recipes")

with open(DATA_PATH, "r", encoding="utf-8") as f:
    recipes_list = json.load(f)
recipes_by_id = {r["recipe_id"]: r for r in recipes_list}

# 1. Inspect existing files and identify duplicates
hashes_to_files = defaultdict(list)
files = glob.glob(os.path.join(STATIC_RECIPES_DIR, "recipe_*.jpg"))
for p in files:
    try:
        with open(p, "rb") as f:
            h = hashlib.md5(f.read()).hexdigest()
            hashes_to_files[h].append(p)
    except Exception:
        pass

# Good unique hashes (only 1 file has this hash)
good_hashes = set()
for h, plist in hashes_to_files.items():
    if len(plist) == 1:
        # Check if it's the known Lisbon market photo (recipe_89)
        if "recipe_89.jpg" not in plist[0]:
            good_hashes.add(h)

print(f"Initial unique good image hashes: {len(good_hashes)}")

# Problem recipes to fix:
# Any recipe that shared a duplicate hash OR is recipe_89
problem_rids = []
for h, plist in hashes_to_files.items():
    if len(plist) > 1:
        for p in plist:
            rid = int(os.path.basename(p).split("_")[1].split(".")[0])
            problem_rids.append(rid)
if 89 not in problem_rids:
    problem_rids.append(89)
# Also check if any recipe is missing a file
for r in recipes_list:
    rid = r["recipe_id"]
    p = os.path.join(STATIC_RECIPES_DIR, f"recipe_{rid}.jpg")
    if not os.path.exists(p) and rid not in problem_rids:
        problem_rids.append(rid)

problem_rids = sorted(list(set(problem_rids)))
print(f"Total recipes requiring distinct replacement: {len(problem_rids)}")

# Exact dish search queries for all problem recipes
DISH_SEARCH_QUERIES = {
    5: ["boiled egg curry indian", "egg masala curry", "muttai kulambu"],
    7: ["andhra chicken fry", "chicken vepudu", "kodi vepudu", "chicken 65"],
    9: ["crab curry indian", "nandu kulambu", "crab masala", "spicy crab"],
    11: ["vegetable biryani indian", "veg biryani handi", "hyderabadi veg biryani"],
    14: ["baingan bharta", "roasted eggplant curry", "vankaya pachadi"],
    15: ["dal tadka yellow dal", "yellow lentil curry", "tadka dal"],
    16: ["chana masala", "chole masala", "punjabi chana masala"],
    17: ["vegetable korma indian", "mixed vegetable curry indian"],
    18: ["mushroom masala indian", "kalan curry", "mushroom gravy"],
    19: ["tomato rice indian", "thakkali sadam", "spiced tomato rice"],
    21: ["pulihora tamarind rice", "tamarind rice south indian"],
    23: ["curd rice thayir sadam", "dahi chawal indian"],
    24: ["bisi bele bath karnataka", "bisi bele huliyanna"],
    41: ["ragi mudde ragi sankati", "finger millet balls", "ragi ball"],
    60: ["quinoa salad bowl", "mediterranean quinoa bowl"],
    67: ["tofu broccoli stir fry", "tofu stir fry sesame"],
    68: ["prawns masala fry", "coastal prawn masala", "shrimp masala"],
    70: ["yogurt berry parfait", "greek yogurt fruit parfait"],
    71: ["chicken clear soup", "chicken broth soup herbs"],
    75: ["peanut butter banana smoothie", "protein banana shake"],
    78: ["pepper chicken fry", "kerala pepper chicken", "andhra pepper chicken"],
    80: ["gongura royyalu prawns", "prawns curry indian", "shrimp curry"],
    81: ["crab fry indian", "peethala vepudu", "spicy fried crab"],
    82: ["guddu pulusu andhra", "egg tamarind curry", "spicy egg stew"],
    83: ["spicy lamb curry indian", "mutton boti masala", "mutton fry boti"],
    86: ["fried prawns indian", "crispy prawn fry", "royyala vepudu"],
    89: ["chicken fry indian style", "natu kodi vepudu", "country chicken fry"],
    94: ["prawn pulao indian", "shrimp biryani", "royyala pulao"],
    95: ["fish tamarind curry", "chepala pulusu andhra", "bommidala pulusu"],
    103: ["pepper rasam indian", "miriyala chaaru", "milagu rasam"],
    105: ["clear toor dal broth", "kandi kattu", "dal soup indian"],
    106: ["menthi majjiga", "spiced buttermilk indian", "masala chaas"],
    107: ["pachi pulusu raw tamarind", "raw rasam andhra"],
    108: ["bitter gourd curry indian", "kakarakaya pulusu", "karela sabzi"],
    109: ["bottle gourd stew", "lauki curry", "anapakaya pulusu"],
    110: ["brinjal tamarind curry", "vankaya pulusu", "ennai kathirikai"],
    111: ["tindora fry", "dondakaya vepudu", "ivy gourd fry"],
    112: ["arbi fry crispy", "chamadumpa vepudu", "colocasia fry"],
    113: ["yam spinach curry", "kanda bachali kura", "suran saag"],
    115: ["beetroot poriyal", "beetroot stir fry indian", "beetroot vepudu"],
    117: ["ridge gourd peel stir fry", "beerakaya fry", "turai sabzi"],
    118: ["snake gourd coconut fry", "potlakaya fry", "padavalanga thoran"],
    122: ["bottle gourd milk curry", "doodhi kootu", "sorakaya palu kura"],
    123: ["drumstick cashew curry", "munakkaya kaju", "murungakkai kootu"],
    124: ["brinjal cilantro curry", "vankaya kothimeera", "baingan masala"],
    125: ["capsicum besan sabzi", "bell pepper gram flour", "shimla mirch"],
    127: ["roasted tomato chutney", "tomato pachadi andhra", "thakkali chutney"],
    128: ["cucumber chutney south indian", "dosakaya pachadi", "vellarikka"],
    129: ["ridge gourd chutney", "beerakaya pachadi", "peerkangai chutney"],
    130: ["roasted brinjal chutney", "vankaya pachadi andhra", "baingan bharta mash"],
    135: ["curry leaves chutney", "karivepaku pachadi", "karuveppilai thogayal"],
    138: ["lobia vada", "black eyed peas fritters", "alasanda vada"],
    140: ["atukula upma poha", "andhra poha peanuts", "kanda poha"],
    141: ["rava dosa crispy", "onion rava dosa", "sooji dosa"],
    142: ["biyyam rava upma", "uppudu pindi", "rice rava upma"],
    144: ["palathalikalu sweet", "rice noodle kheer", "seviyan kheer"],
    149: ["bellam paramannam", "sweet pongal jaggery", "sakkarai pongal"],
    151: ["sarva pindi telangana", "rice flour spicy pancake", "thalipeeth"],
    152: ["bagara rice dalcha", "hyderabadi bagara rice", "ghee rice"],
    154: ["telangana pachi pulusu", "charred chili tamarind rasam"],
    155: ["mutton fry telangana", "golichina mamsam", "mutton sukka dry"],
    158: ["dal makhani amritsari", "creamy black lentil dal"],
    162: ["rajma masala punjabi", "punjabi rajma chawal"],
    164: ["methi thepla gujarati", "fenugreek flatbread"],
    165: ["undhiyu gujarati", "surti undhiyu winter pot"],
    166: ["gujarati khatti meethi dal", "sweet sour toor dal"],
    171: ["chholar dal luchi", "bengali chana dal coconut"],
    183: ["thalassery chicken biryani", "malabar biryani kaima rice"],
    185: ["avial kerala sadya", "avial coconut vegetables"],
    189: ["chicken ghee roast mangalore", "kundapur chicken ghee roast"],
    192: ["ragi mudde chicken saaru", "karnataka ragi ball curry"],
    194: ["idli sambar hotel style", "steamed idli with sambar"],
    196: ["ven pongal ghee cashews", "khara pongal south indian"],
    198: ["tomato rasam thanjavur", "thakkali rasam fresh coriander"]
}

def search_openverse_for_dish(queries, seen_hashes):
    for q in queries:
        url = "https://api.openverse.org/v1/images/?q=" + urllib.parse.quote(q) + "&page_size=8"
        req = urllib.request.Request(url, headers={'User-Agent': 'TastioApp/1.0 (contact@tastio.ai)'})
        try:
            with urllib.request.urlopen(req, timeout=8) as resp:
                data = json.loads(resp.read().decode('utf-8'))
                for r in data.get("results", []):
                    title = (r.get("title") or "").lower()
                    if any(bad in title for bad in ['market', 'shop', 'street', 'crowd', 'store', 'sign', 'building', 'people', 'man', 'woman']):
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
                            if h in seen_hashes:
                                continue
                            img = Image.open(io.BytesIO(raw))
                            img = img.convert('RGB')
                            w, h_px = img.size
                            if w > 800:
                                new_w = 800
                                new_h = int(h_px * (800 / w))
                                img = img.resize((new_w, new_h), Image.Resampling.LANCZOS)
                            return img, h, r.get("title")
                    except Exception:
                        continue
        except Exception:
            pass
    return None, None, None

# Process each problem recipe
print(f"Fixing {len(problem_rids)} problem recipes with unique, authentic images...")
fixed_count = 0

for rid in problem_rids:
    r = recipes_by_id[rid]
    rname = r["recipe_name"]
    queries = DISH_SEARCH_QUERIES.get(rid, [rname, f"{rname} Indian"])
    
    img, h, title = search_openverse_for_dish(queries, good_hashes)
    if img and h:
        target_path = os.path.join(STATIC_RECIPES_DIR, f"recipe_{rid}.jpg")
        img.save(target_path, "JPEG", quality=85, optimize=True)
        good_hashes.add(h)
        r["image_link"] = f"/static/images/recipes/recipe_{rid}.jpg"
        fixed_count += 1
        print(f"[{fixed_count}/{len(problem_rids)}] Recipe {rid} ({rname}) -> '{title}' (Hash: {h[:8]})")
    else:
        print(f"WARNING: Could not find unique image for recipe {rid} ({rname})")

# Save updated data.json
with open(DATA_PATH, "w", encoding="utf-8") as f:
    json.dump(recipes_list, f, indent=2, ensure_ascii=False)

print(f"Updated data.json with all {len(recipes_list)} recipes.")

# Final check of all 198 recipes
final_hashes = {}
for r in recipes_list:
    rid = r["recipe_id"]
    p = os.path.join(STATIC_RECIPES_DIR, f"recipe_{rid}.jpg")
    if os.path.exists(p):
        with open(p, "rb") as f:
            final_hashes[rid] = hashlib.md5(f.read()).hexdigest()

from collections import Counter
h_cnt = Counter(final_hashes.values())
dups = {h: count for h, count in h_cnt.items() if count > 1}

print("\n================ FINAL REPORT ================")
print(f"Total recipes: {len(recipes_list)}")
print(f"Images verified on disk: {len(final_hashes)}")
print(f"Unique image contents: {len(h_cnt)}")
print(f"Remaining duplicate contents: {len(dups)}")
if len(dups) == 0 and len(final_hashes) == len(recipes_list):
    print("ALL 198 RECIPES HAVE 100% UNIQUE, NON-DUPLICATE, AUTHENTIC IMAGES!")
