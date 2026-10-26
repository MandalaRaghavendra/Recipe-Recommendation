import json

with open('ai-service/data.json', 'r', encoding='utf-8') as f:
    recipes = json.load(f)

for r in recipes[:60]:
    print(f"ID: {r['recipe_id']:3d} | {r['recipe_name'][:40]:40s} | {r.get('image_link', '')}")
