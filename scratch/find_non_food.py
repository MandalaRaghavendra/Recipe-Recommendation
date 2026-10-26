import json
import os
import torch
import torchvision.models as models
from PIL import Image

PROJECT_ROOT = r"d:\recipie\Recipe-Recommendation"
STATIC_RECIPES_DIR = os.path.join(PROJECT_ROOT, "web-app", "static", "images", "recipes")
DATA_PATH = os.path.join(PROJECT_ROOT, "ai-service", "data.json")

with open(DATA_PATH, "r", encoding="utf-8") as f:
    recipes = json.load(f)

weights = models.MobileNet_V3_Small_Weights.DEFAULT
model = models.mobilenet_v3_small(weights=weights)
model.eval()
preprocess = weights.transforms()
categories = weights.meta["categories"]

# Non-food ImageNet keywords
SUSPICIOUS_CATS = [
    'menu', 'recreational vehicle', 'sea snake', 'apiary', 'banana', 'pencil box', 
    'rotisserie', 'paper towel', 'Petri dish', 'coral fungus', 'terrapin', 'crutch',
    'comic book', 'book jacket', 'carton', 'envelope', 'packet', 'lighter', 'matchstick'
]

flagged = []
for r in recipes:
    rid = r["recipe_id"]
    p = os.path.join(STATIC_RECIPES_DIR, f"recipe_{rid}.jpg")
    img = Image.open(p).convert("RGB")
    batch = preprocess(img).unsqueeze(0)
    with torch.no_grad():
        preds = model(batch).squeeze(0).softmax(0)
        class_id = preds.argmax().item()
        score = preds[class_id].item()
        cat = categories[class_id]
        
    for bad in SUSPICIOUS_CATS:
        if bad in cat:
            flagged.append((rid, r["recipe_name"], cat, score))
            break

print(f"Total flagged non-food images: {len(flagged)}")
for item in flagged:
    print(f"Recipe {item[0]:3d}: {item[1]:40s} -> ImageNet: '{item[2]}' ({item[3]:.2f})")
