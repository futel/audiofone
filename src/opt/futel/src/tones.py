import time
from pythonosc import udp_client

# netreceive port in the audiofone.pd patch
NETRECEIVE_PORT = 6066

# The path seperator format for the messages is for osc, puredata gets the whole
# thing.


class Tones:
    """
    Send messages to the puredata audiofone patch with a UDP client.
    For causing the patch to start or stop playing sounds.
    """
    def __init__(self, host='127.0.0.1', port=NETRECEIVE_PORT):
        self.client = udp_client.SimpleUDPClient(host, port)

    def dialtone(self):
        self.client.send_message('/dialtone', '')

    def off(self):
        self.client.send_message('/off', '')

    def busy(self):
        self.client.send_message('/busy', '')

    def fast_busy(self):
        self.client.send_message('/fastbusy', '')

    def ring(self):
        self.client.send_message('/ring', '')

    def key(self, key):
        if key in ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9']:
            key = int(key)
        self.client.send_message('/key', key)

    def play_audio(self, basename):
        self.client.send_message('/play', basename)

    def keys_off(self):
        self.client.send_message('/keys', 'off')
