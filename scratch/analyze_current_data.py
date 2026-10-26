import json
from collections import Counter

with open(r"d:\recipie\Recipe-Recommendation\ai-service\data.json", "r", encoding="utf-8") as f:
    recipes = json.load(f)

img_links = [r.get("image_link", "") for r in recipes]
counts = Counter(img_links)

print("Duplicates in data.json:")
for link, c in counts.most_common():
    if c > 1:
        print(f"{c} recipes share: {link}")

print("\nNon-local or strange links:")
for r in recipes:
    link = r.get("image_link", "")
    if not link.startswith("/static/images/recipes/"):
        print(f"Recipe {r['recipe_id']} ({r['recipe_name']}): {link}")
