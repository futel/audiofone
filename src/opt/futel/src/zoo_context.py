"""
Dialplan for a simple menu.
"""

import random
import subprocess
import threading
from transitions import Machine, State

from log import log
import menu
import tones

audio_directory = "/opt/futel/audio/zoo/"

menu_filename = 'menu.json'
menu_plan = menu.get_menus(menu_filename)


#menu_soundfile = 'for-more-information-contact-the-operator-from-any-fewtel-phone-or-visit-our-website-at-fewtel-dot-net'
#content_filename = '7592868_margarets_monologue.wav'

states = [
    State(name='onhook'),
    State(name='digits'),
    State(name='audio'),
    State(name='busy')]

transitions = [
    # Play first audio on hook up.
    {'trigger': 'hook_up', 'source': 'onhook', 'dest': 'audio'},
    # Stop all audio and timers, reset digits, on hook down.
    {'trigger': 'hook_down', 'source': '*', 'dest': 'onhook' },
    # Don't change state for these internal transitions. Don't call exit or
    # enter callbacks.
    {'trigger': 'key_press',
     'source': ['onhook', 'busy'],
     'dest': None},
    {'trigger': 'key_release',
     'source': ['onhook', 'busy'],
     'dest': None},
    # Play key of key press from audio.
    {'trigger': 'key_press',
     'source': 'audio',
     'dest': 'digits'},
    # Stop key audio, append digit, play content after key release.
    {'trigger': 'key_release',
     'source': 'digits',
     'dest': 'audio'},
    # Play busy.
    {'trigger': 'go_busy',
     'source': 'audio',
     'dest': 'busy' }]


class Dialplan(object):
    """Object to run state machine actions."""

    def __init__(self, tone_player, keypad):
        self.tone_player = tone_player
        self.keypad = keypad
        self.audio_process = None
        self.digit_sequence = []

    def log_state(self, event):
        log("before state %s %s %s" % (event.state, event.event, event.args))

    def audio_off(self):
        self.tone_player.off()
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
        self.digit_sequence = []

    def on_enter_digits(self, event):
        """Stop all audio, play key tone."""
        key = event.kwargs.get('key')
        self.audio_off()
        self.tone_player.key(key)

    def key_to_digit(self, key):
        """Return digit corresponding to key, or None."""
        try:
            return int(key)
        except (TypeError, ValueError):
            return None         # We ignore missing or non-digit keys.

    def on_enter_audio(self, event):
        """Stop key audio, append digit, play content after key release."""
        key = event.kwargs.get('key')
        log("Key release %s" %(key))

        digit = self.key_to_digit(key)
        content_name = None
        if digit is not None:
            # The user entered a usable key, is it valid?
            #self.digit_sequence.append(digit)
            digit_sequence = self.digit_sequence + [digit]
            content_name = menu.get_content_name(digit_sequence, menu_plan)
            if content_name:
                # Valid key, update the stored history.
                self.digit_sequence = self.digit_sequence + [digit]
        if not content_name:
            # We didn't get a valid key, use the current content to replay it
            # and don't update the digit history/
            content_name = menu.get_content_name(self.digit_sequence, menu_plan)

        self.audio_off()
        self.play_audio(content_name)
        # We would like to repeat the audio a few times and then play a
        # busy signal.
        # Could do this by starting a nonblocking timer to periodically
        # self.audio_process.poll() until the audio process is done, then
        # do the next step of repeat or busy, then iterate.
        # Would need to cancel the timer on every state change.
        # Q&D way to do this is to just have the menu audio include 5 repeats
        # and then a long busy signal.

    def on_enter_busy(self, event):
        """Stop all audio, play busy."""
        self.audio_off()
        self.tone_player.busy()


def get_dialplan(keypad):
    """Create, set up, and return the object to become the state machine."""
    tone_player = tones.Tones()
    dialplan = Dialplan(tone_player, keypad)

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
