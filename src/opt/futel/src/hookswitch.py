#!/usr/bin/env python3

from gpiozero import Button

import subprocess
import signal
import sys
import time

hookswitch = Button(7)

audio_child = None

PLAY_DIALTONE_CMD = [
    'aplay',
    '/opt/futel/src/dialtone.wav']

def log(line):
    print(line)
    sys.stdout.flush()

def play_dialtone():
    """ Play dialtone if audio child is None. """
    global audio_child
    log("play dialtone")
    terminate_audio()
    if audio_child is None:
        audio_child = subprocess.Popen(PLAY_DIALTONE_CMD)
    else:
        log("audio_child exists")

def terminate_audio():
    """ Stop audio child if not None. """
    global audio_child
    log("terminate audio")
    if audio_child is not None:
        audio_child.terminate()
    else:
        log("no audio child to terminate")
    audio_child = None

hookswitch.when_pressed = play_dialtone
hookswitch.when_released = terminate_audio

signal.pause()
