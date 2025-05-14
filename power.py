"""
    From RPi docs, to enable wakeup with the Real Time Clock :

    $ sudo -E rpi-eeprom-config --edit

    and add the following lines

    POWER_OFF_ON_HALT=1
    WAKE_ON_GPIO=0

    test with

    $ echo +600 | sudo tee /sys/class/rtc/rtc0/wakealarm
    $ sudo halt

    ----------------------------------------------------------------
    For photo taking, see
    https://datasheets.raspberrypi.com/camera/picamera2-manual.pdf
    ----------------------------------------------------------------

   This script starts as a service on boot (run as root).

   If the hour is 12, take photo, and set
   the next on time to 18:00 and power off.
   Checks if the current time is outside the 'on' time of around
   ten minutes around 18:00, and if it is outside, it sets the next boot
   time into the RTC and powers off.

   If is inside the on time, it waits 5 seconds and tests again.

   Note, all times are obtained with timezone.utc, if using this in other
   timezones, this must be altered accordingly.

   Times take no notice of daylight savings time, so midday will always
   be the timezone midday, not adjusted for DST, and the 18:00 hours
   will therefore change with respect to local time.

   Loop:

        If the hour is 12, and no photo taken yet, then take it, shut down.

        If current time is between 12:05 and 17:55:
              Set RTC to turn Pi on at 18:00
              Shut down Pi

        If current time is between 18:10 and 11:50 next day:
               Set RTC to turn Pi on at 11:55
               Shut down Pi

        Otherwise, Wait 5 seconds, continue loop
 """


import sys, time, subprocess, pathlib

from datetime import datetime, timezone, timedelta

TIMEZONE = timezone.utc

IMAGES = pathlib.Path("/home/bernard/git/timelapse/images")


def takephoto(timestamp):
    """Takes a photo, and places it into the folder given by global variable IMAGES
       the timestamp is used to create the filename
    """

    timestampstring = timestamp.strftime('%Y%m%d')

    filename =  f"image_{timestampstring}.txt"

    filepath = IMAGES / filename

    if filepath.exists():
        # This file has already been created
        return

    # Note, currently a timestamp is saved rather than a photo
    filepath.write_bytes(timestamp.strftime('%Y%m%d_%H_%M_%S').encode("UTF-8"))


def get_epoch():
    """If the current time is between 11:50 and 12:05, wait, takes photo at 12:00
       If the current time is between 17:55 and 18:10, wait.
       Returns epoch in seconds when the pi should next be powered up, this is
       either at 11:55 or 18:00 depending on which is next.
    """


    while True:

        timestamp = datetime.now(tz=TIMEZONE)

        if timestamp.hour == 12:
            # If the hour hits 12, take the photo
            takephoto(timestamp)
            # Set RTC to turn Pi on at 18:00
            evetime = datetime(timestamp.year, timestamp.month, timestamp.day, hour=18, tzinfo=TIMEZONE)
            # evetime in epoch seconds
            epoch = int(evetime.timestamp())
            return epoch

        # test if current time >= 12:00   and < 17:55
        # If so, set on-time to 18:00

        if ((timestamp.hour >= 12 and timestamp.hour < 17) or
            (timestamp.hour == 17 and timestamp.minute < 55)):
            # Set RTC to turn Pi on at 18:00
            evetime = datetime(timestamp.year, timestamp.month, timestamp.day, hour=18, tzinfo=TIMEZONE)
            # evetime in epoch seconds
            epoch = int(evetime.timestamp())
            return epoch

        # test if current time > 18:10 or < 11:50
        # If so, set on-time to the following 11:55

        if (timestamp.hour >= 19 or timestamp.hour < 11 or
            (timestamp.hour == 11 and timestamp.minute < 50) or
            (timestamp.hour == 18 and timestamp.minute > 10)):
            # Set RTC to turn Pi on at 11:55
            midday = datetime(timestamp.year, timestamp.month, timestamp.day, hour=11, minute=55, tzinfo=TIMEZONE)
            if timestamp.hour >= 18:
                # get midday of next day
                midday = midday + timedelta(days=1)
            epoch = int(midday.timestamp())
            return epoch

        # still on-time, wait 5 seconds and continue
        time.sleep(5)



if __name__ == "__main__":

    print("Starting")

    # wait four minutes on boot to allow a user to boot the pi, remote connect,
    # and if required stop the shutdown.
    time.sleep(240)

    # After the four minutes, if time is right (12:00 midday) this takes photo and returns with the epoch of 18:00
    # If the current time is 'on-time' within the ten minutes after 18:00 it waits until 'off-time' then returns
    # the epoch of next wake up time at 11:55 the next day.
    # This on-time around 18:00 gives a remote user a chance to connect if required.
    # If the current time is already an 'off-time', it returns immediately with the epoch of
    # next wake up time.
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
