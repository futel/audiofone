import random
import subprocess
import threading
from transitions import Machine, State

from log import log
from tones import Tones

audio_directory = "/mnt/futel/"

#menu_soundfile = 'for-more-information-contact-the-operator-from-any-fewtel-phone-or-visit-our-website-at-fewtel-dot-net'
menu_filename = '7592868_margarets_monologue.wav'
content_filename = '7592868_margarets_monologue.wav'
silence_filename = 'one_minute_silence.wav'

states = [
    State(name='onhook'),
    State(name='menu'),
    State(name='digits'),
    State(name='audio'),
    State(name='busy')]

transitions = [
    # Play menu on hook up.
    {'trigger': 'hook_up', 'source': 'onhook', 'dest': 'menu'},
    # Stop all audio and timers on hook down.
    {'trigger': 'hook_down', 'source': '*', 'dest': 'onhook' },
    # Don't change state for these internal transitions. Don't call exit or
    # enter callbacks.
    {'trigger': 'key_press',
     'source': ['onhook', 'busy'],
     'dest': None},
    {'trigger': 'key_release',
     'source': ['onhook', 'busy'],
     'dest': None},
    # Play key of key press from menu.
    {'trigger': 'key_press',
     'source': ['menu', 'audio'],
     'dest': 'digits'},
    # Play content after key release.
    {'trigger': 'key_release',
     'source': 'digits',
     'dest': 'audio'},
    # Play busy.
    {'trigger': 'go_busy',
     'source': ['menu', 'audio'],
     'dest': 'busy' }]


class Dialplan(object):
    """Object to run state machine actions."""

    def __init__(self, tones, keypad):
        self.tones = tones
        self.keypad = keypad
        self.audio_process = None

    def log_state(self, event):
        log("before state %s %s %s" % (event.state, event.event, event.args))

    def audio_off(self):
        self.tones.off()
        if self.audio_process:
            self.audio_process.terminate()

    def play_audio(self, filename):
        self.audio_off()
        audio_path = audio_directory + filename
        audio_cmd = ['aplay', audio_path]
        log("play %s" % (audio_path))
        self.audio_process = subprocess.Popen(audio_cmd)

    def on_enter_onhook(self, event):
        self.audio_off()
        # We need to cancel because if the key is pressed and the
        # hook is then pressed, and then the hook is released, the key tone
        # will not be playing. If the key is then released, the key release
        # event will happen, but the user did not hear the tone.
        self.keypad.cancel()

    def on_enter_menu(self, event):
        self.play_audio(menu_filename)
        # Would like to start a nonblocking timer to wait and then
        # self.audio_process.poll() until the audio process is done, then
        # self.go_busy(). Would need to cancel the timer on every state change.

    def on_enter_digits(self, event):
        """ Stop all audio, play key tone. """
        key = event.kwargs.get('key')
        self.audio_off()
        self.tones.key(key)

    def on_enter_audio(self, event):
        key = event.kwargs.get('key')
        log("Key release => %s" %(key))
        self.audio_off()
        self.play_audio(content_filename)

    def on_enter_busy(self, event):
        self.audio_off()
        self.tones.busy()


def get_dialplan(keypad):
    """Create, set up, and return the object to become the state machine."""
    tones = Tones()
    dialplan = Dialplan(tones, keypad)

    # Attach state machinery to the dialplan object. The transitions library
    # adds the trigger methods (hook_down, hook_up, ...) and is_<state>()
    # helpers to the model, not to the Machine, so we return the model.
    machine = Machine(
        dialplan,
        states=states,
        transitions=transitions,
        before_state_change='log_state',
        send_event=True,
        initial='onhook')

    return dialplan
