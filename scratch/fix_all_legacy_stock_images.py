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

# Exact mapping of verified food dishes for recipes that had wrong / legacy images
ACCURATE_DISH_FILES = {
    # 25: Andhra Special Pongal -> Delicious hot Ven Pongal with cashews (NOT Rangoli floor art!)
    25: "File:Ven Pongal with cashew.jpg",
    # 26: Gongura Pappu -> Real yellow dal with greens (NOT empty clay pot!)
    26: "File:Tadka Daal (Indian lentil curry).jpg",
    # 27: Pesarattu -> Crispy green moong dal dosa (NOT concert singer!)
    27: "File:Pesarattu-Upma with Ginger Chutney.JPG",
    # 28: Gutti Vankaya Kura -> Stuffed brinjal curry
    28: "File:Bharali Vangi (Stuffed Brinjal Curry).jpg",
    # 29: Andhra Chicken Curry
    29: "File:Andhra Chicken Curry - WCI-Day0-Dinner.jpg",
    # 30: Dibba Rotti -> Andhra minapa rotti / thick lentil uttapam
    30: "File:Back side of Mix lentils Uttapam P 20190410 144927.jpg",
    # 31: Tamarind Rice
    31: "File:LEMON PULIHORA.JPG",
    # 32: Tomato Pappu
    32: "File:Boiled yellow lentil tomato ginger garlic.jpg",
    # 33: Aloo Vepudu -> Crispy potato fry
    33: "File:Alu Bhaja.jpg",
    # 34: Coconut Chutney
    34: "File:Coconut Chutney in a bowl.jpg",
    # 35: Lemon Rice
    35: "File:Chitranna (Lemon Rice) prepared by an indian woman.jpg",
    # 36: Punugulu -> Crispy fritters
    36: "File:Mysore Bonda-Noida-UP-SP005.jpg",
    # 37: Mamidikaya Pappu -> Mango dal
    37: "File:Tok Dal or Mango Dal (Bengali cuisine).jpg",
    # 38: Mirapakaya Bajji -> Chili fritters
    38: "File:Mirapakaya Bajji or Mirchi Bhajji.JPG",
    # 39: Sunnundalu -> Urad dal jaggery laddu
    39: "File:Andhra Telangana Sweet - Sunnundalu.jpg",
    # 40: Chicken Biryani
    40: "File:Chicken Biryani-Pune-Maharashtra-SP001.jpg",
    # 42: Bendakaya Fry -> Okra stir fry
    42: "File:Bhindi fry.jpg",
    # 43: Rasam (Chaaru)
    43: "File:Tomato Rasam - Home Made.JPG",
    # 44: Bobbatlu -> Puran poli / sweet flatbread
    44: "File:Obbattu.jpg",
    # 45: Chicken Liver Fry
    45: "File:Fried Chicken Liver.jpg",
    # 46: Masala Vada
    46: "File:Parippu Vada aka Paruppu Vadai - Vada made with Lentil.jpg",
    # 47: Aratikaya Fry -> Raw banana fry
    47: "File:Raw Banana Fry FoodBells of WELLBELLS Guntur AndhraPradesh.jpg",
    # 48: Ulavacharu -> Horse gram soup / Kollu rasam
    48: "File:Kollu rasam.JPG",
    # 49: Chicken Fry (Kodi Vepudu)
    49: "File:Chicken 65 (Fried Chicken).jpg",
    # 50: Semiya Payasam -> Vermicelli kheer
    50: "File:Seviyan-kheer-seviyan-payasam.jpg",
    # 52: Dal Tadka
    52: "File:Lunch - Wikimedia Commons Workshop - Kolkata - August 2023 - Yellow Dal Tadka.jpg",
    # 58: Crispy Masala Dosa -> Real masala dosa (NOT concert singer!)
    58: "File:Masala Dosa with Chutneys.jpg",
    # 79: Mutton Keema -> Meatball curry (NOT BBQ pork ribs!)
    79: "File:Mutton keema unde curry.jpg",
    # 88: Talakaya Kura -> Mutton head curry (NOT BBQ pork ribs!)
    88: "File:Spicy mutton curry.jpg",
    # 97: Palakura Pappu -> Spinach dal
    97: "File:Spinach Dal (Palak Dal).jpg",
    # 98: Menthi Kura Pappu -> Fenugreek dal
    98: "File:Methi Dal (Fenugreek Leaves Dal).jpg",
    # 99: Beerakaya Pappu -> Ridge gourd dal
    99: "File:Ridge gourd dal curry.jpg",
    # 100: Bachali Kura Pappu -> Malabar spinach dal
    100: "File:Malabar spinach dal bowl.jpg"
}

# Collect existing hashes from recipes NOT in ACCURATE_DISH_FILES
preserved_hashes = set()
for p in glob.glob(os.path.join(STATIC_RECIPES_DIR, "recipe_*.jpg")):
    rid = int(os.path.basename(p).split("_")[1].split(".")[0])
    if rid not in ACCURATE_DISH_FILES:
        preserved_hashes.add(hashlib.md5(open(p, "rb").read()).hexdigest())

print(f"Loaded {len(preserved_hashes)} preserved hashes.")

def download_wiki_file(title):
    api_url = f"https://commons.wikimedia.org/w/api.php?action=query&titles={urllib.parse.quote(title)}&prop=imageinfo&iiprop=url|size&format=json"
    req = urllib.request.Request(api_url, headers=WIKI_HEADERS)
    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            data = json.loads(resp.read().decode('utf-8'))
            pages = data.get('query', {}).get('pages', {})
            for p in pages.values():
                info = p.get('imageinfo', [{}])[0]
                img_url = info.get('url')
                if img_url:
                    img_req = urllib.request.Request(img_url, headers=WIKI_HEADERS)
                    with urllib.request.urlopen(img_req, timeout=12) as img_resp:
                        raw = img_resp.read()
                        im = Image.open(io.BytesIO(raw)).convert('RGB')
                        w, h_px = im.size
                        if w > 800:
                            new_w = 800
                            new_h = int(h_px * (800 / w))
                            im = im.resize((new_w, new_h), Image.Resampling.LANCZOS)
                        return im
    except Exception as e:
        print(f"  Error fetching {title}: {e}")
    return None

def search_fallback(query):
    url = f"https://commons.wikimedia.org/w/api.php?action=query&format=json&generator=search&gsrnamespace=6&gsrsearch={urllib.parse.quote(query)}&gsrlimit=3&prop=imageinfo&iiprop=url|size"
    req = urllib.request.Request(url, headers=WIKI_HEADERS)
    try:
        with urllib.request.urlopen(req, timeout=8) as resp:
            data = json.loads(resp.read().decode('utf-8'))
            pages = data.get('query', {}).get('pages', {})
            for p in pages.values():
                t = p.get('title', '')
                if any(bad in t.lower() for bad in ['festival', 'singer', 'concert', 'rangoli', 'pot.', 'pot_', '.png', '.pdf']):
                    continue
                info = p.get('imageinfo', [{}])[0]
                img_url = info.get('url')
                if img_url:
                    img_req = urllib.request.Request(img_url, headers=WIKI_HEADERS)
                    with urllib.request.urlopen(img_req, timeout=12) as img_resp:
                        raw = img_resp.read()
                        im = Image.open(io.BytesIO(raw)).convert('RGB')
                        w, h_px = im.size
                        if w > 800:
                            new_w = 800
                            new_h = int(h_px * (800 / w))
                            im = im.resize((new_w, new_h), Image.Resampling.LANCZOS)
                        return im, t
    except Exception as e:
        pass
    return None, None

success_count = 0
for rid, wiki_title in ACCURATE_DISH_FILES.items():
    print(f"Downloading Recipe {rid:3d} -> '{wiki_title}'...")
    im = download_wiki_file(wiki_title)
    if not im:
        # Try search fallback without 'File:' prefix
        clean_name = wiki_title.replace("File:", "").replace(".jpg", "").replace(".JPG", "")
        im, found_t = search_fallback(clean_name)
        if im:
            print(f"  Fallback found '{found_t}'")
            
    if im:
        target_path = os.path.join(STATIC_RECIPES_DIR, f"recipe_{rid}.jpg")
        im.save(target_path, "JPEG", quality=85, optimize=True)
        h = hashlib.md5(open(target_path, "rb").read()).hexdigest()
        preserved_hashes.add(h)
        success_count += 1
        print(f"SUCCESS: Recipe {rid:3d} updated (Hash: {h[:8]})")
    else:
        print(f"FAILED: Recipe {rid:3d} could not be updated")

print("\n" + "="*50)
print(f"Finished updating {success_count}/{len(ACCURATE_DISH_FILES)} recipes!")
