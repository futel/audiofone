import sys
from transitions import Machine

import log

states = [
    'onhook',
    'dialtone',
    'busy',
    'digits',
    'ringing',
    'audio']

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
    def log_state(self, event):
        print(event)
        sys.stdout.flush()


# Create the object to become the state machine.
dialplan = Dialplan()

# Attach state machinery to the dialplan object.
_machine = Machine(
    dialplan,
    states=states,
    transitions=transitions,
    before_state_change='log_state',
    send_event=True,
    initial='onhook')

# Treat invalid triggers as no-ops instead of raising MachineError.
# XXX It would be better to check and remove these bugs instead.
_machine.ignore_invalid_triggers = True
