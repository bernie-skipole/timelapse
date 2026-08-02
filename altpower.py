"""
    From RPi docs, for RPI5, to enable low power mode and wakeup with the Real Time Clock:

    $ sudo -E rpi-eeprom-config --edit

    and edit the following line

    POWER_OFF_ON_HALT=1

    test with

    $ echo +600 | sudo tee /sys/class/rtc/rtc0/wakealarm
    $ sudo halt

    ----------------------------------------------------------------
    For photo taking using usb webcam use fswebcam which needs to be
    installed with apt 
    ----------------------------------------------------------------

   This script starts as a service on boot (run as root).

   Loop:

        If the hour is 10, 11, 12, 13 or 14 and no photo taken yet, then take it.

        If the hour is one of 10, 11, 12, 13 set RTC to turn Pi on at hour plus one 

        If current time is between 14:00 and 17:55:
              Set RTC to turn Pi on at 18:00
              Shut down Pi

        If current time is between 18:10 and 9:50 next day:
               Set RTC to turn Pi on at 9:55
               Shut down Pi

        Otherwise, Wait 5 seconds, continue loop

   Note, all times are obtained with timezone.utc, if using this in other
   timezones, this must be altered accordingly.

   Times take no notice of daylight savings time.

   Note: this script uses the Python imaging library Pillow to measure brightness of
   the image at a specific 'grass' point on the image.

   So this requires pillow to be installed, typically with

   sudo apt update
   sudo apt install python3-pil

 """


import os, sys, time, subprocess, pathlib

from datetime import datetime, timezone, timedelta

from PIL import Image

TIMEZONE = timezone.utc

IMAGES = pathlib.Path("/home/bernard/git/timelapse/images")

# Image pixels the webcam is capable of
CAMXY = "4000x3000"

# Image brightness will be tested by inspecting a block of 40x40 pixels at position TESTX, TESTY
# So these values should be chosen at a static representative point of the image. In my case this
# is a patch of grass
 
TESTX = 3500
TESTY = 2500


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



def takephoto(timestamp):
    """Takes a photo, and places it into the folder given by global variable IMAGES
       the timestamp is used to create the filename
    """

    timestampstring = timestamp.strftime('%Y%m%d%H')

    filepath = IMAGES / f"image_{timestampstring}.jpeg"

    if filepath.exists():
        # This file has already been created
        return

    ## Use fswebcam to take a photo
    #
    #  fswebcam -r 4000x3000 --set "Auto Exposure=Manual Mode" --set "Exposure Time, Absolute=10" --no-banner -D 4 -S 12 --jpeg 95 filepath
    #
    # exposure time is 10 to 5000, so setting it at 10 is a very short time
    #
    # testing on laptop: fswebcam -r 4000x3000 -d /dev/video2 --no-banner -D 2 -S 12 --jpeg 95 filepath
    #
    # Note: my USB webcam takes pictures at 4000x3000 pixels. This value CAMXY and TESTX, TESTY would have to be adapted
    # for other models of webcam. Also the exposure times, set in the string "Exposure Time, Absolute=10" together with the levels
    # of brightness at which the photo is re-taken would have to be adapted by trial and error.
    #
    # Start by taking an initial photo with exposure of 10
    ##

    subprocess.run(["fswebcam", "-r", CAMXY,
                    "--set", "Auto Exposure=Manual Mode",
                    "--set", "Exposure Time, Absolute=10",
                    "--no-banner",
                    "-D", "4", "-S", "12", "--jpeg", "95", str(filepath)])
    time.sleep(5)

    # Open Image with Pillow, and check brightness
    with Image.open(filepath) as img:
        b = get_brightness(img, TESTX, TESTY)

    if b<0.15:
        # very dark photo, retake with 50 exposure

        # rename original file
        os.rename(filepath, IMAGES / f"image_{timestampstring}_orig.jpeg")

        # exposure 50
        subprocess.run(["fswebcam", "-r", CAMXY,
                        "--set", "Auto Exposure=Manual Mode",
                        "--set", f"Exposure Time, Absolute=50",
                        "--no-banner",
                        "-D", "4", "-S", "12", "--jpeg", "95", str(filepath)])

        time.sleep(5)

    elif b<0.20:
        # dark photo, retake with 20 exposure

        # rename original file
        os.rename(filepath, IMAGES / f"image_{timestampstring}_orig.jpeg")

        # exposure 20
        subprocess.run(["fswebcam", "-r", CAMXY,
                        "--set", "Auto Exposure=Manual Mode",
                        "--set", f"Exposure Time, Absolute=20",
                        "--no-banner",
                        "-D", "4", "-S", "12", "--jpeg", "95", str(filepath)])

        time.sleep(5)
    elif b<0.25:
        # fairly dark photo, retake with 15 exposure

        # rename original file
        os.rename(filepath, IMAGES / f"image_{timestampstring}_orig.jpeg")

        # exposure 15
        subprocess.run(["fswebcam", "-r", CAMXY,
                        "--set", "Auto Exposure=Manual Mode",
                        "--set", f"Exposure Time, Absolute=15",
                        "--no-banner",
                        "-D", "4", "-S", "12", "--jpeg", "95", str(filepath)])

        time.sleep(5)




def get_epoch():
    """Checks the time, and if correct calls takephoto.
       Returns epoch in seconds when the pi should next be powered up, this is
       either at 9:55, 10:00, 11:00, 12:00, 13:00, 14:00 or 18:00 depending on which is next.

       If the current hour is 10, 11, 12, 13 or 14, takes photo.
 
       If the hour is one of 10, 11, 12, 13 set RTC to turn Pi on at hour plus one 

       If current time is between 14:00 and 17:55:
              Set RTC to turn Pi on at 18:00
              Shut down Pi

       If current time is between 18:10 and 9:50 next day:
              Set RTC to turn Pi on at 9:55
              Shut down Pi

       Otherwise, Wait 5 seconds, continue loop
    """


    while True:

        timestamp = datetime.now(tz=TIMEZONE)

        if timestamp.hour in (10, 11, 12, 13, 14):
            # Take the photo
            takephoto(timestamp)

        # test for current time, and return next on-time

        for hr in range(10, 14):    # hr is 10, 11, 12, 13
            if (timestamp.hour == hr and timestamp.minute < 55):
                # Set RTC to turn Pi on at hr plus 1
                nexttime = datetime(timestamp.year, timestamp.month, timestamp.day, hour=hr+1, tzinfo=TIMEZONE)
                # next hour in epoch seconds
                epoch = int(nexttime.timestamp())
                return epoch

        if ((timestamp.hour >= 14 and timestamp.hour < 17) or
            (timestamp.hour == 17 and timestamp.minute < 55)):
            # Set RTC to turn Pi on at 18:00
            evetime = datetime(timestamp.year, timestamp.month, timestamp.day, hour=18, tzinfo=TIMEZONE)
            # evetime in epoch seconds
            epoch = int(evetime.timestamp())
            return epoch

        # test if current time > 18:10 or < 9:50
        # If so, set on-time to the following 9:55

        if (timestamp.hour >= 19 or timestamp.hour < 9 or
            (timestamp.hour == 9 and timestamp.minute < 50) or
            (timestamp.hour == 18 and timestamp.minute > 10)):
            # Set RTC to turn Pi on at 9:55
            nexttime = datetime(timestamp.year, timestamp.month, timestamp.day, hour=9, minute=55, tzinfo=TIMEZONE)
            if timestamp.hour >= 18:
                # get next day
                nexttime = nexttime + timedelta(days=1)
            epoch = int(nexttime.timestamp())
            return epoch

        # still on-time, wait 5 seconds and continue
        time.sleep(5)



if __name__ == "__main__":

    # wait four minutes on boot to allow a user to boot the pi, remote connect,
    # and if required stop the shutdown.
    time.sleep(240)

    # After the four minutes, if time is right (10:00, 11:00, 12:00, 13:00, 14:00) this takes photo.
    # Returns the epoch of the next wake up time.
    try:
        epoch = get_epoch()
    except:
        # on any failure, set epoch to 9:55 next day
        timestamp = datetime.now(tz=TIMEZONE) + timedelta(days=1)
        nexttime = datetime(timestamp.year, timestamp.month, timestamp.day, hour=9, minute=55, tzinfo=TIMEZONE)
        epoch = int(nexttime.timestamp())

    # For testing: print a message with the epoch of the next on-time
    # print(f"Setting wakealarm at epoch {epoch}")
    # ontime = datetime.fromtimestamp(epoch).strftime('%Y%m%d %H:%M:%S')
    # print(f"Which is at {ontime}")


    # set the wakeup time into the RTC
    path = pathlib.Path("/sys/class/rtc/rtc0/wakealarm")
    # clear current wakealarm
    path.write_bytes("0".encode("UTF-8"))
    # and write new time
    path.write_bytes(str(epoch).encode("UTF-8"))

    # shutdown after one minute. This is broadcast to any connected user
    # and gives a user the chance to stop it with
    # sudo shutdown -c
    subprocess.run(["shutdown", "+1"])
    sys.exit(0)
