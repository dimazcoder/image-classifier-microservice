import glob
import os.path as osp
import pathlib

import numpy as np
from PIL import Image
from pytorch_lightning import LightningDataModule
from torch.utils.data import DataLoader, Dataset, Subset
from transformers import ViTFeatureExtractor
from torchvision import transforms
from torchvision.datasets import ImageFolder
from sklearn.model_selection import train_test_split


class DocDataset(Dataset):
    def __init__(self, dataset, transforms=None, transforms_tensor=None):
        self.dataset = dataset
        self.transforms = transforms
        self.transforms_tensor = transforms_tensor
        self.feature_extractor = ViTFeatureExtractor.from_pretrained(
            'google/vit-base-patch16-224-in21k'
        )
        
    def process_img(self, img: Image):
        processed_img = self.feature_extractor(img, return_tensors="pt")
        return processed_img["pixel_values"][0]
        
    def __len__(self):
        return len(self.dataset)
    
    def __getitem__(self, index):
        img, label = self.dataset[index]
        if self.transforms is not None:
            img = self.transforms(img)
        img = self.process_img(img)
        if self.transforms_tensor is not None:
            img = self.transforms_tensor(img)
        return img, label
        
class DocDataModule(LightningDataModule):
    def __init__(self, base_path="./data", 
                 train_batch_size=32, eval_batch_size=64,
                 train_size=0.75, num_workers=3, seed=21
                ):
        self.train_batch_size = train_batch_size
        self.eval_batch_size = eval_batch_size
        self.num_workers = num_workers
        # self.train_size = train_size
        self.seed = seed
        self.train_size = train_size
        self.dataset_full = ImageFolder(base_path)
        self.prepare_data_per_node = True
        
    def setup(self, stage=None):
        indices = range(len(self.dataset_full))
        train_inds, eval_inds, _, eval_targets = train_test_split(
            indices, 
            self.dataset_full.targets,
            train_size=self.train_size, 
            stratify=self.dataset_full.targets,
            random_state=self.seed
        )
        test_size = (len(self.dataset_full) - len(train_inds)) // 2
        val_inds, test_inds = train_test_split(
            eval_inds,
            test_size=test_size,
            stratify=eval_targets,
            random_state=self.seed
        )
        
        train_transforms = transforms.Compose([
            transforms.TrivialAugmentWide(),
            # transforms.RandomRotation(degrees=90),
            # transforms.RandomRotation(degrees=270),
            transforms.RandomInvert(p=0.3),
            transforms.RandomAdjustSharpness(0, p=0.3),
            transforms.RandomAffine(degrees=180, scale=(0.8, 1)),
        ])
        
        train_transforms_tensor = transforms.Compose([
            transforms.RandomErasing(p=0.1)    
        ])
        
        self.train = Subset(self.dataset_full, train_inds)
        self.train = DocDataset(self.train, transforms=train_transforms,
                        transforms_tensor=train_transforms_tensor
                    )
        self.val = Subset(self.dataset_full, val_inds)
        self.val = DocDataset(self.val)
        self.test = Subset(self.dataset_full, test_inds)
        self.test = DocDataset(self.test)
        print(f"Size of train: {len(self.train)}")
        print(f"Size of val: {len(self.val)}")
        print(f"Size of test: {len(self.test)}")
        
    def train_dataloader(self):
        return DataLoader(
            self.train, 
            batch_size=self.train_batch_size, 
            shuffle=True,
            num_workers=self.num_workers, 
            pin_memory=True, 
        )
        
    def val_dataloader(self):
        return DataLoader(
            self.val,
            num_workers=self.num_workers,
            pin_memory=True,
            batch_size=self.eval_batch_size
        )
                
    def test_dataloader(self):
        return DataLoader(
            self.test,
            num_workers=self.num_workers,
            batch_size=self.eval_batch_size
        )        
        
        
if __name__ == "__main__":
    base_path = "/home/nash/Desktop/projects/room_type_classification/data/train"    
    data = DocDataModule(base_path=base_path, train_batch_size=64, train_size=0.8)
    data.setup()
    tra = data.train_dataloader()
    pass
    for t, l in tra:
        print(t.shape, l)
        break
    pass
    print(data.dataset_full.classes)
    print(data.dataset_full.class_to_idx)