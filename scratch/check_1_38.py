import os
import torch
import torchvision.models as models
from PIL import Image

PROJECT_ROOT = r"d:\recipie\Recipe-Recommendation"
STATIC_RECIPES_DIR = os.path.join(PROJECT_ROOT, "web-app", "static", "images", "recipes")

weights = models.MobileNet_V3_Small_Weights.DEFAULT
model = models.mobilenet_v3_small(weights=weights)
model.eval()
preprocess = weights.transforms()
categories = weights.meta["categories"]

for i in range(1, 39):
    p = os.path.join(STATIC_RECIPES_DIR, f"recipe_{i}.jpg")
    img = Image.open(p).convert("RGB")
    batch = preprocess(img).unsqueeze(0)
    with torch.no_grad():
        preds = model(batch).squeeze(0).softmax(0)
        class_id = preds.argmax().item()
        cat = categories[class_id]
        score = preds[class_id].item()
    print(f"Recipe {i:2d}: {cat:25s} ({score:.2f})")
