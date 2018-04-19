# The EV3 communication socket
# Author: Jan-Luca D., Finn G.

import atexit

from bluetooth import *
import threading
from constants import *
from logger import *
from utils import *

setLogLevel(logLevel)

s = None
client = None
size = MSGLEN

class BluetoothThread():
    """Take all signals from outside pyqt and send it to pyqt"""
    def __init__(self, channels={}):
        threading.Thread.__init__(self) 
        
        # Set the close listner...
        atexit.register(self.onExit)
        
        self.connected = False
        self.isRunning = True
        
        # Create dictionary for the listener...
        self.channels = channels
        
    def start(self):
        """Create the server in another thread"""
        # Create the bluetooth server...
        info("Create Bluetooth server")
        try:
            self.creatServer()
        except Exception as e:
            error("Failed to create server: %s" % e)
            return
        
    def closeServer(self):
        """Close the server"""
        # Close bluetooth server...
        s.close()
        info("Close bluetooth server")
        
        # Set status to disconnected...
        self.connected = False
        self.isRunning = False
        
    def addListener(self, channel, callback):
        """Add a listener for a channel"""
        
        debug("Add new listener for the channel '%s': %s" % (channel, callback))
        
        self.channels[channel] = callback       
            

    def creatServer(self, mac=None):
        """Start the bluetooth server socket"""
        # Get MAC from device if possible
        if mac == None:
            if getOS() == "Linux":
                try:
                    mac = runCommand(
                        "hcitool dev | grep -o \"[[:xdigit:]:]\{11,17\}\"")
                except:
                    raise Exception("Please activate bluetooth")
            else:
                mac = "00:00:00:00:00:00"  # Replace with your own mac
        info("Using " + mac + " as MAC")
        backlog = 1
        global s
        
        # Create the server...
        s = BluetoothSocket(RFCOMM)
        s.bind((mac, port))
        s.listen(backlog)
        
        # Update status...
        self.isRunning = True
        
        # Wait for a client...
        self.waitForClient()
            
    def waitForClient(self):
        """Wait for a client"""
        info("Wait for client...")
        try:
            global client
            client, clientInfo = s.accept()
            info("New Connection")
            
            # Update status...
            self.connected = True
        except:
            pass
        
    def onExit(self):
        """Exit callback for bluetooth socket close"""
        global s
        if s != None:
            s.close()
        
        # Update status...
        self.connected = False
        self.isRunning = False

    def send(self, msg):
        """Send data to bluetooth device"""
        
        # Get string of the message...
        text = str(msg)
        
        info("Send '%s' to bluetooth device" % text)
        global client
        
        # Send the string...
        client.send(text)

    def listen(self):
        """Receive messages with a callback"""
        debug("Wait for msg")
        try:
            # Wait for data...
            data = client.recv(size)
        except:
            # Update status...
            self.connected = False
            error("Client disconnected")
            
            # Wait for a new client...
            self.waitForClient()
            return -1
        
        info("Recived msg: %s" % str(data))
        
        # Split the data in channel and value...
        data = str(data).split("'")[1]
        fragments = str(data).split(": ")
        
        channel = fragments[0].strip()
        value = fragments[1].strip()
        
        # Check if the channel is in channels...
        if channel in self.channels:
            # Execute listener...
            return [self.channels[channel], value]
            
        return None
