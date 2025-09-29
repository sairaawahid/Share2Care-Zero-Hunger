from typing import List, Tuple
import torch
from torchvision import transforms
from torchvision.models import mobilenet_v3_small, MobileNet_V3_Small_Weights
from PIL import Image
from io import BytesIO

class FoodImageTagger:
    def __init__(self, top_k: int = 3, device: str = "cpu"):
        self.device = device
        weights = MobileNet_V3_Small_Weights.IMAGENET1K_V1
        self.model = mobilenet_v3_small(weights=weights).to(self.device).eval()
        self.preprocess = weights.transforms()
        self.categories = weights.meta["categories"]
        self.top_k = top_k

    def predict(self, img: Image.Image) -> List[Tuple[str, float]]:
        with torch.no_grad():
            batch = self.preprocess(img).unsqueeze(0).to(self.device)
            out = self.model(batch)
            probs = torch.nn.functional.softmax(out[0], dim=0)
            topk = torch.topk(probs, k=self.top_k)
            return [(self.categories[i], float(probs[i])) for i in topk.indices]

def tag_image_bytes(b: bytes, top_k: int = 3) -> List[Tuple[str, float]]:
    img = Image.open(BytesIO(b)).convert("RGB")
    return FoodImageTagger(top_k=top_k, device="cpu").predict(img)
