# Requirements

- debian trixie or forky or...
  - ansible
  - XXX ansible.posix?
- raspberry pi target box with usb drive
  - XXX sshpass?
- content
  - XXX

# Setup

To be done once.

## Normalize content

See content.md.

## Set up local testing environment

- python3 -m venv venv
- source venv/bin/activate
- pip install -r requirements.txt

## Set up destination hardware

- install Raspberry Pi OS lite on the pi
  - https://www.raspberrypi.org/software/operating-systems/
- enable ssh on the pi with default pi/raspberry login
  - touch /boot/ssh
- format USB drive with VFAT filesystem
- plug USB drive into pi

# Install on destination hardware

- update deploy/hosts for correct pibox ip address
- ansible-playbook -i deploy/hosts playbook.yml
- copy content
  - XXX
- ssh into the box and run alsamixer while doing the tests below
  - aplay /mnt/futel/5852239851.wav
  - have the interface and run them on the real hardware
  - adjust the volume and exit alsamixer
- reboot the pi
  - sudo shutdown -r now
