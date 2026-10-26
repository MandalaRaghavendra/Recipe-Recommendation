import os
import json
import glob
import sys

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding='utf-8')

PROJECT_ROOT = "d:/recipie/Recipe-Recommendation"
DATA_PATH = os.path.join(PROJECT_ROOT, "ai-service", "data.json")

with open(DATA_PATH, "r", encoding="utf-8") as f:
    recipes = json.load(f)

for r in recipes:
    print(f"[{r['recipe_id']:3d}] {r['cuisine']:15s} | {r['diet']:12s} | {r['recipe_name']}")
