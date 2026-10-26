import json

with open(r"d:\recipie\Recipe-Recommendation\ai-service\data.json", "r", encoding="utf-8") as f:
    recipes = json.load(f)

with open(r"d:\recipie\Recipe-Recommendation\scratch\recipe_summary.txt", "w", encoding="utf-8") as out:
    for r in recipes:
        out.write(f"ID {r['recipe_id']:3d} | {r.get('veg_nonveg', 'N/A'):7s} | {r.get('cuisine', 'N/A'):14s} | {r['recipe_name']}\n")

print(f"Wrote {len(recipes)} recipes to recipe_summary.txt")
