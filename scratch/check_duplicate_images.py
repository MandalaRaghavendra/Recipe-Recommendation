import os
import hashlib
from collections import defaultdict
import json

recipes_dir = r"d:\recipie\Recipe-Recommendation\web-app\static\images\recipes"
with open(r"d:\recipie\Recipe-Recommendation\ai-service\data.json", "r", encoding="utf-8") as f:
    recipes = {r["recipe_id"]: r["recipe_name"] for r in json.load(f)}

hashes = defaultdict(list)
for i in range(1, 199):
    fn = f"recipe_{i}.jpg"
    p = os.path.join(recipes_dir, fn)
    if os.path.exists(p):
        with open(p, "rb") as f:
            h = hashlib.md5(f.read()).hexdigest()
        hashes[h].append(i)

print(f"Total unique image contents out of 198 files: {len(hashes)}")
for h, ids in hashes.items():
    if len(ids) > 1:
        print(f"\nHash {h[:8]} shared by {len(ids)} recipes:")
        for rid in ids:
            print(f"   ID {rid}: {recipes.get(rid)}")
