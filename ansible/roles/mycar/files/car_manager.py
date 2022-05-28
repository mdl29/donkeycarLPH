import requests
import socket
import os
import fcntl
import struct
from netifaces import ifaddresses, AF_INET

class CarManager:
    def __init__(self):
        # Temp, hardcoded for now as we're still deciding on how/where to put it.
        addr = "http://192.168.1.129:8000"
        self.name = socket.gethostname()
        # "There's no way this'll ever break."
        self.ip = ifaddresses("wlan0")[AF_INET][0]["addr"]
        self.color = os.environ['CONTROLLER_LED_COLOR']

        requests.post(addr + "/cars", json = {
            "name": self.name,
            "ip": self.ip,
            "color": self.color
        })

    def update(self):
        return
        
    def run_threaded(self):
        return
        
    def run(self):
        return self.run_threaded()
