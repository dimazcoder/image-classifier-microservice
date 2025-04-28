import os
import torch
import numpy as np

from PIL import Image, ImageOps

from app.infrastructure.libs.CLIP.model import clip


class SimilarImagesFinder:
    def __init__(self, device="gpu", weights="weights/ViT-L-14.pt",
                 ref_img_paths='Floor_Plan_images', dissimilar_imgs_path='data/not_floor_plans'):
        self.device = device
        self.model, self.preprocess = clip.load(weights,
                                                device=device)
        self.ref_img_features = self.get_images_feature(ref_img_paths)

        # get features of indoor/outdoor/irrelevent imgs
        self.dissimilar_imgs = self.get_images_feature(dissimilar_imgs_path)

    def get_images_feature(self, ref_image_paths):
        if os.path.isdir(ref_image_paths):
            ref_img_paths = [os.path.join(ref_image_paths, f)
                             for f in os.listdir(ref_image_paths)]
        else:
            ref_img_paths = [ref_image_paths]
        # Make ref images batch
        ref_img_batch = []
        for ref_img_path in ref_img_paths:
            ref_pil_image = Image.open(ref_img_path)
            ref_image = self.preprocess(ref_pil_image).to(self.device)
            ref_img_batch.append(ref_image)
        # Get reference images feature
        with torch.no_grad():
            ref_img_features = self.model.encode_image(torch.stack(ref_img_batch)).float()
            ref_img_features /= ref_img_features.norm(dim=-1, keepdim=True)
        return ref_img_features

    def average(self, scores):
        average_score = np.average(scores)
        return average_score

    def infer_scores(self, query_pil_image):
        with torch.no_grad():
            test_img_features = self.model.encode_image(query_pil_image).float()
        test_img_features /= test_img_features.norm(dim=-1, keepdim=True)
        similarity_score = test_img_features.cpu().numpy() @ self.ref_img_features.cpu().numpy().T

        # find similarity of input image with indoor/outdoor/irrelevent imgs
        dissimilarity_score = test_img_features.cpu().numpy() @ self.dissimilar_imgs.cpu().numpy().T

        return similarity_score, dissimilarity_score

    def convert_to_grayscale(self, pil_image):
        # Convert to gray scale image if not already
        # L mode is for 8 bit pixel, black and white 
        if pil_image.mode != 'L': 
            pil_image = ImageOps.grayscale(pil_image)
        else:
            pil_image = pil_image
        return pil_image 

    def predict(self, query_pil_image):
        # To grayscale
        query_pil_image = self.convert_to_grayscale(query_pil_image)
        # Process pil image
        query_pil_image = self.preprocess(query_pil_image).unsqueeze(0).to(self.device)
        # Get score 
        similarity_score, dissimilarity_score = self.infer_scores(query_pil_image)
        return similarity_score, dissimilarity_score
 
