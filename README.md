# audiofone

Stand-alone phone audio interface.

# Prerequisites:

raspberry pi target box
* running [Raspberry Pi OS lite](https://www.raspberrypi.org/software/operating-systems/)
* ssh enabled and accessible with default pi/raspberry login
 * can do this by touching ssh file on boot partition:
 * `touch /boot/ssh`

dev box
* ansible

# Install:

* update deploy/hosts for correct pibox ip address
* ansible-playbook -i deploy/hosts playbook.yml

# Test on pi:

* /opt/futel/src/audiofone.py
* watch stdout
* short gpio pin 7 to gpio ground
* have a keypad and frob the hookswitch and keys

# Hardware / Pinouts

* GPIO  7 - pin26 - Hookswitch
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
It is run from supervisord, you can steal the command
from `src/etc/supervisor/conf.d/puredata.conf`.

# sound files

Sound files may be placed on a USB stick.  For example, a sound file containing
the sound to play when the user dials 1-800-555-1212 might be:

`18005551212-information-thing.wav`

The naming convention is:

`<number>[-any-suffix].wav`

Where:
* `<number>` is the phone number to dial.  It may not start with zero and may not contain any special digits (no *, #, A, B, C, D).  Do not put dashes in the number.
* after the number you may put an optional hyphen and arbitrary descriptive text.  
The suffix/description should not contain spaces.

Avoid having two files with the same number prefix (behavior is undefined).

## wave format

The `.wav` files must be:
* PCM
* 16-bit little endian (LE)
* 44.1kHz sampling rate
* Mono (preferred) or stereo (if stereo, only the left channel will be played)
