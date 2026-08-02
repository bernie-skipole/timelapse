
"""Gets images from /home/bernard/git/timelapse/images
   copies just the mid-day images to /home/bernard/git/timelapse/images2
   at the same time adjusting the brightness of those which are too dark.

   Requires environment with pillow"""

import os, shutil

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


def adjust_brightness_gamma(image_path, gamma=0.6, output_path="gamma_corrected.jpg"):
    """
    Brightens midtones and shadows while protecting highlights using gamma correction.
    gamma < 1.0 brightens the image. gamma = 1.0 is unchanged.
    """
    # Open image and convert to RGB
    img = Image.open(image_path).convert("RGB")
    
    # Create a lookup table (LUT) to map old pixel values to new ones
    # This prevents expensive per-pixel loops in Python
    lut = [int(((i / 255.0) ** gamma) * 255) for i in range(256)]
    
    # Apply the LUT to all bands (R, G, B) of the image
    # If your image has an alpha channel (RGBA), only apply to the first 3 channels
    if img.mode == "RGBA":
        r, g, b, a = img.split()
        r = r.point(lut)
        g = g.point(lut)
        b = b.point(lut)
        bright_img = Image.merge("RGBA", (r, g, b, a))
    else:
        bright_img = img.point(lut * 3)
        
    bright_img.save(output_path)


if __name__ == "__main__":

    # point on image where brightness is measured

    TESTX = 3500
    TESTY = 2500

    pathin = "/home/bernard/git/timelapse/images"
    pathout = "/home/bernard/git/timelapse/images2"

    # get list of images ending with 12 just to get the mid - day shots
    images = [img for img in os.listdir(pathin) if img.endswith("12.jpeg")]

    for image in images:

        infile = os.path.join(pathin, image)
        outfile = os.path.join(pathout, image)

        # Open Image with Pillow, and check brightness
        with Image.open(infile) as img:
            b = get_brightness(img, TESTX, TESTY)
            if b<0.1:
                adjust_brightness_gamma(infile, gamma=0.4, output_path=outfile)
                print(f"adjusting {image} with gamma 0.4")
            elif b<0.3:
                adjust_brightness_gamma(infile, gamma=0.6, output_path=outfile)
                print(f"adjusting {image} with gamma 0.6")
            else:
                shutil.copyfile(infile, outfile)
            print(image)
            


    
