import json, os, hashlib
from collections import defaultdict
import sys

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding='utf-8')

with open('ai-service/data.json', encoding='utf-8') as f:
    recipes = json.load(f)

img_dir = 'web-app/static/images/recipes'
hash_map = defaultdict(list)
missing = []

for r in recipes:
    rid = r['recipe_id']
    p = os.path.join(img_dir, f'recipe_{rid}.jpg')
    if os.path.exists(p):
        with open(p, 'rb') as f_img:
            h = hashlib.md5(f_img.read()).hexdigest()
            hash_map[h].append(rid)
    else:
        missing.append(rid)

# All recipes sharing duplicate hash:
duplicates = []
for h, rids in hash_map.items():
    if len(rids) > 1:
        duplicates.extend(rids)

print(f"Total duplicate recipes: {len(duplicates)}")
print(f"Missing recipes: {missing}")
print(f"Duplicates list: {sorted(duplicates)}")
