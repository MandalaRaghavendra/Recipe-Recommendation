import json
with open('ai-service/data.json', 'r', encoding='utf-8') as f:
    recipes = json.load(f)

for r in recipes:
    rid = r['recipe_id']
    name = r['recipe_name']
    img = r.get('image_link', '')
    print(f"[{rid:3d}] {name[:40]:40s} -> {img}")
