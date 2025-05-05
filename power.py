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

   This script starts as a service on boot (run as root), checks if
   the current time is outside the 'on' time of around midday and
   18:00, and if it is outside, it sets the next boot time into the
   RTC and powers off.

   If is inside one of the wakeful times, it waits 5 seconds and tests again.

   Note, all times are obtained with timezone.utc, if using this in other
   timezones, this must be altered accordingly.

   Times take no notice of daylight savings time, so midday will always
   be the timezone midday, not adjusted for DST, and the 18:00 hours
   will therefore change with respect to local time.
   This has the advantage that a cron job, taking photo's at midday
   does not need to worry about DST.


   Loop Testing for ‘Off’ time:

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

print("Starting")

while True:

    timestamp = datetime.now(tz=TIMEZONE)

    # test if current time > 12:05   and < 17:55
    # If so, set on-time to 18:00

    if ((timestamp.hour >= 13 and timestamp.hour < 17) or
        (timestamp.hour == 12 and timestamp.minute > 5) or
        (timestamp.hour == 17 and timestamp.minute < 55)):
        # Set RTC to turn Pi on at 18:00
        evetime = datetime(timestamp.year, timestamp.month, timestamp.day, hour=18, tzinfo=TIMEZONE)
        # evetime in epoch seconds
        epoch = int(evetime.timestamp())
        break

    # test if current time > 18:10 or < 11:50
    # If so, set on-time to the following 11:55

    if (timestamp.hour >= 19 or timestamp.hour < 11 or
        (timestamp.hour == 11 and timestamp.minute < 50) or
        (timestamp.hour == 18 and timestamp.minute > 10)):
        # Set RTC to turn Pi on at 11:55
        midday = datetime(timestamp.year, timestamp.month, timestamp.day, hour=11, minute=55, tzinfo=TIMEZONE)
        if timestamp.hour > 12:
            # get midday of next day
            midday = midday + timedelta(days=1)
        epoch = int(midday.timestamp())
        break

    time.sleep(5)

print(f"Setting wakealarm at epoch {epoch}")

ontime = datetime.fromtimestamp(epoch).strftime('%Y%m%d %H:%M:%S')

print(f"Which is at {ontime} local time")

path = pathlib.Path("/sys/class/rtc/rtc0/wakealarm")
# clear current wakealarm
path.write_bytes(str(0).encode("UTF-8"))
# and write new time
path.write_bytes(str(epoch).encode("UTF-8"))
print("Requesting shutdown")
subprocess.run(["shutdown", "+1"])
print("Shutting Down")
sys.exit(0)
