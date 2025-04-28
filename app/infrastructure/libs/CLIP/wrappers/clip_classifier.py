
import torch

from app.infrastructure.libs.CLIP.model import clip


class CLIPClassifier:
    def __init__(self, device="gpu", weights="ViT-L/14.pt"):
        self.device = device   
        self.model, self.preprocess = clip.load(weights, device=self.device)
        
    def infer_scores(self, image, prompts):
        if not torch.is_tensor(image):
            image = self.preprocess(image).unsqueeze(0).to(self.device)
        
        text = clip.tokenize(prompts).to(self.device)
        with torch.no_grad():
            logits_per_image, logits_per_text = self.model(image,
                                                           text)
            probs = logits_per_image.softmax(dim=-1).cpu().numpy()
        # Making list of lists containing class label and score        
        pred_with_class = []
        for prob in probs:
            pred_with_class.append(list(zip(prompts, prob)))
        return pred_with_class

    def select_top_k(self, image, prompts, k=5):
        pred_with_class = self.infer_scores(image, prompts)
        top_k_scores = []
        for score in pred_with_class:
            score = sorted(score, key=lambda x:x[1], reverse=True)
            score = score[:k]
            top_k_scores.append(score)
        return top_k_scores
    
    def predict(self, image, prompts, top_k=1):
        top_k_scores = self.select_top_k(image, prompts, k=top_k)
        all_top_k_scores = []
         # Reverse label and prompt dictionary
        for top_k_score in top_k_scores:
            predicted_classes = []
            # Replace prompt text with its label
            for prompt, score in top_k_score:
                predicted_classes.append((prompt,score))
            all_top_k_scores.append(predicted_classes)
        return all_top_k_scores
    
    def get_preprocessor(self):
        return self.preprocess
 