import os
import hashlib
from collections import defaultdict
import glob

STATIC_RECIPES_DIR = "web-app/static/images/recipes"
PROBLEM_RIDS = [
    5, 7, 8, 9, 11, 14, 15, 16, 17, 18, 19, 21, 23, 24, 41, 56, 60, 67, 68, 70,
    71, 75, 78, 80, 81, 82, 83, 85, 86, 89, 94, 95, 103, 105, 106, 107, 108, 109,
    110, 111, 112, 113, 115, 117, 118, 122, 123, 124, 125, 127, 128, 129, 130, 135,
    138, 140, 141, 142, 144, 149, 151, 152, 154, 155, 158, 162, 164, 165, 166, 171,
    183, 185, 189, 192, 194, 196, 198
]

old_dup_hash = "c23f78d9"

files = glob.glob(os.path.join(STATIC_RECIPES_DIR, "recipe_*.jpg"))
total_files = len(files)
unique_hashes = set()
dup_count = 0
still_dup_thali = []

for rid in PROBLEM_RIDS:
    p = os.path.join(STATIC_RECIPES_DIR, f"recipe_{rid}.jpg")
    if os.path.exists(p):
        with open(p, "rb") as f:
            h = hashlib.md5(f.read()).hexdigest()
            if h.startswith(old_dup_hash):
                still_dup_thali.append(rid)

for p in files:
    with open(p, "rb") as f:
        unique_hashes.add(hashlib.md5(f.read()).hexdigest())

print(f"Total recipe files on disk: {total_files}/198")
print(f"Total unique hashes: {len(unique_hashes)}/198")
print(f"Recipes still waiting for download: {len(still_dup_thali)}")
