"""
Tesscaract Service
status: Uncompleted
https://layout-parser.readthedocs.io/en/latest/notes/modelzoo.html
https://pillow.readthedocs.io/en/stable/handbook/index.html
"""
import cv2
import pytesseract

# Load the image from the file path
image_path = 'pages/page_16.png'
image = cv2.imread(image_path)  # Load image using OpenCV

# Convert the image to grayscale
gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

# Apply thresholding
_, thresholded = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY | cv2.THRESH_OTSU)

# Denoise using Gaussian blur
denoised = cv2.GaussianBlur(thresholded, (3, 3), 0)

# Enhance contrast
clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
enhanced = clahe.apply(denoised)

data = pytesseract.image_to_data(enhanced, output_type=pytesseract.Output.DICT)
text = pytesseract.image_to_string(enhanced)

# Iterate over each detected text block
for i in range(len(data['text'])):
    # Extract bounding box coordinates
    x, y, w, h = int(data['left'][i]), int(data['top'][i]), int(data['width'][i]), int(data['height'][i])

    # Draw bounding box rectangle on the image
    cv2.rectangle(enhanced, (x, y), (x + w, y + h), (0, 255, 0), 2)  # Green rectangle

# Save the modified image with bounding boxes
cv2.imwrite('page_16_with_boxes.jpg', enhanced)

# Print the extracted text
print("Extracted Text:")
print(text)