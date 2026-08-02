
"Given an image filename, return brightness value"

from PIL import Image


def get_range(x,y):
    "Return a range of x,y values around the given x,y"
    for xx in range(x-20, x+20):
        for yy in range(y-20, y+20):
            yield (xx,yy)


def get_brightness(img, x, y):
    """Returns a value between 0.0 and 1.0, where 1.0 is max brightness
       This is tested around the given x, y point of the image"""

    # Note standard brightness measurements weigh R,G,B differently
    # in particular green is emphasised, but since I am simply comparing
    # two brightness levels I have not bothered

    # its also a bit unknown to me what effect snow would have, so I'm keeping
    # it simple

    brightness = 0
    maxb = 0
    # get a range of x,y values around (x,y)
    for p in get_range(x, y):
        red, green, blue = img.getpixel(p)
        brightness += red+green+blue
        maxb += 255+255+255
    return brightness / maxb

# Open Image with Pillow, and check brightness
with Image.open("images/image_2026072814.jpeg") as img:
    b = get_brightness(img, 3500, 2500)
    print(b)

