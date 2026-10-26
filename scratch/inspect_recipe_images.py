import json

with open('ai-service/data.json', 'r', encoding='utf-8') as f:
    recipes = json.load(f)

print(f"Total recipes: {len(recipes)}")
for r in recipes:
    print(f"ID: {r['recipe_id']:3d} | Name: {r['recipe_name']:35s} | Cuisine: {r.get('cuisine', ''):12s} | Image: {r.get('image_link', '')}")
