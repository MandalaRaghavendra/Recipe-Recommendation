import json, os, hashlib, glob
from collections import defaultdict
import sys

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding='utf-8')

with open('ai-service/data.json', encoding='utf-8') as f:
    recipes = json.load(f)

img_dir = 'web-app/static/images/recipes'
for r in recipes:
    rid = r['recipe_id']
    p = os.path.join(img_dir, f'recipe_{rid}.jpg')
    exists = os.path.exists(p)
    size = os.path.getsize(p) if exists else 0
    h = hashlib.md5(open(p, 'rb').read()).hexdigest()[:8] if exists else "NONE"
    print(f"[{rid:3d}] Hash:{h} Size:{size:6d}B Name: {r['recipe_name']}")
