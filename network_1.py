'''
Created on Oct 27, 2019

@author: Cole Sluggett, Kayla Wheeler
'''
import queue
import threading
from network import Interface, NetworkPacket, Host, Router

## thread target for the host to keep forwarding data


def run(self):
    print(threading.currentThread().getName() + ': Starting')
    while True:
        self.forward()
        if self.stop:
            print(threading.currentThread().getName() + ': Ending')
            return
