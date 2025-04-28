import argparse
import matplotlib.pyplot as plt
import numpy as np

from sklearn.metrics import (ConfusionMatrixDisplay, accuracy_score,
                             confusion_matrix, f1_score, precision_score,
                             recall_score)
from tqdm import tqdm

from app.infrastructure.libs.CLIP.datasets.dataloader import dataset_loader
from app.infrastructure.libs.CLIP.wrappers.clip_classifier import CLIPClassifier


class EvaluateCLIP:
    def __init__(self, device, weights, dir_path, BATCH_SIZE=1):
        self.device = device
        self.clip_classifier = CLIPClassifier(device=device,
                                              weights=weights)

        self.preprocess = self.clip_classifier.get_preprocessor()
        self.lables_to_index, self.batch_loader = dataset_loader(
                                                folder_path=dir_path,
                                                transform=self.preprocess,
                                                BATCH_SIZE=BATCH_SIZE)
    def prediction_post_processing(self, labels, predictions):
        labels_mapping_rev = {v:k.replace('_', ' ').title() 
                              for k, v in self.lables_to_index.items()}
        # Update true labels by replacing index to its label
        labels = [labels_mapping_rev[item] for label in labels
                       for item in label]
        # Flat predicted labels
        predictions = [item[0] for prediction in predictions
                       for items in prediction
                       for item in items]

        return labels, predictions  

    def batch_infer(self):
        predictions = []
        labels = []
        for batch in tqdm(self.batch_loader, position= 0, disable=False):
            batch_prediction = self.clip_classifier.predict(
                                            image=batch[0].to(self.device))
            # True labels
            labels.append(batch[1].tolist())
            # Predictions
            predictions.append(batch_prediction)
        # Post Processing
        labels, predictions = self.prediction_post_processing(
                                                            labels,
                                                            predictions)
        return labels, predictions 

    def compute_metrics(self):
        labels, predictions = self.batch_infer()
        self.accuracy = accuracy_score(labels, predictions)
        self.precision = precision_score(labels, predictions,
                                    average='weighted', zero_division=0)
        self.recall = recall_score(labels, predictions, 
                              average='weighted', zero_division=0)
        self.f1_Score = f1_score(labels, predictions, average='weighted')
        confusion_mat = confusion_matrix(labels, predictions)
        # Display confusion matrix in some good visualization
        labels_mapping = {k.replace('_', ' ').title():v 
                          for k, v in self.lables_to_index.items()}
        cm_display = ConfusionMatrixDisplay(
                                confusion_matrix=confusion_mat,
                                display_labels = list(labels_mapping.keys()))
        # Class wise accuracy
        confusion_mat = confusion_mat.astype('float') / confusion_mat.sum(axis=1)[:, np.newaxis]
        # Setting Precision to 3 decimal points
        precised_class_accuracies = ['%.3f' % accurcy 
                                     for accurcy in confusion_mat.diagonal()]
        # Combine label and its corresponding accuracy
        class_wise_accuracy = list(zip(list(labels_mapping.keys()),
                                       precised_class_accuracies))
        # Sorting class wise accuracy in ascending order
        self.sorted_class_accuracies = sorted(class_wise_accuracy,
                                         key = lambda x: x[1])
        # Plotting Confusion Matrix
        fig, ax = plt.subplots(figsize=(15,15))
        cm_display.plot(ax=ax, xticks_rotation='vertical')
        # Save confusion matrix plot as png 
        plt.savefig(f'confusion_matrix.png')
    
    def print_results(self):
        print('-----------------------------------------------')
        print('Accuracy: ', self.accuracy)
        print('-----------------------------------------------')
        print('Precision: ', self.precision)
        print('-----------------------------------------------')
        print('Recall: ', self.recall)
        print('-----------------------------------------------')
        print('f1 Score: ', self.f1_Score)
        print('-----------------------------------------------')
        print('class_wise_accuracy: ', self.sorted_class_accuracies)
        print('-----------------------------------------------')



if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--dir_path', type=str, help='Path of a data root dir')
    parser.add_argument('--weights', type=str, help='Path of a weights')
    parser.add_argument('--device', default='cpu', choices=['cuda', 'cpu'],
                        help='Device to run computation')
    args = parser.parse_args()

    CLIP_evaluate = EvaluateCLIP(device=args.device, weights=args.weights,
                                 dir_path=args.dir_path)
    # Compute metrics
    CLIP_evaluate.compute_metrics()
    # Print results
    CLIP_evaluate.print_results()

    
        

            
