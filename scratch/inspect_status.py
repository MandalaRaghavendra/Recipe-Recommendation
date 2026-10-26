import json, os, hashlib, glob
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
            hash_map[h].append((rid, r['recipe_name']))
    else:
        missing.append((rid, r['recipe_name']))

print(f"Total recipes: {len(recipes)}")
print(f"Missing images: {len(missing)}")
for rid, name in missing:
    print(f"  Missing: [{rid}] {name}")
print(f"Unique hashes: {len(hash_map)}")
for h, items in hash_map.items():
    if len(items) > 1:
        print(f"\nHash {h[:8]} shared by {len(items)} recipes:")
        for rid, name in items[:10]:
            print(f"  - [{rid}] {name}")
        if len(items) > 10:
            print(f"  ... and {len(items)-10} more")
