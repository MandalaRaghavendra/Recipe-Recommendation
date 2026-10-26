import json, os, hashlib
import sys

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding='utf-8')

with open('ai-service/data.json', encoding='utf-8') as f:
    recipes = json.load(f)

img_dir = 'web-app/static/images/recipes'
non_dup_rids = []
problem_set = {5, 7, 9, 11, 14, 15, 16, 17, 18, 19, 21, 23, 24, 41, 56, 60, 67, 68, 70, 71, 75, 78, 80, 81, 82, 83, 85, 86, 89, 94, 95, 103, 105, 106, 107, 108, 109, 110, 111, 112, 113, 115, 117, 118, 122, 123, 124, 125, 127, 128, 129, 130, 135, 138, 140, 141, 142, 144, 149, 151, 152, 154, 155, 158, 162, 164, 165, 166, 171, 183, 185, 189, 192, 194, 196, 198, 8}

for r in recipes:
    if r['recipe_id'] not in problem_set:
        print(f"[{r['recipe_id']:3d}] {r['recipe_name']}")
