import pytesseract
from PIL import Image
import os
import glob


path_to_image = './img/'

def ocr_jpeg_to_text(image_path):
    # Open the image using PIL
    with Image.open(image_path) as img:
        # Convert the image to grayscale
        img = img.convert('L')
        # Use pytesseract to perform OCR on the image
        text = pytesseract.image_to_string(img, lang='eng+rus')
        return text

def get_files_in_directory(path, file_mask):
    path = path + file_mask
    file_list = glob.glob(path)
    return file_list
    

for img in get_files_in_directory(path_to_image, '*.jpg'):
    text = ocr_jpeg_to_text(img)
    needed_row = []
    rows = [r for r in text.split('\n') if not r.isspace() and r]
    
    for row in rows:
        if 'ПОДПИСАНИЕ ДАННЫХ' in row:
            needed_row = rows.index(row) + 1
            #print(text)
        if 'у смо не заполнен код' in row:
            print(row)
    if needed_row and needed_row > 0:
        print(f'{rows[needed_row]} - img: {img}' )
        