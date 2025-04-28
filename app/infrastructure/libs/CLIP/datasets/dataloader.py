import torch
from PIL import Image
from torchvision import datasets

EXT_LIST = (".jpg", ".jpeg", ".png", ".ppm", ".bmp",
            ".pgm", ".tif", ".tiff", ".webp")

def loader(path):
    return Image.open(path)

def dataset_loader(folder_path, transform, BATCH_SIZE=64):
    # Read all images from a directory 
    folder_dataset = datasets.DatasetFolder(root=folder_path,
                                            loader=loader,
                                            extensions=EXT_LIST,
                                            transform=transform)
    # Get Class labels and corresponding mapping to index
    class_labels, lables_to_index = folder_dataset.find_classes(folder_path)
    # Make batches of images
    batch_loader = torch.utils.data.DataLoader(folder_dataset,
                                               batch_size=BATCH_SIZE,
                                               shuffle=False,
                                               num_workers=4,
                                               pin_memory=True)
   
    return lables_to_index, batch_loader


  
    
