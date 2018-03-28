# A Class for the bluetooth communication
# Author: Finn G.

class Message:
    """This class displays a bluetooth message"""
    def __init__(self, channel=None, value=None, level=0):
        self.channel = channel
        self.value = value
        self.level = level
        
    def __str__(self):
        """Class to string function"""
        return "%s: %s" % (self.channel, self.value)
