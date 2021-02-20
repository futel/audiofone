#!/usr/bin/env python2

import RPi.GPIO as GPIO
import datetime
import subprocess
import sys
import time

PIN = 7

GPIO.setmode(GPIO.BCM)          # pin numbering?
GPIO.setup(PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)

def log(line):
    print(line)
    sys.stdout.flush()

def button_callback(channel):
    if GPIO.input(PIN):
        log("rising")         # release switch
    else:
        log("falling")        # contact switch

GPIO.add_event_detect(PIN, GPIO.BOTH, callback=button_callback)

while True:
    log("cycle")
    time.sleep(5)
