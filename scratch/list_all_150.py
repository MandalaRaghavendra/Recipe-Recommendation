import json

with open('ai-service/data.json', 'r', encoding='utf-8') as f:
    recipes = json.load(f)

for r in recipes:
    print(f"[{r['recipe_id']:3d}] {r['recipe_name']:42s} | {r.get('cuisine', ''):12s} | {r.get('meal_type', ''):10s} | {r.get('veg_nonveg', ''):7s} | {r.get('image_link', '')}")
