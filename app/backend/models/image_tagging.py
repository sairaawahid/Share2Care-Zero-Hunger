import torch
import torch.nn as nn
import torchvision.transforms as T
from torchvision import models
from PIL import Image
import json
from pathlib import Path

from app.backend.config import IMGNET_LABELS_JSON

# -----------------------------
# Load MobileNetV2 Pretrained
# -----------------------------
_device = torch.device("cpu")

_model = models.mobilenet_v2(pretrained=True)
_model.eval()

# Transformation pipeline (match ImageNet training)
_transform = T.Compose([
    T.Resize(256),
    T.CenterCrop(224),
    T.ToTensor(),
    T.Normalize(mean=[0.485, 0.456, 0.406],
                std=[0.229, 0.224, 0.225]),
])

# -----------------------------
# ImageNet Labels
# -----------------------------
if not Path(IMGNET_LABELS_JSON).exists():
    import urllib.request
    labels_url = "https://raw.githubusercontent.com/pytorch/hub/master/imagenet_classes.txt"
    Path(IMGNET_LABELS_JSON).parent.mkdir(parents=True, exist_ok=True)
    urllib.request.urlretrieve(labels_url, IMGNET_LABELS_JSON)

with open(IMGNET_LABELS_JSON) as f:
    idx_to_label = [line.strip() for line in f.readlines()]

# -----------------------------
# Food Keywords for Filtering
# -----------------------------
FOOD_KEYWORDS = [
    "dish", "food", "drink", "bread", "cake", "pizza", "burger", "sandwich",
    "soup", "noodle", "pasta", "rice", "fruit", "vegetable", "salad",
    "egg", "cheese", "meat", "fish", "chicken", "beef", "pork", "lamb",
    "seafood", "bean", "nut", "potato", "tomato", "carrot", "onion",
    "ice cream", "dessert", "milk", "coffee", "tea", "juice", "bottle"
]

def _is_food_label(label: str) -> bool:
    l = label.lower()
    return any(keyword in l for keyword in FOOD_KEYWORDS)

# -----------------------------
# Main Function
# -----------------------------
def tag_food_image(img: Image.Image, topk: int = 3):
    """Classify a food image using MobileNetV2 and return top-k likely food predictions."""
    try:
        inp = _transform(img).unsqueeze(0).to(_device)
        with torch.no_grad():
            logits = _model(inp)
            probs = torch.nn.functional.softmax(logits[0], dim=0)

        # Get top-N broader set, then filter for food
        top_probs, top_idxs = probs.topk(50)
        results = [(idx_to_label[idx], float(prob)) for idx, prob in zip(top_idxs, top_probs)]

        # Keep only likely food labels
        food_results = [(lbl, prob) for lbl, prob in results if _is_food_label(lbl)]

        # Return top-k food predictions
        if food_results:
            return food_results[:topk]
        else:
            return [("No food detected", 0.0)]
    except Exception as e:
        return [("Error", str(e))]
