from io import BytesIO
import os
from PIL import Image, ImageOps
import os

def resize(in_path,size,qualtiy):
    """this function decreases the size of an image"""
    img_file = open(in_path,'rb')
    bytes_img = BytesIO(img_file.read())
    with Image.open(bytes_img) as image:
        image  = ImageOps.exif_transpose(image)
        image = image.resize(size,Image.LANCZOS)
        image.save(in_path,optimize=True,quality=qualtiy)