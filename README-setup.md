## raspberry pi target box notes

* [sshpass](https://manpages.debian.org/stretch/sshpass/sshpass.1.en.html) so that ansible doesn't cry a lot
* pi network enabled and active
 * on the pi3, run raspi-config and enable+config wifi

# Serial terminal

Sometimes it's preferred just to have a [serial terminal](https://elinux.org/RPi_Serial_Connection),
that you can interact with from another computer via a usb<->serial cable:

```
echo enable_uart=1 >> /boot/config.txt
```

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

