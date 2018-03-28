# Constants file
# Used for global not-changing variables

# Author: Finn G.

from logger import *

MSGLEN = 1024
port = 3
logLevel = DEBUG
alive = True

class Message:
    def __init__(self, channel=None, value=None, level=0):
        self.channel = channel
        self.value = value
        self.level = level
        
    def __str__(self):
        return "%s: %s" % (self.channel, self.value)
