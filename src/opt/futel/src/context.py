import random
import threading
from transitions import Machine, State

import dialnumbers
from log import log

BUSY_TIMEOUT = 15.0 # seconds

states = [
    State(name='onhook'),
    State(name='dialtone'),
    State(name='busy'),
    #State(name='key_down'),
    State(name='digits'),
    State(name='ringing'),
    State(name='audio')]

transitions = [
    {'trigger': 'hook_up', 'source': 'onhook', 'dest': 'dialtone' },
    {'trigger': 'hook_down', 'source': '*', 'dest': 'onhook' },
    {'trigger': 'dialtone_timeout',
      'source': ['dialtone', 'digits'],
      'dest': 'busy' },
    # Don't change state for keys from these states.
    {'trigger': 'key_press',
     'source': ['onhook', 'busy', 'ringing', 'audio'],
     'dest': None},
    {'trigger': 'key_release',
      'source': ['onhook', 'busy', 'ringing', 'audio'],
      'dest': None},
    {'trigger': 'key_press',
     'source': ['dialtone', 'digits'],
     'dest': 'digits' },
    {'trigger': 'key_release',
      'source': ['dialtone', 'digits'],
      'dest': 'digits',
      'after': 'after_key_release'},
    {'trigger': 'complete_key', 'source': 'dialtone', 'dest': 'ringing' },
    {'trigger': 'complete_key', 'source': 'digits', 'dest': 'ringing' },
    {'trigger': 'done_ringing', 'source': 'ringing', 'dest': 'audio' },
]


class Dialplan(object):
    """Object to run state machine actions."""

    def __init__(self, tones):
        self.tones = tones
        self.busy_timer = None
        self.ring_timer = None
        self.dialed_number = ''

    def log_state(self, event):
        log("before state %s %s %s" % (event.state, event.event, event.args))

    def play_busy(self):
        log("Too long off hook...")
        self.dialtone_timeout()

    def cancel_timers(self):
        self.cancel_busy_timer()
        self.cancel_ring_timer()

    def cancel_busy_timer(self):
        if self.busy_timer is not None:
            self.busy_timer.cancel()
            self.busy_timer = None

    def cancel_ring_timer(self):
        if self.ring_timer is not None:
            self.ring_timer.cancel()
            self.ring_timer = None

    def start_busy_timer(self):
        log("starting busy timer")
        self.cancel_busy_timer()
        # XXX also cancel_timers()
        self.busy_timer = threading.Timer(BUSY_TIMEOUT, self.play_busy)
        self.busy_timer.start()

    def start_ring_timer(self, soundfile):
        log("starting ring timer")
        ring_time = random.randrange(4, 13)
        log("Ring for %d seconds" % (ring_time))
        self.ring_timer = threading.Timer(
            ring_time, lambda: self.play_audio_after_ring(soundfile))
        self.ring_timer.start()

    def play_audio_after_ring(self, soundfile):
        self.done_ringing(soundfile=soundfile)
        self.ring_timer = None

    def on_enter_onhook(self, event):
        self.cancel_timers()
        self.tones.off()

    def on_enter_dialtone(self, event):
        self.dialed_number = ''
        self.tones.dialtone()
        self.start_busy_timer()

    def on_enter_busy(self, event):
        self.tones.off()
        self.tones.busy()

    def on_enter_ringing(self, event):
        soundfile = event.kwargs.get('soundfile')
        self.start_ring_timer(soundfile)

    def on_enter_audio(self, event):
        soundfile = event.kwargs.get('soundfile')
        self.tones.off()
        log("DEBUG: play() %s" %(soundfile))
        self.tones.play_audio(soundfile)

    def on_enter_digits(self, event):
        key = event.kwargs.get('key')
        self.tones.off()
        self.tones.key(key)
        self.cancel_timers()
        self.start_busy_timer()

    def after_key_release(self, event):
        key = event.kwargs.get('key')
        log(">> Key release => %s" %(key))
        self.tones.off()
        # Collect the number and add it to dialed_number.
        self.dialed_number = self.dialed_number + key
        soundfile = dialnumbers.have_number(self.dialed_number)
        if soundfile is dialnumbers.NumberValidity.INVALID_KEY:
            self.dialtone_timeout()
        elif soundfile is dialnumbers.NumberValidity.NOT_PREFIX:
            # XXX This should be a fast busy instead of slow busy.
            self.dialtone_timeout()
        elif soundfile is dialnumbers.NumberValidity.POSSIBLE_PREFIX:
            log("possible soundfile %s" % self.dialed_number)
        else:
            self.start_number_event(soundfile)

    def start_number_event(self, soundfile):
        """
        Enter ringing state, start thread to play soundfile after timer.
        """
        self.tones.ring()
        self.cancel_timers()
        self.complete_key(soundfile=soundfile)


def get_dialplan(tones):
    """Create, set up, and return the object to become the state machine."""
    dialplan = Dialplan(tones)

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

    # Treat invalid triggers as no-ops instead of raising MachineError.
    # XXX It would be better to check and remove these bugs instead.
    # machine.ignore_invalid_triggers = True

    return dialplan
