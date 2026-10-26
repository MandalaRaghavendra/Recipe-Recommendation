import json
import os

with open(r"d:\recipie\Recipe-Recommendation\ai-service\data.json", "r", encoding="utf-8") as f:
    recipes = json.load(f)

print(f"Total recipes: {len(recipes)}")
for r in recipes[:30]:
    print(f"ID {r['recipe_id']}: {r['recipe_name']} | Veg: {r.get('veg_nonveg')} | Link: {r.get('image_link')}")
