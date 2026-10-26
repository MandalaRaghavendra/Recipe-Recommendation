import os
import json
import urllib.request
import urllib.parse

WIKI_FILES = {
    "pootharekulu.jpg": "File:Pootharekulu dry fruits.jpg",
    "mango_thokku.jpg": "File:Grated Mango Pickle.jpg",
    "mutton_sukka.jpg": "File:Mutton Fry.jpg",
    "cabbage_poriyal.jpg": "File:Cabbage and Carrot Poriyal.jpg",
    "yellow_dal.jpg": "File:Dal Tadka-Delhi.jpg",
    "ginger_chutney.jpg": "File:Pesarattu and Ginger chutney.jpg"
}

DEST_DIR = r"d:\recipie\Recipe-Recommendation\web-app\static\images\recipes"
os.makedirs(DEST_DIR, exist_ok=True)

headers = {'User-Agent': 'TastioApp/1.0 (contact: admin@tastio.local)'}

for local_name, wiki_file in WIKI_FILES.items():
    dest_path = os.path.join(DEST_DIR, local_name)
    if os.path.exists(dest_path) and os.path.getsize(dest_path) > 1000:
        print(f"Skipping {local_name}, already exists")
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
