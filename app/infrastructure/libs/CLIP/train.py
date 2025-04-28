import argparse
import sys
import os
import torch
import torch.nn as nn
import matplotlib.pyplot as plt

sys.path.append(os.path.abspath(os.path.join(
                os.path.dirname(__file__), 
                os.pardir)
               ))
import clip as clip

from tqdm import tqdm
from torch import optim
from PIL import Image
from sklearn.model_selection import train_test_split
from torch.utils.data import Dataset, DataLoader, random_split

device = "cpu"
if torch.cuda.is_available():
    device = "cuda:1"


class Data(Dataset):
    def __init__(self, root, preprocess=None):
        self.paths = []
        self.texts = []
        self.preprocess = preprocess
        for cls in os.listdir(root):
            label = cls.replace("_", " ")
            path = os.path.join(root, cls)
            for item in os.listdir(path):
                self.paths.append(os.path.join(path, item))
                self.texts.append(label)

    def __len__(self):
        return len(self.paths)
    
    def __getitem__(self, index):
        image_path = self.paths[index]
        text = self.texts[index]

        image = Image.open(image_path)
        if self.preprocess:
            image = self.preprocess(image)
        # print("---zzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzz")
        # print(image_path)
        return image, text

#model        
def convert_models_to_fp32(model): 
    for p in model.parameters(): 
        p.data = p.data.float() 
        p.grad.data = p.grad.data.float()

# Freeze layers
def freeze_layers(model):       
    #named_parameters is a tuple with (parameter name: string, parameters: tensor)
    for name, param in model.parameters():
        param.requires_grad = True

def train(model, train_loader, optimizer, scheduler, loss_img, loss_txt, epochs):
    print("<--------training started-------->")
    i = 0
    for epoch in tqdm(range(epochs)):
        step = 0
        tr_loss = 0
        model.train()
        pbar = tqdm(train_loader, leave=False)
        for batch in pbar:
            step += 1
            optimizer.zero_grad()
            images, texts = batch
            # print(texts)
            images = images.to(device)
            
            texts = clip.tokenize(texts).to(device)
            logits_per_image, logits_per_text = model(images, texts) #model take images, and text tokens as input
            
            # print(logits_per_image, logits_per_text)
            size = logits_per_image.shape[0]
            ground_truth = torch.arange(size).to(device)
            
            l1 = loss_img(logits_per_image,ground_truth)
            l2 = loss_txt(logits_per_text,ground_truth)
            total_loss = (l1 + l2)/2 
            
            # print(l1.item(), l2.item(), total_loss.item())
            total_loss.backward() # updates lr*gradient
            tr_loss += total_loss.item()
            # optimizer.step()
            convert_models_to_fp32(model)
            optimizer.step()
            scheduler.step() #Why this??
            # clip.model.convert_weights(model) # Why this??
            # scheduler.step()
            clip.model.convert_weights(model)
            
            pbar.set_description(f"train batchCE: {total_loss.item()}", refresh=True)
        tr_loss /= step
        print(f"epoch {epoch}, tr_loss {tr_loss}")

def run_sample(model, dataset, index):
    image, text = dataset[index]
    image = image.unsqueeze(0).to(device)
    text = clip.tokenize(text).to(device)
    print(image.shape, text.shape)
    logits_per_image, logits_per_text = model(image, text)
    print(logits_per_image.shape, logits_per_text.shape)
    print(logits_per_image, logits_per_text)

def run_batch(model, loader):
    batch = next(iter(loader))
    images, texts = batch
    images = images.to(device)
    texts = clip.tokenize(texts).to(device)
    logits_per_image, logits_per_text = model(images, texts)
    print(logits_per_image.shape, logits_per_text.shape)
    print(logits_per_image)
    print(logits_per_text)

def main(args):
    model, preprocess = clip.load("ViT-L/14", device=device, jit=False)
    # model = model.to(device)
    # Freeze layers
    # freeze_layers(model)
    train_ds = Data(args.data_dir_path, preprocess)
    train_loader = DataLoader(train_ds, batch_size=args.batch_size, shuffle=True)
    # There are separate loss functions for the image and text.
    loss_img = nn.CrossEntropyLoss()
    loss_txt = nn.CrossEntropyLoss()
    # optimizer = optim.Adam(model.parameters(), lr=5e-5,betas=(0.9,0.98),eps=1e-6,weight_decay=0.2)
    optimizer = optim.Adam(model.parameters(), lr=1e-5)
    scheduler = optim.lr_scheduler.CosineAnnealingLR(optimizer, len(train_loader)*args.epochs)
    # run_sample(model, train_ds, 10)
    # run_batch(model, train_loader)
    # scheduler = optim.lr_scheduler.CosineAnnealingLR(optimizer, len(train_dataloader)*EPOCH)
    train(model, train_loader, optimizer,scheduler, loss_img, loss_txt, args.epochs)
    torch.save(model.state_dict(), "best_style_model.pt")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--data_dir_path", default="test_data",
                        help="It must be a root dir path")
    parser.add_argument("--epochs", type=int, default="100",
                        help="Number of iterations or epochs")
    parser.add_argument("--batch_size", type=int, default="16",
                        help="Batch size to get batch of images")
    args = parser.parse_args()
    main(args)