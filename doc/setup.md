## raspberry pi target box notes

* [sshpass](https://manpages.debian.org/stretch/sshpass/sshpass.1.en.html) so that ansible doesn't cry a lot
* pi network enabled and active
 * on the pi3, run raspi-config and enable+config wifi

# Serial terminal

Sometimes it's preferred just to have a [serial terminal](https://elinux.org/RPi_Serial_Connection), that you can interact with from another computer via a usb<->serial cable from your pc to the pi serial gpio pins.

Add the following 2 lines to config.txt:
  - `enable_uart=1`
  - `dtoverlay=disable-bt`


## dev box notes

 Maybe you don't want to install a bunch of top-level packages to get ansible
 set up across your entire machine.  That's fine, it'll run from a
 virtualenv:

 ```
 $ virtualenv -p python3 ansible-env
 $ source ansible-env/bin/activate
 $ pip install ansible
 ```
Any time you need to run ansible commands now, just source the activate script
mentioned above.

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

## protel 25-pin D

The protel key/hookswitch units have a 25-pin D connector on them.
Can we pin these connections out?

keys:

* key 1 - 11 22
* key 2 - 11 10
* key 3 - 11 13
* key 4 - 12 22
* key 5 - 12 10
* key 6 - 12 13
* key 7 - 25 22
* key 8 - 25 10
* key 9 - 25 13
* key * - 23 22
* key 0 - 23 10
* key # - 23 13
  
row/cols:

* col 1 - pin 22
* col 2 - pin 10
* col 3 - pin 13
* row 1 - pin 11
* row 2 - pin 12
* row 3 - pin 25
* row 4 - pin 23

hookswitch:
* pin 20 8

## protel 15-pin D

I cut the connector off, so this is counted with the red wire
on the ribbon cable being pin 1:

* key 1 - pin  8 11
* key 2 - pin  9 11
* key 3 - pin 15 11
* key 4 - pin  8 13
* key 5 - pin  9 13
* key 6 - pin 15 13
* key 7 - pin  8 14
* key 8 - pin  9 14
* key 9 - pin 15 14
* key * - pin  8 10
* key 0 - pin  9 10?
* key # - pin 15 10

rows/cols:

* col 1 = pin 8
* col 2 = pin 9
* col 3 = pin 15
* row 1 = pin 11
* row 2 = pin 13
* row 3 = pin 14
* row 4 = pin 10

hookswitch:
* pin 4 5

## protel 20 pin male header

seen from the board. pin 1 upper left. pin 11 lower left.

* key 1 - 13 4
* key 2 - 13 14
* key 3 - 13 11
* key 4 - 12 4
* key 5 - 12 14
* key 6 - 12 11
* key 7 - 1 4
* key 8 - 1 14
* key 9 - 1 11
* key * -
* key 0 -
* key # -

rows/cols:

* col 1 = pin 4
* col 2 = pin 14
* col 3 = pin 11
* row 1 = pin 13
* row 2 = pin 12
* row 3 = pin 1
* row 4 = 

# pd patch

Audio is played through pd.  Python just commands it through
OSC (open sound control) messages over local UDP.

listens on port 6066 for osc messages.
Pd is run from supervisord, you can steal the command
from `src/etc/supervisor/conf.d/puredata.conf`.
