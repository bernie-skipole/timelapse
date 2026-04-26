# timelapse
Project to make a mid-day photo taker

Raspberry Pi 5 has a ‘low power’ feature plus a Real Time Clock, which has a ‘wake up’ capability.

Seconds to wake up time can be inserted into a file which is read on going low power (Linux ‘shutdown’ but retaining power to the board). After the given seconds, the board powers up again.

This suggests a time lapse project:

I would like to take a mid-day photo of some apple trees throughout a year, to stitch in a film showing snow on bare trees, spring blossom, leafing up, growing apples, falling leaves.

Due to difficulty of getting power to the garden, I’m using:

Solar panel plus battery with raspberry pi with camera, all boxed up and mounted.

Pi in low-power mode apart from brief mid-day on-time for the photo, plus an evening on-time to give myself a chance to connect and pull down photo’s or do any changes.

power.py set to start on boot (using power.service). This uses fswebcam to take a photo at mid day, and also controls on and off time of the pi.


Current status:

Installed and started in spring 2026, confident that the power budget will be ok through the summer months, not sure abouit winter!
