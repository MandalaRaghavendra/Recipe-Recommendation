import os
import json
from PIL import Image

PROJECT_ROOT = r"d:\recipie\Recipe-Recommendation"
DATA_PATH = os.path.join(PROJECT_ROOT, "ai-service", "data.json")
STATIC_RECIPES_DIR = os.path.join(PROJECT_ROOT, "web-app", "static", "images", "recipes")

with open(DATA_PATH, "r", encoding="utf-8") as f:
    recipes = json.load(f)

print(f"Loaded {len(recipes)} recipes.")

# Check recipes with potential mismatches or known issues from previous scripts
# Check what each recipe is and its cuisine, veg/nonveg, ingredients
suspicious = []
for r in recipes:
    rid = r["recipe_id"]
    name = r["recipe_name"]
    veg = r.get("veg_nonveg", "").lower()
    cuisine = r.get("cuisine", "")
    img_link = r.get("image_link", "")
    
    # Check if image file exists
    local_filename = f"recipe_{rid}.jpg"
    local_path = os.path.join(STATIC_RECIPES_DIR, local_filename)
    if not os.path.exists(local_path):
        suspicious.append((rid, name, "Image file does not exist on disk!"))
    else:
        sz = os.path.getsize(local_path)
        if sz < 10000:
            suspicious.append((rid, name, f"Image file is very small ({sz} bytes)"))

print(f"File checks: {len(suspicious)} suspicious items")
for s in suspicious:
    print(s)
