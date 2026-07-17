# Requirements

- debian trixie or forky or...
  - ansible
  - normalize-audio
- raspberry pi target box
  - with usb drive attached
- content
  - see content.md

# Setup

To be done once.

## Set up content

See content.md. Normalize, put sound files on drive, attach drive to pi.

## Set up local testing environment

- python3 -m venv venv
- source venv/bin/activate
- pip install -r requirements.txt

## Test

Run the automated tests, see test.md.

## Set up destination media

- install Raspberry Pi OS lite on the boot media
  - https://www.raspberrypi.org/software/operating-systems/
- enable ssh on the pi with default pi/raspberry login on the boot media
  - https://www.raspberrypi.com/documentation/computers/getting-started.html#manual-ssh-setup
  - touch /ssh on the bootfs partition
  - echo 'pi:$6$kbkDiqxh6zOiT3xc$JRhOaQln5qaL8LZXwQYlQJVrcXlUt5yU0EBvdC5400lYm5r/HWdbA8oHczKNJH270qYGeqiCOHlicS3MDd44G0' > /run/media/karl/bootfs/userconf.txt # where bootfs is mounted on /run/media/karl
  - echo 'pi ALL=(ALL) NOPASSWD: ALL' | sudo tee /run/media/karl/rootfs/etc/sudoers.d/pi

# Install on destination hardware

## Configure for current installation

Connect the pi to the local network. Update deploy/hosts for correct pibox ip address.

## Install

- ansible-playbook -i deploy/hosts playbook.yml
- copy content
  - XXX
- ssh into the box and run alsamixer while doing the tests below
  - aplay /mnt/futel/5852239851.wav
  - have the interface and run them on the real hardware
  - adjust the volume and exit alsamixer
- reboot the pi
  - sudo shutdown -r now

## Test

Run the manual tests, see test.py.

