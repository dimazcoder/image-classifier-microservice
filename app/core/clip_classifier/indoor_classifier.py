import os
from app.core.config import config
from PIL import Image
import torch
from app.infrastructure.libs.CLIP.wrappers.clip_classifier import CLIPClassifier


class IndoorClassifier:
    def __init__(self, ckpt='trained_weights/ViT-L-14.pt', use_cuda=True) -> None:
        weights = os.path.join(config.static_path, ckpt)
        self.device = 'cuda' if use_cuda and torch.cuda.is_available() else 'cpu'
        self.model = CLIPClassifier(device=self.device, weights=weights)
        self.prompts = {
            'Outdoor': [
                'a photo of an extrior of a house',
                'a photo of a building',
                'a photo of the building',
                'a photo of a sports stadium',
                'a photo of a forest',
                'a photo of a mountain',
                'a photo of a sea',
                'a photo of an airfield',
                'a photo of an amusement park',
                'a photo of an army base',
                'a photo of a soldiers',
                'a photo of an athletic field',
                'a photo of a boat deck',
                'a photo of a boat',
                'a photo of a bus station',
                'a photo of a bus',
                'a photo of a road',
                'a photo of a stadium',
                'a photo of public gatherings',
                'a photo of a crowd of people',
                'a photo of a bullring',
                'a photo of a bull',
                'a photo of airfield',
                'a photo of aeroplane',
                'a photo of an amusement arcade',
                'a photo of a river',
                'a photo of a sky',
                'a photo of grass with sky',
                'a photo of a furnish lawn with grass'],

            'Indoor': [
                'a photo of an interior of room',
                'a photo of a bedroom',
                'a photo the bedroom',
                'a photo of a kitchen'
                'a photo of the kitchen'
                'a photo of a living room'
                'a photo of the living room'
                'a photo of a bathroom'
                'a photo of the bathroom'
                'a photo of a basement',
                'a photo of a hall',
                'a photo of inside of furnish room',
                'a photo of a empty room',
                'a photo of sofas in room',
            ],
            "Irrelevent": [
                "a photo of a graph",
                "a photo of a chart",
                "a photo of an art",
                "a photo of bar plot"
                "a photo of pie plot"
                "text",
                "text in image",
                "a photo contains text",
                "a photo of a map",
                "a photo of a floor plan",
                "a photo of a 3D plan",
                "a photo of a blueprint",
                "an ariel view of a room",
                "an ariel view of a house",
            ]
        }

    def is_valid_size(self, size, valid_size: tuple = (200, 200)):
        if valid_size is not None:
            mW, mH = valid_size
            W, H = size
            if W < mW or H < mH:
                return False
        return True

    def __call__(self, pil_image: Image.Image, min_size: tuple = None):
        if isinstance(pil_image, str):
            pil_image = Image.open(pil_image).convert('RGB')

        if not self.is_valid_size(pil_image.size, valid_size=min_size):
            return []

        result = self.model.predict(image=pil_image,
                                    prompts=self.prompts,
                                    top_k=1)
        return result

    def is_valid_image_class(self, image: Image.Image, min_size: tuple = (200, 200), thresh: float = 0.9, classes=None):
        if classes is None:
            classes = ['Indoor', 'Outdoor']
        result = self(image, min_size=min_size)
        if len(result) > 0:
            cls, score = result[0][0]
            if cls in classes and score > thresh:
                return True
        return False

    def is_indoor_or_outdoor(self, image: Image.Image, min_size: tuple = (200, 200), thresh: float = 0.9):
        return self.is_valid_image_class(
            image, min_size, thresh, classes=['Indoor', 'Outdoor']
        )

    # def is_indoor(self, image: Image.Image,
    #               min_size: tuple = (200, 200),
    #               thresh: float = 0.8):
    #     result = self(image, min_size=min_size)
    #     print(f"predictiction for image {image} result {result}", flush=True)
    #     if len(result) > 0:
    #         cls, score = result[0][0]
    #         if cls == 'Indoor' and score > thresh:
    #             return True
    #     return False