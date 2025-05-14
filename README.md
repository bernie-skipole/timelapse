# timelapse
Project to make a mid-day photo taker

Raspberry Pi 5 has a ‘low power’ feature plus a Real Time Clock, which has a ‘wake up’ capability.

Seconds to wake up time can be inserted into a file which is read on going low power (Linux ‘shutdown’ but retaining power to the board). After the given seconds, the board powers up again.

This suggests a time lapse project:

I would like to take a mid-day photo of some apple trees throughout a year, to stitch in a film showing snow on bare trees, spring blossom, leafing up, growing apples, falling leaves.

Due to difficulty of getting power to the garden, I’m thinking of:

Solar panel plus battery with raspberry pi with camera, all boxed up and mounted.

Pi in low-power mode apart from brief mid-day on-time for the photo, plus an evening on-time to give myself a chance to connect and pull down photo’s or do any changes.


Current status:

writing and testing code to wake around 12:00 to take a photo, and 18:00 each day for ten minutes.

To consider:

Solar panel, battery, power management.

I should be able to get wifi to garden, but may need an external antenna.

Which camera, and its protection: glass covering or naked lens.

The physical box and mount.

RTC battery
