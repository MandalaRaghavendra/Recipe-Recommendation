import os
from PIL import Image

recipes_dir = r"d:\recipie\Recipe-Recommendation\web-app\static\images\recipes"

print("Checking image sizes and aspect ratios:")
count = 0
for i in range(1, 199):
    fn = f"recipe_{i}.jpg"
    p = os.path.join(recipes_dir, fn)
    if os.path.exists(p):
        with Image.open(p) as img:
            w, h = img.size
            # Check if any image is suspiciously tiny or huge
            if w < 200 or h < 200:
                print(f"{fn} is unusually small: {w}x{h}")
            count += 1
    else:
        print(f"Missing {fn}!")
print(f"Verified {count}/198 image files exist.")
