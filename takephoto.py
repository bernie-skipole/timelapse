

"""

takephoto.py

This will eventually take a photo

Currently creates a file holding a timestamp string

To repeatedly run this at midday, as your own user (in my case bernard)

Type

crontab -e

and create the entry

0 12 * * * /usr/bin/python3 /home/bernard/git/timelapse/takephoto.py > /dev/null 2>&1


The path to the python script should be adjusted to your own script location

Note that the '12' is midday UTC, this should be adjusted with your timezone
offset from UTC to get at midday in your own timezone.

Similarly you may want to adjust the path and 'tc=timezone.utc' arguments below,
which are used to create a file

"""


import pathlib

from datetime import datetime, timezone

folder = pathlib.Path("/home/bernard/git/timelapse/images")

timestamp = datetime.now(tz=timezone.utc)

timestampstring = timestamp.strftime('%Y%m%d_%H_%M_%S')

filename =  f"image_{timestampstring}.txt"

filepath = folder / filename

filepath.write_bytes(timestampstring.encode("UTF-8"))
