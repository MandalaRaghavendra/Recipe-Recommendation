import json
from collections import defaultdict

with open('ai-service/data.json', 'r', encoding='utf-8') as f:
    recipes = json.load(f)

url_to_recipes = defaultdict(list)
for r in recipes:
    url_to_recipes[r.get('image_link', '')].append((r['recipe_id'], r['recipe_name']))

print(f"Total unique URLs: {len(url_to_recipes)}")
for i, (url, recs) in enumerate(url_to_recipes.items(), 1):
    print(f"\n--- URL #{i} ({len(recs)} recipes) ---")
    print(f"URL: {url}")
    print("Recipes:")
    for rid, rname in recs:
        print(f"  [{rid:3d}] {rname}")
