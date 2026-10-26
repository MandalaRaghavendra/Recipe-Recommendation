import os
import hashlib

recipes_dir = r"d:\recipie\Recipe-Recommendation\web-app\static\images\recipes"

test_rids = [25, 26, 27, 28, 44, 58, 79, 88]
for rid in test_rids:
    p = os.path.join(recipes_dir, f"recipe_{rid}.jpg")
    if os.path.exists(p):
        size = os.path.getsize(p)
        with open(p, "rb") as f:
            h = hashlib.md5(f.read()).hexdigest()[:8]
        print(f"Recipe {rid}: size {size} bytes, hash {h}")
    else:
        print(f"Recipe {rid}: MISSING")
