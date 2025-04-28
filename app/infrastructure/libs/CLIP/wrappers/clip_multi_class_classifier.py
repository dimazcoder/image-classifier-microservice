import argparse
import os
import sys
import time
import torch


sys.path.append(os.path.abspath(os.path.join(
                os.path.dirname(__file__), 
                os.pardir)
               ))
import clip as clip

from tqdm import tqdm
from PIL import Image
from datasets.dataloader import dataset_loader


class ClipClassifier:
    def __init__(
        self,
        device="gpu",
        weight_path="weights/ViT-L-14.pt",
        use_batch_processing = False,
        label_groups=[[
                "Art Deco architecture house",
                # "Contemporary architecture house", 
                # "French architecture house",
                # "Italian architecture house",
                # "Mediterranean architecture house",
                # "Modern architecture house",
                # "Roman architecture house",
                # "Spanish architecture house",
                # "Tudor architecture house",
                # "Victorian architecture house",
                # "Villa",
                # "Bungalow",
                # "Multi Level House",
                # "Century Home",
                # "Farm house",
                # "Art Nouveau architecture house",
                # "Biedermeier architecture house",
                # "Baroque architecture house",
                # "Renaissance architecture house",
                # "Gothic architecture house",
                "Edwardian architecture house"
                ],
                ["Terrace or Deck of a house",
                # "Glass Siding of house",
                # "Flat Roof architecture",
                # "Lift or Elevator",
                "Water Tank",],
                ['A photo of a Basement',
                #  'A photo of a Bathroom',
                #  'A photo of a Bedroom',
                #  'A photo of a Garage',
                #  'A photo of a Garden with flowers and trees',
                #  'A photo of a Gym or persons doing excercise for fitness',
                #  'A photo of a Kitchen',
                #  'A photo of a Living Room',
                #  'A photo of a Office',
                #  'A photo of a Closet or wardrobe or walk in closet or walk in wardrobe',
                #  'A photo of a Swimming Pool',
                #  'A photo of a Game Room',
                #  'A photo of a Dining room or table to eat food',
                #  'A photo of a Cinema Room',
                #  'A photo of a Library building or students studying in the library',
                #  'A photo of a Balcony with potted plants',          
                #  'A photo of a Laundry with washing machines or clothes',
                #  'A photo of a Stylish Loft Design',
                #  'A photo of a Wine Room',
                #  'A photo of a Bar',
                #  'A photo of a Children Room with toys or painting or cars',
                #  'A photo of a Terrace or Patio',
                #  'A photo of a Storage Room',
                 'A photo of a Empty Room']
                ]

        ):
        self.device = "cuda" if device=="gpu" else "cpu"
        self.use_batch_processing = use_batch_processing
        self.pred_with_class = []
        self.model, self.preprocess = clip.load(weight_path, device=self.device)
        self.label_groups = label_groups
        self.ext_list = (".jpg", ".jpeg", ".png", ".ppm", ".bmp", ".pgm", ".tif", ".tiff", ".webp")
    
    def inference(self, pil_image):
        pred_with_class = []
        pred_with_class = self.infer_scores(pil_image, pred_with_class)  
        return pred_with_class
    
    def batch_inference(self, image_batches):
        pred_with_class = []
        true_labels = []
        for batch in tqdm(image_batches, position= 0, disable=False):
            pred_with_class = self.infer_scores(batch[0].to(self.device),
                                           pred_with_class)                         
            true_labels.append(batch[1].tolist())
        self.true_labels = true_labels
        return pred_with_class
    
    # For batch prediction    
    def batch_predict(self, dir_path, top_k=2, batch_size=64):
        self.BATCH_SIZE = batch_size
        labels_mapping, images = dataset_loader(dir_path, self.ext_list,
                                                self.preprocess, batch_size)
        batch_predictions = self.predict(pil_image=images, top_k=top_k)
        return batch_predictions, self.true_labels, labels_mapping

    def infer_scores(self, pil_image, pred_with_class):
        if not self.use_batch_processing:
            pil_img = self.preprocess(pil_image).unsqueeze(0).to(self.device)
        else:
            pil_img = pil_image
        flat_labels = [label for label_group in self.label_groups
                        for label in label_group] 
        text = clip.tokenize(flat_labels).to(self.device)
        with torch.no_grad():
            logits_per_image, logits_per_text = self.model(pil_img, text)
            # print(logits_per_image.squeeze()[3,4,5])
            logits_flat_labels = logits_per_image.squeeze().tolist()
            # Check list of lists
            if self.use_batch_processing:
                if len(logits_flat_labels) == self.BATCH_SIZE:
                    logits_flat_labels = logits_flat_labels
                else:
                    logits_flat_labels = [logits_flat_labels]   
            elif not self.use_batch_processing:  
                logits_flat_labels = [logits_flat_labels]   
            
            all_probs_group = []
            for logits in logits_flat_labels:
                probs_groups = []
                for group in self.label_groups:
                    logits_group = logits[:len(group)]
                    logits_group = torch.Tensor(logits_group)
                    probs_group = logits_group.softmax(dim=-1).tolist()
                    probs_groups.append(probs_group)
                    # Delete the elements of current group so next group elements
                    # are in front of list and can be sliced
                    del logits[:len(group)]
                all_probs_group.append(probs_groups)
                
        # all_images_prob = [] 
        for probs_group in all_probs_group:
            scores = []
            for label_group, probs_group in zip(self.label_groups, probs_group):
                label_probs_group = list(zip(label_group, probs_group))
                scores.append(label_probs_group)
            pred_with_class.append(scores)
        return pred_with_class

    def select_top_k(self, img_paths, k=5):
        if not self.use_batch_processing:
            scores = self.inference(img_paths)
        else:
            scores = self.batch_inference(img_paths)
        all_images_scores = []
        for image_score in scores:
            all_scores = []
            for score in image_score:
                score = sorted(score, key=lambda x:x[1], reverse=True)
                score = score[:k]
                all_scores.append(score)
            all_images_scores.append(all_scores)
        return all_images_scores
    
    def predict(self, pil_image, top_k=1):
        scores = self.select_top_k(pil_image, k=top_k)
        all_predicted_score = []
        for image_score in scores:
            predicted_classes = []
            for label_probs_group in image_score:
                for label, score in label_probs_group:
                    predicted_classes.append((label, score))
            all_predicted_score.append(predicted_classes)
        # predicted_classes = [[(label, score) for label, score in label_probs_group]
        #                         for label_probs_group in scores]
        return all_predicted_score


if __name__=='__main__':    
    parser = argparse.ArgumentParser()
    parser.add_argument("-input_path", default="test_data",
                        help="For batch processing must be root dir path else image paths ")
    parser.add_argument("-use_batch_processing", action='store_true',
                        dest='use_batch_processing', help="Use batch processing")

    args = parser.parse_args()
    BATCH_SIZE = 2

    if not args.use_batch_processing:
        # Read images from a directory or a path
        if os.path.isdir(args.input_path):
            img_paths = [os.path.join(args.input_path, f) for f in os.listdir(args.input_path)]
        else:
            img_paths = [args.input_path]
    else:
        dir_path = [args.input_path]
    # Initialize room type classifier
    clip_classifier = ClipClassifier(device="gpu",
                                    use_batch_processing=args.use_batch_processing)
    tic = time.time()
    if not args.use_batch_processing:
    # 1-by-1 image prediction code
        for img_path in img_paths:
            pil_image = Image.open(img_path)
            predicted_classes = clip_classifier.predict(pil_image, top_k=1)
            print(predicted_classes)
    # Batch Prediction
    else:
        predicted_classes, _, _  = clip_classifier.batch_predict(dir_path, top_k=1, batch_size=BATCH_SIZE)
        print('------------------------------------------------------')
        print(predicted_classes)
        print(len(predicted_classes))
    toc = time.time()
 
    print("-------------------------------------------------------")
    print(f"Time taken {toc-tic:.2f} secs")
    print("-------------------------------------------------------")   
