import os
import json
import urllib.request
import urllib.parse

WIKI_FILES = {
    "masala_vada.jpg": "File:Masala vada.jpg",
    "rajma_masala.jpg": "File:Rajma Masala (32081557778).jpg",
    "pongal.jpg": "File:Venpongal.jpg",
    "rava_kesari.jpg": "File:Rava Kesari.jpg",
    "besan_chilla.jpg": "File:Besan Chila.jpg",
    "crab_curry.jpg": "File:Kerala Crab curry.jpg",
    "fish_tikka.jpg": "File:Tandoori Fish tikka.jpg",
    "egg_porutu.jpg": "File:Egg-bhurji.jpg",
    "tomato_chutney.jpg": "File:TomatoChutney.jpg",
    "green_chutney.jpg": "File:Coriander coconut chutney.JPG",
    "andhra_pulusu.jpg": "File:Indian Sambar.jpg",
    "challa_charu.jpg": "File:Andhra Kadhi - Its a buttermilk based stew which is a Telugu people food. Vegetables are cooked in it..jpg"
}

DEST_DIR = r"d:\recipie\Recipe-Recommendation\web-app\static\images\recipes"
os.makedirs(DEST_DIR, exist_ok=True)

headers = {'User-Agent': 'TastioApp/1.0 (contact: admin@tastio.local)'}

for local_name, wiki_file in WIKI_FILES.items():
    dest_path = os.path.join(DEST_DIR, local_name)
    if os.path.exists(dest_path) and os.path.getsize(dest_path) > 1000:
        print(f"Skipping {local_name}, already exists ({os.path.getsize(dest_path)} bytes)")
        continue
    
    api_url = f"https://commons.wikimedia.org/w/api.php?action=query&titles={urllib.parse.quote(wiki_file)}&prop=imageinfo&iiprop=url&format=json"
    try:
        req = urllib.request.Request(api_url, headers=headers)
        with urllib.request.urlopen(req, timeout=10) as resp:
            data = json.loads(resp.read().decode('utf-8'))
            pages = data['query']['pages']
            img_url = None
            for p in pages.values():
                if 'imageinfo' in p and p['imageinfo']:
                    img_url = p['imageinfo'][0]['url']
                    break
            
            if img_url:
                print(f"Downloading {wiki_file} from {img_url}...")
                img_req = urllib.request.Request(img_url, headers=headers)
                with urllib.request.urlopen(img_req, timeout=15) as img_resp:
                    img_data = img_resp.read()
                    with open(dest_path, "wb") as f_out:
                        f_out.write(img_data)
                print(f"Saved {local_name} ({len(img_data)} bytes)")
            else:
                print(f"Could not find imageinfo for {wiki_file}")
    except Exception as e:
        print(f"Error fetching {wiki_file}: {e}")
