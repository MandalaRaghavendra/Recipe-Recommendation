import json
import os
import hashlib

PROJECT_ROOT = "d:/recipie/Recipe-Recommendation"
STATIC_RECIPES_DIR = os.path.join(PROJECT_ROOT, "web-app", "static", "images", "recipes")

# Check MD5 hashes of all current files:
hashes_map = {}
for i in range(1, 199):
    p = os.path.join(STATIC_RECIPES_DIR, f"recipe_{i}.jpg")
    if os.path.exists(p):
        hashes_map[i] = hashlib.md5(open(p, "rb").read()).hexdigest()

recipes = json.load(open("ai-service/data.json", encoding="utf-8"))

# Check recipes 25, 26, 27 hashes:
h25 = hashes_map[25] # Rangoli
h26 = hashes_map[26] # Clay pot
h27 = hashes_map[27] # Concert singer

print(f"Recipe 25 (Rangoli) Hash: {h25}")
print(f"Recipe 26 (Clay pot) Hash: {h26}")
print(f"Recipe 27 (Concert singer) Hash: {h27}")

# Find all recipes that have the exact same hash as 25, 26, 27 or other legacy hashes:
for rid, h in hashes_map.items():
    if h == h25:
        print(f"Shares Rangoli hash ({h[:8]}): [{rid}] {recipes[rid-1]['recipe_name']}")
    if h == h26:
        print(f"Shares Clay pot hash ({h[:8]}): [{rid}] {recipes[rid-1]['recipe_name']}")
    if h == h27:
        print(f"Shares Singer hash ({h[:8]}): [{rid}] {recipes[rid-1]['recipe_name']}")
