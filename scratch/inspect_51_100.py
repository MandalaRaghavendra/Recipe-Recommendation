import json

keywords = json.load(open('scratch/recipe_search_keywords.json', encoding='utf-8'))
for item in keywords[50:100]:
    rid = item['id']
    name = item['name']
    img = item.get('current_img', '')
    print(f"[{rid:3d}] {name:38s} -> {img}")
