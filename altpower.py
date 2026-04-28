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

        If the hour is 12, and no photo taken yet, then take it.

        If current time is between 12:00 and 17:55:
              Set RTC to turn Pi on at 18:00
              Shut down Pi

        If current time is between 18:10 and 11:50 next day:
               Set RTC to turn Pi on at 11:55
               Shut down Pi

        Otherwise, Wait 5 seconds, continue loop

   Note, all times are obtained with timezone.utc, if using this in other
   timezones, this must be altered accordingly.

   Times take no notice of daylight savings time, so midday will always
   be the timezone midday, not adjusted for DST, and the 18:00 hours
   will therefore change with respect to local time.

 """


import sys, time, subprocess, pathlib, os

from datetime import datetime, timezone, timedelta

from PIL import Image, ImageEnhance




TIMEZONE = timezone.utc

IMAGES = pathlib.Path("/home/bernard/git/timelapse/images")


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


def takephoto(timestamp):
    """Takes a photo, and places it into the folder given by global variable IMAGES
       the timestamp is used to create the filename
    """

    timestampstring = timestamp.strftime('%Y%m%d%H')

    filename =  f"image_{timestampstring}.jpeg"

    filepath = IMAGES / filename

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
    ##

    subprocess.run(["fswebcam", "-r", "4000x3000",
                    "--set", "Auto Exposure=Manual Mode",
                    "--set", "Exposure Time, Absolute=10",
                    "--no-banner",
                    "-D", "4", "-S", "12", "--jpeg", "95", str(filepath)])

    img = Image.open(str(filepath))
    b = getbrightness(img)
    if b>0.58:
        # remove file and take again with shorter exposure
        os.remove(filepath)
        subprocess.run(["fswebcam", "-r", "4000x3000",
                        "--set", "Auto Exposure=Manual Mode",
                        "--set", "Exposure Time, Absolute=9",
                        "--no-banner",
                        "-D", "4", "-S", "12", "--jpeg", "95", str(filepath)])
    if b<0.42:
        # remove file and take again with longer exposure
        os.remove(filepath)
        subprocess.run(["fswebcam", "-r", "4000x3000",
                        "--set", "Auto Exposure=Manual Mode",
                        "--set", "Exposure Time, Absolute=11",
                        "--no-banner",
                        "-D", "4", "-S", "12", "--jpeg", "95", str(filepath)])
    img.close()






def get_epoch():
    """Returns epoch in seconds when the pi should next be powered up, this is
       either at 11:55 or 18:00 depending on which is next.

       If the current hour is 12, takes photo.
       If the current time is between 12:00 and 17:55, set epoch to 18:00, return
       If current time > 18:10 or < 11:50, set epoch to the following 11:55, return

       If none of the above, wait five seconds and test again. This ensures the pi
       is on and available for remote connection between 18:00 and 18:10.
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

    print("Starting")

    # wait four minutes on boot to allow a user to boot the pi, remote connect,
    # and if required stop the shutdown.
    time.sleep(240)

    # After the four minutes, if time is right (10:00, 11:00, 12:00, 13:00, 14:00) this takes photo.
    # Returns the epoch of the next wake up time.
    epoch = get_epoch()

    # print a message with the epoch of the next on-time
    print(f"Setting wakealarm at epoch {epoch}")
    ontime = datetime.fromtimestamp(epoch).strftime('%Y%m%d %H:%M:%S')
    print(f"Which is at {ontime} local time")

    # set the wakeup time into the RTC
    path = pathlib.Path("/sys/class/rtc/rtc0/wakealarm")
    # clear current wakealarm
    path.write_bytes("0".encode("UTF-8"))
    # and write new time
    path.write_bytes(str(epoch).encode("UTF-8"))

    # shutdown after one minute. This is broadcast to any connected user
    # and gives a user the chance to stop it with
    # sudo shutdown -c
    print("Requesting shutdown")
    subprocess.run(["shutdown", "+1"])
    sys.exit(0)
