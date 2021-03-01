# audiofone

Stand-alone phone audio interface.

# Prerequisites:

raspberry pi
* running [Raspberry Pi OS lite](https://www.raspberrypi.org/software/operating-systems/)
* ssh enabled and accessible with default pi/raspberry login
 * can do this by touching ssh file on boot partition:
 * `touch /boot/ssh`
* [sshpass](https://manpages.debian.org/stretch/sshpass/sshpass.1.en.html) so that ansible doesn't cry a lot
* pi network enabled and active
 * on the pi3, run raspi-config and enable+config wifi

 ## ansible on the development host (your laptop)

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

# Serial terminal

Sometimes it's preferred just to have a [serial terminal](https://elinux.org/RPi_Serial_Connection),
that you can interact with from another computer via a usb<->serial cable:

```
echo enable_uart=1 >> /boot/config.txt
```

# Install:

* update deploy/hosts for correct pibox ip address
* ansible-playbook -i deploy/hosts playbook.yml

# Test on pi:

* sudo /opt/futel/src/hookswitch.py
* watch stdout
* short gpio pin 7 to gpio ground

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

listens on port 6066 for osc messages.
There is a run script in the pd directory, but it basically does this:

```
pd -alsa -send "pd dsp 1" -nogui pd/tones.pd
```
