from transitions import Machine

states = [
    'onhook',
    'dialtone',
    'busy',
    'digits',
    'dialing',
    'ringing',
    'audio']

transitions = [
    { 'trigger': 'hook_up', 'source': 'onhook', 'dest': 'dialtone' },
    { 'trigger': 'hook_down', 'source': '*', 'dest': 'onhook' },
    { 'trigger': 'dialtone_timeout', 'source': 'dialtone', 'dest': 'busy' },
    { 'trigger': 'key', 'source': 'dialtone', 'dest': 'digits' },
    { 'trigger': 'key', 'source': 'digits', 'dest': 'digits' },
    # XXX complete number, invalid number, invalid prefix keeps us in digits
    #{ 'trigger': 'xxx', 'source': 'ringing', 'dest': 'audio' },
]

dialplan = Machine(
    states=states,
    transitions=transitions,
    initial='onhook')
