import os
import json
import hashlib
from collections import defaultdict, Counter
import sys

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding='utf-8')

PROJECT_ROOT = "d:/recipie/Recipe-Recommendation"
DATA_PATH = os.path.join(PROJECT_ROOT, "ai-service", "data.json")
STATIC_RECIPES_DIR = os.path.join(PROJECT_ROOT, "web-app", "static", "images", "recipes")

with open(DATA_PATH, "r", encoding="utf-8") as f:
    recipes = json.load(f)

hashes_map = defaultdict(list)
missing = []

for r in recipes:
    rid = r["recipe_id"]
    p = os.path.join(STATIC_RECIPES_DIR, f"recipe_{rid}.jpg")
    if not os.path.exists(p):
        missing.append((rid, r["recipe_name"]))
    else:
        with open(p, "rb") as f_img:
            h = hashlib.md5(f_img.read()).hexdigest()
            hashes_map[h].append((rid, r["recipe_name"]))

dup_groups = {h: items for h, items in hashes_map.items() if len(items) > 1}

print(f"Total recipes: {len(recipes)}")
print(f"Total unique image hashes: {len(hashes_map)}")
print(f"Missing images: {len(missing)}")
print(f"Duplicate hash groups: {len(dup_groups)}")

for h, items in dup_groups.items():
    print(f"\nDuplicate Hash {h[:8]} shared by {len(items)} recipes:")
    for rid, name in items:
        print(f"  - [{rid:3d}] {name}")
