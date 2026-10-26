import os
import torch
import torchvision.models as models
from torchvision import transforms
from PIL import Image

PROJECT_ROOT = r"d:\recipie\Recipe-Recommendation"
STATIC_RECIPES_DIR = os.path.join(PROJECT_ROOT, "web-app", "static", "images", "recipes")

try:
    weights = models.MobileNet_V3_Small_Weights.DEFAULT
    model = models.mobilenet_v3_small(weights=weights)
    model.eval()
    preprocess = weights.transforms()
    categories = weights.meta["categories"]
    print("Pretrained MobileNet loaded successfully!")
    
    non_food = []
    for i in range(1, 199):
        p = os.path.join(STATIC_RECIPES_DIR, f"recipe_{i}.jpg")
        img = Image.open(p).convert("RGB")
        batch = preprocess(img).unsqueeze(0)
        with torch.no_grad():
            preds = model(batch).squeeze(0).softmax(0)
            class_id = preds.argmax().item()
            score = preds[class_id].item()
            category_name = categories[class_id]
        print(f"Recipe {i:3d}: {category_name:30s} ({score:.2f})")
except Exception as e:
    print(f"Could not run MobileNet: {e}")
