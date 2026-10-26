import os
import sys

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding='utf-8')
import json
import urllib.request
import urllib.parse
from PIL import Image
import io

PROJECT_ROOT = r"d:\recipie\Recipe-Recommendation"
STATIC_RECIPES_DIR = os.path.join(PROJECT_ROOT, "web-app", "static", "images", "recipes")
WIKI_HEADERS = {'User-Agent': 'TastioApp/1.0 (contact@tastio.org)'}

# Exact verified URLs or Wikimedia titles for all identified mismatched recipes
ACCURATE_IMAGE_MAP = {
    # 21: Tamarind Rice (Pulihora)
    21: {"type": "wiki", "target": "File:Andhra Pulihora.jpg"},
    # 22: Coconut Rice
    22: {"type": "unsplash", "url": "https://images.unsplash.com/photo-1596797038530-2c107229654b?w=800&auto=format&fit=crop&q=80"},
    # 29: Andhra Chicken Curry
    29: {"type": "wiki", "target": "File:Andhra Chicken Curry - WCI-Day0-Dinner.jpg"},
    # 53: Grilled Lemon Herb Chicken (replace menu)
    53: {"type": "unsplash", "url": "https://images.unsplash.com/photo-1532550907401-a500c9a57435?w=800&auto=format&fit=crop&q=80"},
    # 91: Gongura Chicken (replace RV camper)
    91: {"type": "unsplash", "url": "https://images.unsplash.com/photo-1603894584373-5ac82b2ae398?w=800&auto=format&fit=crop&q=80"},
    # 111: Dondakaya Vepudu (replace sea snake)
    111: {"type": "unsplash", "url": "https://images.unsplash.com/photo-1546833999-b9f581a1996d?w=800&auto=format&fit=crop&q=80"},
    # 116: Kakarakaya Vepudu (Bitter Gourd Fry, replace apiary)
    116: {"type": "wiki", "target": "File:Fried Bitter Gourd in Mango Sauce.jpg"},
    # 118: Potlakaya Fry (Snake Gourd Fry, replace snake dance book)
    118: {"type": "unsplash", "url": "https://images.unsplash.com/photo-1601050690597-df0568f70950?w=800&auto=format&fit=crop&q=80"},
    # 126: Gongura Pachadi (replace pencil box)
    126: {"type": "unsplash", "url": "https://images.unsplash.com/photo-1589301760014-d929f3979dbc?w=800&auto=format&fit=crop&q=80"},
    # 142: Biyyam Rava Upma (replace rotisserie)
    142: {"type": "wiki", "target": "File:South Indian Breakfast of Upma.jpg"},
    # 146: Kakinada Gottam Kaja (replace frying pan)
    146: {"type": "wiki", "target": "File:Kotayya Kaja Kakinada kaja (1).jpg"},
    # 148: Rava Kesari (Semolina Halwa with Ghee & Saffron)
    148: {"type": "wiki", "target": "File:Sooji Halwa (Rava Sheera).jpg"},
    # 156: Sakinalu (Telangana Festive Crunch, replace paper towel)
    156: {"type": "wiki", "target": "File:Murukku or Chakli.jpg"},
    # 161: Sarson Ka Saag & Makki Di Roti (replace petri dish)
    161: {"type": "wiki", "target": "File:Makki di Roti Te Sarson Da Saag.jpg"},
    # 180: Sabudana Khichdi (replace coral fungus)
    180: {"type": "wiki", "target": "File:Sabudana Khichdi.jpg"},
    # 186: Karimeen Pollichathu (replace terrapin turtle)
    186: {"type": "wiki", "target": "File:Karimeen Ilayill Pollichathu.JPG"},
    # 197: Madurai Kothu Parotta (replace crutch)
    197: {"type": "wiki", "target": "File:Chicken Kothu Parotta.jpg"}
}

def get_wiki_direct_url(title):
    api_url = f"https://commons.wikimedia.org/w/api.php?action=query&titles={urllib.parse.quote(title)}&prop=imageinfo&iiprop=url|size&format=json"
    req = urllib.request.Request(api_url, headers=WIKI_HEADERS)
    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            data = json.loads(resp.read().decode('utf-8'))
            pages = data.get("query", {}).get("pages", {})
            for pid, pdata in pages.items():
                info = pdata.get("imageinfo", [{}])[0]
                return info.get("url")
    except Exception as e:
        print(f"Error fetching wiki url for {title}: {e}")
    return None

def download_and_save(url, target_path):
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'})
    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            raw = resp.read()
            if len(raw) < 5000:
                return False
            img = Image.open(io.BytesIO(raw)).convert('RGB')
            w, h = img.size
            if w > 800:
                new_w = 800
                new_h = int(h * (800 / w))
                img = img.resize((new_w, new_h), Image.Resampling.LANCZOS)
            img.save(target_path, "JPEG", quality=88, optimize=True)
            return True
    except Exception as e:
        print(f"Error downloading {url}: {e}")
        return False

success = 0
for rid, cfg in ACCURATE_IMAGE_MAP.items():
    target_path = os.path.join(STATIC_RECIPES_DIR, f"recipe_{rid}.jpg")
    img_url = None
    if cfg["type"] == "unsplash":
        img_url = cfg["url"]
    elif cfg["type"] == "wiki":
        img_url = get_wiki_direct_url(cfg["target"])
    
    if img_url:
        ok = download_and_save(img_url, target_path)
        if ok:
            print(f"✅ Successfully updated Recipe {rid} -> {target_path}")
            success += 1
        else:
            print(f"❌ Failed to download for Recipe {rid}")
    else:
        print(f"❌ No URL found for Recipe {rid}")

print(f"\nDone! Updated {success}/{len(ACCURATE_IMAGE_MAP)} recipe images with verified food photos.")
