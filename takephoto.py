

"""

takephoto.py

This will eventually take a photo

Currently creates a file holding a timestamp string

To repeatedly run this at midday, as user bernard

Type

crontab -e

and create the entry

0 12 * * * /usr/bin/python3 /home/bernard/git/timelapse/takephoto.py > /dev/null 2>&1


"""


import pathlib

from datetime import datetime, timezone

folder = pathlib.Path("/home/bernard/git/timelapse/images")

timestamp = datetime.now(tz=timezone.utc)

timestampstring = timestamp.strftime('%Y%m%d_%H_%M_%S')

filename =  f"image_{timestampstring}.txt"

filepath = folder / filename

filepath.write_bytes(timestampstring.encode("UTF-8"))
