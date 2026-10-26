import json
import os
import glob
import sys

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding='utf-8')

PROJECT_ROOT = "d:/recipie/Recipe-Recommendation"
DATA_PATH = os.path.join(PROJECT_ROOT, "ai-service", "data.json")

with open(DATA_PATH, "r", encoding="utf-8") as f:
    recipes = json.load(f)

# Inspect known log mappings:
# We know from logs which titles were downloaded for recipes
print("Analyzing recipes that received non-matching images...")
