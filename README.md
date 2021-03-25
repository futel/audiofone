# audiofone

Stand-alone phone audio interface.

# Prerequisites:

raspberry pi target box
* running [Raspberry Pi OS lite](https://www.raspberrypi.org/software/operating-systems/)
* ssh enabled and accessible with default pi/raspberry login
 * can do this by touching ssh file on boot partition:
 * `touch /boot/ssh`
USB flash drive mounted on pi
* see README-config.md

dev box
* ansible

# Install:

* update deploy/hosts for correct pibox ip address
* ansible-playbook -i deploy/hosts playbook.yml
* ssh into the box and run alsamixer while doing the tests below
  * adjust the volume and exit alsamixer.
  * reboot the pi with `sudo shutdown -r now`

# Test on pi:

On boot, supervisord will launch the main audiofone.py app and
puredata.

* ensure sd card and USB stick are inserted
* plug in power
* wait about 15-20 seconds for the pi to boot and mount the usb stick
* lift handset, you should hear dialtone
  * if you do not, hear a dialtone, you probably didn't wait long enough after boot. Replace the hookswitch and wait a bit longer and then try again.
* dial one of the numbers of a wav file on the usb stick. You should hear ringing and then audio
* hang up, lift the receiver, do nothing, verify you hear a busy after 15 seconds
* hang up, dial an invalid number, verify that you hear a fast busy after the first invalid keypress
* run alsamixer and verify that your preferred volume persists across reboots

Logs are in `/var/log/supervisor/puredata.log` and `/var/log/supervisor/audiofone.log`.

# Hardware / Pinouts

* GPIO  7 - pin26 - Hookswitch (other side to ground pin)
* GPIO 17 - pin11 - Input - keypad col 0
* GPIO 27 - pin13 - Input - keypad col 1
* GPIO 22 - pin15 - Input - keypad col 2
* GPIO 12 - pin32 - Output - keypad row 0
* GPIO 16 - pin36 - Output - keypad row 1
* GPIO 20 - pin38 - Output - keypad row 2
* GPIO 21 - pin40 - Output - keypad row 3
* headphone jack -> earpiece audio

# pd patch

Audio is played through pd.  Python just commands it through
OSC (open sound control) messages over local UDP.

listens on port 6066 for osc messages.
Pd is run from supervisord, you can steal the command
from `src/etc/supervisor/conf.d/puredata.conf`.

# normalizing audio

You can use the `normalize-audio` utility to normalize the volume of the audio files.
Warning: this will destructively modify the files in-place (keep a copy as originals prior to doing this).

```
sudo apt update && sudo apt install normalize-audio
normalize-audio *.wav

```
