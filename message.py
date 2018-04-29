# A Class for the bluetooth communication
# Author: Finn G.

class Message:
    """This class displays a bluetooth message"""
    def __init__(self, channel = None, value = None):
        self.channel = channel
        self.value = value

    def __str__(self):
        """Class to string function"""
        return "%s: %s" % (self.channel, self.value)
