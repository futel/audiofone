
import time
from pythonosc import udp_client

class Tones:
    def __init__(self, host = '127.0.0.1', port = 6066):
        self.client = udp_client.SimpleUDPClient(host, port)

    def dialtone(self):
        self.client.send_message('/dialtone', '')

    def off(self):
        self.client.send_message('/off', '')

    def busy(self):
        self.client.send_message('/busy', '')

    def key(self, key):
        if key in ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9']:
            key = int(key)
        self.client.send_message('/key', key)
