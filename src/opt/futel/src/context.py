import threading
from transitions import Machine, State

from log import log

BUSY_TIMEOUT = 15.0 # seconds

states = [
    State(name='onhook'),
    State(name='dialtone'),
    State(name='busy'),
    State(name='digits'),
    State(name='ringing'),
    State(name='audio')]

transitions = [
    { 'trigger': 'hook_up', 'source': 'onhook', 'dest': 'dialtone' },
    { 'trigger': 'hook_down', 'source': '*', 'dest': 'onhook' },
    { 'trigger': 'dialtone_timeout',
      'source': ['dialtone', 'digits'],
      'dest': 'busy' },
    { 'trigger': 'key_down',
      'source': ['dialtone', 'digits'],
      'dest': 'digits' },
    { 'trigger': 'key_up',
      'source': ['dialtone', 'digits'],
      'dest': 'digits' },
    # add nop key_down key_up from other states
    { 'trigger': 'complete_key', 'source': 'dialtone', 'dest': 'ringing' },
    { 'trigger': 'complete_key', 'source': 'digits', 'dest': 'ringing' },
    { 'trigger': 'done_ringing', 'source': 'ringing', 'dest': 'audio' },
]


class Dialplan(object):
    """Object to run state machine actions."""

    def __init__(self, tones):
        self.tones = tones
        self.busy_timer = None

    def log_state(self, event):
        log("before state %s %s %s" % (event.state, event.event, event.args))

    def play_busy(self):
        log("Too long off hook...")
        self.dialtone_timeout()

    def cancel_busy_timer(self):
        if self.busy_timer is not None:
            self.busy_timer.cancel()
            self.busy_timer = None

    def start_busy_timer(self):
        log("starting busy timer")
        self.cancel_busy_timer()
        # XXX also cancel_timers()
        self.busy_timer = threading.Timer(BUSY_TIMEOUT, self.play_busy)
        self.busy_timer.start()

    def on_enter_onhook(self, event):
        self.cancel_busy_timer()
        self.tones.off()

    def on_enter_dialtone(self, event):
        self.tones.dialtone()
        self.start_busy_timer()

    def on_enter_busy(self, event):
        self.tones.off()
        self.tones.busy()

    def on_enter_audio(self, event):
        soundfile = event.kwargs.get('soundfile')
        self.tones.off()
        log("DEBUG: play() %s" %(soundfile))
        self.tones.play_audio(soundfile)

    # def on_enter_digits(self, event):
    #     # This is a key release, stop playing tones
    #     self.tones.off()


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
