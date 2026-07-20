from transitions import Machine

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
    { 'trigger': 'key', 'source': 'dialtone', 'dest': 'digits' },
    { 'trigger': 'key', 'source': 'digits', 'dest': 'digits' },
    { 'trigger': 'complete_key', 'source': 'dialtone', 'dest': 'ringing' },
    { 'trigger': 'complete_key', 'source': 'digits', 'dest': 'ringing' },
    { 'trigger': 'done_ringing', 'source': 'ringing', 'dest': 'audio' },
]

dialplan = Machine(
    states=states,
    transitions=transitions,
    initial='onhook')
