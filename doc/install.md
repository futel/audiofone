# Prerequisites:

raspberry pi target box
* running [Raspberry Pi OS lite](https://www.raspberrypi.org/software/operating-systems/)
* ssh enabled and accessible with default pi/raspberry login
 * can do this by touching ssh file on boot partition:
 * `touch /boot/ssh`
* mounted USB flash drive
 * see README-config.md

dev box
* debian trixie
* ansible
* ansible.posix
* sshpass

# Install:

* update deploy/hosts for correct pibox ip address
* ansible-playbook -i deploy/hosts playbook.yml
* ssh into the box and run alsamixer while doing the tests below
  * aplay /mnt/futel/5852239851.wav
  * have the interface and run them on the real hardware
  * adjust the volume and exit alsamixer
* reboot the pi
  * sudo shutdown -r now
