"""
Gets images from /home/bernard/git/timelapse/images

and for each day removes the brightest and darkest, and copies rest into

/home/bernard/git/timelapse/culledimages
"""

import os, shutil
from PIL import Image


def getbrightness(img):
    greyscale = img.convert('L')
    hgram = greyscale.histogram()
    pixels = sum(hgram)
    brightness = scale = len(hgram)

    for index in range(0, scale):
        ratio = hgram[index] / pixels
        brightness += ratio * (-scale + index)

    return 1 if brightness == 255 else brightness / scale


def cull_filelist(filelist, putfiles):
    blist = []
    imlist = []
    for fpath,fname in filelist:
        img = Image.open(fpath)
        imlist.append(img)
        blist.append(getbrightness(img))
    bmax = max(blist)
    bmin = min(blist)
    for index, b in enumerate(blist):
        if b != bmax and b != bmin:
            imlist[index].save(putfiles+filelist[index][1])
    for img in imlist:
        img.close()
    filelist.clear()


if __name__ == '__main__':
    getfiles = os.listdir("/home/bernard/git/timelapse/images")
    putfiles = "/home/bernard/git/timelapse/culledimages/"
    filelist = []
    for filename in getfiles:
        filepath = "/home/bernard/git/timelapse/images/" + filename
        if not os.path.isfile(filepath):
            continue
        if not filelist:
            filelist.append((filepath, filename))
            continue
        lastfile = filelist[-1][1][:14]  # get the filename less the hour part of the name
        if filename[:14] == lastfile:    # this file is on the same day
            filelist.append((filepath, filename))
            continue
        elif len(filelist) != 5:
            # so this filename is not on same day as those in filelist
            # but there are less than five files, so do not cull, just copy
            for fpath,fname in filelist:
                # copy files to putfiles folder
                shutil.copyfile(fpath, putfiles+fname)
            filelist.clear()
            filelist.append((filepath, filename))
            continue
        else:
           # so current file is on a different day to the five files in the filelist
           # cull the filelist
           cull_filelist(filelist, putfiles)
    if filelist:
        if len(filelist) != 5:
            for fpath,fname in filelist:
                # copy files to putfiles folder
                shutil.copyfile(fpath, putfiles+fname)
        else:
            cull_filelist(filelist, putfiles)









