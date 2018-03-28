class Message:
    def __init__(self, channel=None, value=None, level=0):
        self.channel = channel
        self.value = value
        self.level = level
        
    def __str__(self):
        return "%s: %s" % (self.channel, self.value)
