import sys
from transitions import Machine, State

import log

states = [
    State(name='onhook'),
    State(name='dialtone'),
    State(name='busy', on_enter=['enter_busy']),
    State(name='digits'),
    State(name='ringing'),
    State(name='audio')]

transitions = [
    { 'trigger': 'hook_up', 'source': 'onhook', 'dest': 'dialtone' },
    { 'trigger': 'hook_down', 'source': '*', 'dest': 'onhook' },
    { 'trigger': 'dialtone_timeout', 'source': 'dialtone', 'dest': 'busy' },
    { 'trigger': 'dialtone_timeout', 'source': 'digits', 'dest': 'busy' },
    { 'trigger': 'key', 'source': 'dialtone', 'dest': 'digits' },
    { 'trigger': 'key', 'source': 'digits', 'dest': 'digits' },
    { 'trigger': 'complete_key', 'source': 'dialtone', 'dest': 'ringing' },
    { 'trigger': 'complete_key', 'source': 'digits', 'dest': 'ringing' },
    { 'trigger': 'done_ringing', 'source': 'ringing', 'dest': 'audio' },
]


class Dialplan(object):
    """Object to run state machine actions."""
    def __init__(self, tones):
        self.tones = tones

    def log_state(self, event):
        print(event)
        sys.stdout.flush()

    def enter_busy(self, event):
        self.tones.off()
        self.tones.busy()


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
    machine.ignore_invalid_triggers = True

    return dialplan
