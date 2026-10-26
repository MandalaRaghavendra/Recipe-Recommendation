import os
import json
import hashlib
from PIL import Image

PROJECT_ROOT = "d:/recipie/Recipe-Recommendation"
STATIC_RECIPES_DIR = os.path.join(PROJECT_ROOT, "web-app", "static", "images", "recipes")
DATA_PATH = os.path.join(PROJECT_ROOT, "ai-service", "data.json")

with open(DATA_PATH, "r", encoding="utf-8") as f:
    recipes = json.load(f)

for r in recipes:
    rid = r["recipe_id"]
    p = os.path.join(STATIC_RECIPES_DIR, f"recipe_{rid}.jpg")
    size = os.path.getsize(p)
    im = Image.open(p)
    w, h = im.size
    print(f"[{rid:3d}] {r['cuisine']:12s} | {r['diet']:12s} | {r['recipe_name']:35s} | {w}x{h} | {size}B")
