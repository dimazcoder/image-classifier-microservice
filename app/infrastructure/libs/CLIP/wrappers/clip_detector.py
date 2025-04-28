import os
import sys
import time

import numpy as np
import torch
import cv2
import matplotlib.pyplot as plt
from PIL import Image

import models.clip_image_model.CLIP.clip as clip
# import CLIP.clip as clip


clip.clip._MODELS = {
    "ViT-B/32": "https://openaipublic.azureedge.net/clip/models/40d365715913c9da98579312b702a82c18be219cc2a73407c4526f58eba950af/ViT-B-32.pt",
    "ViT-B/16": "https://openaipublic.azureedge.net/clip/models/5806e77cd80f8b59890b7e101eabd078d9fb84e6937f9e85e4ecb61988df416f/ViT-B-16.pt",
    "ViT-L/14": "https://openaipublic.azureedge.net/clip/models/b8cca3fd41ae0c99ba7e8951adf17d267cdb84cd88be6f7c2e0eca1737a03836/ViT-L-14.pt",
    }

def mask_to_bboxes(mask):
    _, binary_mask = cv2.threshold(mask, 50, 255, cv2.THRESH_BINARY)
    
    contours, _ = cv2.findContours(binary_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
    # print(f"Contours are {len(contours)}")
    # cv2.drawContours(vis, contours, -1, (0, 255, 0), 3)
    c = max(contours, key = cv2.contourArea)
    # contours = [c]
    contour_bboxes = [cv2.boundingRect(c) for c in contours]
    return contour_bboxes
    
def relevance_image_to_attention_mask(image_relevance, orig_pil_image, device='cpu'):
    # create heatmap from mask on image
    
    orig_np_image = np.asarray(orig_pil_image)
    dim = int(image_relevance.numel() ** 0.5)
    image_relevance = image_relevance.reshape(1, 1, dim, dim)
    orig_img_h, orig_img_w, _ = orig_np_image.shape
    image_relevance = torch.nn.functional.interpolate(
        image_relevance, size=[orig_img_h, orig_img_w], mode='bilinear'
        )
    # image_relevance = image_relevance.reshape(orig_img_h, orig_img_w).cuda().data.cpu().numpy()
    image_relevance = image_relevance.reshape(orig_img_h, orig_img_w).to(device).data.cpu().numpy()
    image_relevance = (image_relevance - image_relevance.min()) / (image_relevance.max() - image_relevance.min())
    
    mask = (image_relevance* 255).round().astype(np.uint8)
    return mask

class ClipDetector:
    def __init__(
        self,
        device="gpu",
        weight_path="weights/ViT-L-14.pt",
        classes=[
            "air conditioner"
            ]
        ):
        self.device = "cuda" if device=="gpu" else "cpu"
        self.model, self.preprocess = clip.load(weight_path, device=self.device, jit=False)
        self.classes = classes

    def infer_scores(self, pil_image):
        pil_image = self.preprocess(pil_image).unsqueeze(0).to(self.device)
        text = clip.tokenize(self.classes).to(self.device)
        with torch.no_grad():
            logits_per_image, logits_per_text = self.model(pil_image, text)
            probs = logits_per_image.softmax(dim=-1).cpu().numpy()[0]
        scores = {}
        for label, confidence in zip(self.classes, probs):
            scores[label] = confidence
        return scores

    def select_top_k(self, pil_image, k=5):
        scores = self.infer_scores(pil_image)
        scores = sorted(scores.items(), key=lambda x:x[1], reverse=True)
        scores = scores[:k]
        return scores
    
    def predict(self, pil_image, top_k=1):
        scores = self.select_top_k(pil_image, k=top_k)
        predicted_classes = [(label, score) for (label, score) in scores]
        return predicted_classes

    def interpret(self, pil_image, start_layer=-1):
        """Interpret clip model activations"""
        
        image = self.preprocess(pil_image).unsqueeze(0).to(self.device)
        texts = clip.tokenize(self.classes).to(self.device)
        batch_size = texts.shape[0]
        images = image.repeat(batch_size, 1, 1, 1)
        logits_per_image, logits_per_text = self.model(images, texts)
        probs = logits_per_image.softmax(dim=-1).detach().cpu().numpy()[0]
        
        confidence_scores = []
        for label, confidence in zip(self.classes, probs):
            confidence_scores.append((label, confidence))
        
        index = [i for i in range(batch_size)]
        one_hot = np.zeros((logits_per_image.shape[0], logits_per_image.shape[1]), dtype=np.float32)
        one_hot[torch.arange(logits_per_image.shape[0]), index] = 1
        one_hot = torch.from_numpy(one_hot).requires_grad_(True)
        one_hot = torch.sum(one_hot.to(self.device) * logits_per_image)
        self.model.zero_grad()

        image_attn_blocks = list(dict(self.model.visual.transformer.resblocks.named_children()).values())

        if start_layer == -1: 
        # calculate index of last layer 
            start_layer = len(image_attn_blocks) - 1
        
        num_tokens = image_attn_blocks[0].attn_probs.shape[-1]
        R = torch.eye(num_tokens, num_tokens, dtype=image_attn_blocks[0].attn_probs.dtype).to(self.device)
        R = R.unsqueeze(0).expand(batch_size, num_tokens, num_tokens)
        for i, blk in enumerate(image_attn_blocks):
            if i < start_layer:
                continue
            grad = torch.autograd.grad(one_hot, [blk.attn_probs], retain_graph=True)[0].detach()
            cam = blk.attn_probs.detach()
            cam = cam.reshape(-1, cam.shape[-1], cam.shape[-1])
            grad = grad.reshape(-1, grad.shape[-1], grad.shape[-1])
            cam = grad * cam
            cam = cam.reshape(batch_size, -1, cam.shape[-1], cam.shape[-1])
            cam = cam.clamp(min=0).mean(dim=1)
            R = R + torch.bmm(cam, R)
        image_relevance = R[:, 0, 1:]
   
        return image_relevance, confidence_scores
    
    def detect(self, pil_image, top_k=1):
        """Detect objects defined during initilization
        returns:
        detected_bboxes:[(label, confidence, bboxes)]"""
        relevance_images, scores = self.interpret(pil_image)
        detected_bboxes = []
        for i in range(len(self.classes)):
            image_relevance = relevance_images[i]
            mask = relevance_image_to_attention_mask(image_relevance, pil_image, self.device)
            bboxes = mask_to_bboxes(mask)
            label, confidence = scores[i]
            detected_bboxes.append((label, confidence, bboxes))
        # Select top_k objects
        detected_bboxes = sorted(detected_bboxes, key=lambda x:x[1], reverse=True)
        detected_bboxes = detected_bboxes[:top_k]
        return detected_bboxes

if __name__=='__main__':
    print("333333333333")
    print(sys.argv)
    input_path = sys.argv[1]
    output_dir = sys.argv[2]    

    if os.path.isdir(input_path):
        img_paths = [os.path.join(input_path, f) for f in os.listdir(input_path)]
    else:
        img_paths = [input_path]

    for img_path in sorted(img_paths):
        tic = time.time()
        print(img_path)
        pil_image = Image.open(img_path)
        image_name = os.path.basename(img_path)
        model = ClipDetector(
            device="cpu",
            weight_path="ViT-B/32",
            classes=["air conditioner"]
            )
        k = len(model.classes)
        k = 3
        detected_bboxes = model.detect(pil_image)
        toc = time.time()
        print(img_path)
        # print(scores)
        print(detected_bboxes)
        np_image = np.asarray(pil_image)
        np_image = cv2.cvtColor(np_image, cv2.COLOR_RGB2BGR)
        for label, conf, bboxes in detected_bboxes:
        # x,y,w,h = mask_bboxes
            if "not" in label.lower(): continue
            for x,y,w,h in bboxes:
                cv2.rectangle(np_image ,(x,y), (x+w,y+h), (0,255,0), 2)
        cv2.imwrite(f"{output_dir}/{image_name}", np_image)
        print(f"Time taken {toc-tic:.2f} secs")
        print("-------------------------------------------------------")
        print()    
