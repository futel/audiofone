# Test locally

## Setup

See "Set up local testing environment" in install.md.

## Run unit tests

```
source venv/bin/activate
pytest test/
```

# Test on pi

## Manual tests

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

## Logs

- /var/log/supervisor/puredata.log
- /var/log/supervisor/audiofone.log

# Local test and development

PD preferences needed when testing on my ubuntu box:
- audio system ALSA
- input/output devices: the 2nd "HD-Audio Generic (hardware)" in the list
