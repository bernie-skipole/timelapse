from pathlib import Path

import shutil

from PIL import Image


gammabrighten = lambda i: int(((i / 255.0) ** (1.0 / 2.0)) * 255)
gammabrightenabit = lambda i: int(((i / 255.0) ** (1.0 / 1.5)) * 255)


def get_range(x,y):
    "Return a range of x,y values around the iven x,y"
    for xx in range(x-20, x+20):
        for yy in range(y-20, y+20):
            yield (xx,yy)


def get_brightness(img):
    "Returns a value between 0.0 and 1.0, where 1.0 is max brightness"
    brightness = 0
    maxb = 0
    # get a range of x,y values around (3500, 2500)
    for p in get_range(3500, 2500):
        pixel = img.getpixel(p)
        red, green, blue = pixel
        brightness += red+green+blue
        maxb += 255+255+255
    return brightness / maxb


in_path = Path("images")

# Loop through jpeg files inside the 'in' folder
for file_path in in_path.glob('*.jpeg'):
    output_file = Path("out", file_path.name)
    # Open the image
    img = Image.open(file_path)
    b = get_brightness(img)
    if b<0.1:
        corrected_img = img.point(gammabrighten)
        # Save the image to out
        corrected_img.save(output_file, quality=95)
        corrected_img.close()
    elif b<0.2:
        corrected_img = img.point(gammabrightenabit)
        # Save the image to out
        corrected_img.save(output_file, quality=95)
        corrected_img.close()
    else:
        # Save the unaltered image to out
        shutil.copy(file_path, output_file)
    img.close()
    print(file_path.name)


