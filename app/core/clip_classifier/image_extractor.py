import numpy as np
from PIL import Image
import torch
import layoutparser as lp


def set_in_image_dim(x1, y1, x2, y2, H, W):
    """
    This function checks where x1 and x2 are in range 0-W and y1 and y2 in range 0-H.
    Args:
        x1 (int): top left corner horizontal dist
        y1 (int): top left corner verticle dist
        x2 (int): bottom right corner horizontal dis
        y2 (int): bottom right corner verticle dist

    Returns:
        x1, y1, x2, y2
    """
    if x1 < 0:
        x1 = 0
    if y1 < 0:
        y1 = 0
    if x2 >= W:
        x2 = W - 1
    if y2 >= H:
        y2 = H - 1
    return x1, y1, x2, y2


class ImageExtractor:
    """
    A class to extract table images from the page image.

    This class parse the whole image of page and detect the tables in
    it. Save the parsed image of page with bounding box around objects
    and all the table images on that page
    """

    def __init__(self, use_cuda: bool = True):
        self.device = 'cuda' if use_cuda and torch.cuda.is_available() else 'cpu'

        self.pl_parser = lp.models.Detectron2LayoutModel('lp://PrimaLayout/mask_rcnn_R_50_FPN_3x/config',
                                                         extra_config=["MODEL.ROI_HEADS.SCORE_THRESH_TEST", 0.9],
                                                         device=self.device)

    def save_tables(self, image, table_blocks, image_path, page_no):
        for i, tb in enumerate(table_blocks):
            x1, y1, x2, y2 = tb.block.coordinates
            x1, y1, x2, y2 = int(x1), int(y1), int(x2), int(y2)
            img = np.zeros_like(image)
            x1, y1, x2, y2 = set_in_image_dim(x1, y1, x2, y2, img.shape[0], img.shape[1])
            img = image[y1:y2, x1:x2, :]
            img = Image.fromarray(img.astype(np.uint8))
            img.save(f"{image_path}/page_{page_no}_t{i + 1}.png")

    def predict(self, img_path, table_path, layout_path, page_no):
        image = Image.open(img_path).convert("RGB")
        layout = self.pl_parser.detect(image)
        layout = lp.Layout([b for b in layout if b.type == 2])
        image = np.array(image)
        H, W, _ = image.shape
        self.save_tables(image, layout, table_path, page_no)

        img = lp.draw_box(image, layout, box_width=4, color_map={0: "red"})
        img.save(f"{layout_path}/page_{page_no}.png")

    def __call__(self, img_path, tables_dir, layout_path, page_no):
        self.predict(img_path, tables_dir, layout_path, page_no)