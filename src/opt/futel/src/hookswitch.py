#!/usr/bin/env python3

import RPi.GPIO as GPIO

# from gpiozero import Button

# import subprocess
# import signal
# import sys

# hookswitch = Button(7)
#
# audio_child = None
#
# PLAY_DIALTONE_CMD = [
#     'aplay',
#     '/opt/futel/src/audio/dialtone.wav']
#
# def log(line):
#     print(line)
#     sys.stdout.flush()
#
# def play_dialtone():
#     """ Play dialtone if audio child is None. """
#     global audio_child
#     log("play dialtone")
#     terminate_audio()
#     if audio_child is None:
#         audio_child = subprocess.Popen(PLAY_DIALTONE_CMD)
#     else:
#         log("audio_child exists")
#
# def terminate_audio():
#     """ Stop audio child if not None. """
#     global audio_child
#     log("terminate audio")
#     if audio_child is not None:
#         audio_child.terminate()
#     else:
#         log("no audio child to terminate")
#     audio_child = None
#
# hookswitch.when_pressed = play_dialtone
# hookswitch.when_released = terminate_audio
#
# signal.pause()

class Hookswitch:
    def __init__(self, on_hook_down, on_hook_up, pin = 26):
        self._on_hook_up = on_hook_up
        self._on_hook_down = on_hook_down
        self._pin = pin

    def run(self):
        GPIO.setup(self._pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)
        def state_changed(channel):
            if(GPIO.input(channel) == 0):
                self._on_hook_up()
            else:
                self._on_hook_down()

        GPIO.add_event_detect(self._pin, GPIO.BOTH, callback=state_changed)
        # GPIO.add_event_detect(self._pin, GPIO.RISING, callback=self._on_hook_down)
        # button = Button(self._pin)
        # button.when_pressed = self._on_hook_up
        # button.when_pressed = self._on_hook_down
