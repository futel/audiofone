# audiofone

Stand-alone phone audio interface.

# Have:

raspberry pi
* running [Raspberry Pi OS lite](https://www.raspberrypi.org/software/operating-systems/)
* ssh enabled with default pi/raspberry login
 * can do this by touching ssh file on boot partition:
 * `touch /boot/ssh`

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
