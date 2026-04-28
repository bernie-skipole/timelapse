"""
Normalises images from /home/bernard/git/timelapse/images

and tries to average out changes in exposure to set new images into

/home/bernard/git/timelapse/newimages
"""

import os
from PIL import Image, ImageEnhance


def getbrightness(img):
    "From kmohrf/brightness.py"
    greyscale = img.convert('L')
    hgram = greyscale.histogram()  # a list of pixel counts, one for each pixel value in the source image
    pixels = sum(hgram)
    brightness = scale = len(hgram)   # number of discrete pixel values

    for index in range(0, scale):     # for every hgram 
        ratio = hgram[index] / pixels
        brightness += ratio * (-scale + index)

    return 1 if brightness == 255 else brightness / scale


if __name__ == '__main__':
    getfiles = os.listdir("/home/bernard/git/timelapse/images")
    putfiles = "/home/bernard/git/timelapse/newimages/"
    for filename in getfiles:
        filepath = "/home/bernard/git/timelapse/images/" + filename
        if not os.path.isfile(filepath):
            continue 
        img = Image.open(filepath)
        b = getbrightness(img)
        if b>0.52:
            enhancer = ImageEnhance.Brightness(img)
            img = enhancer.enhance(0.52/b)
        elif b<0.48:
            enhancer = ImageEnhance.Brightness(img)
            img = enhancer.enhance(0.48/b)


        img.save(putfiles+filename)



