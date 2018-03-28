# The EV3 communication socket
# Author: Jan-Luca D., Finn G.

import atexit

from bluetooth import *
import threading
from constants import *
from message import Message
from logger import *
from utils import *

setLogLevel(logLevel)

s = None
client = None
size = MSGLEN

class BluetoothThread(threading.Thread):
    """Take all signals from outside pyqt and send it to pyqt"""
    def __init__(self, bluetoothReciveQueue, bluetoothSendQueue):
        threading.Thread.__init__(self) 
        
        # Set the close listner...
        atexit.register(self.onExit)
        
        self.bluetoothReciveQueue = bluetoothReciveQueue
        self.bluetoothSendQueue = bluetoothSendQueue
        
    def run(self):
        # Create the bluetooth server...
        info("Create Bluetooth server")
        try:
            self.creatServer()
        except Exception as e:
            error("Failed to create server: %s" % e)
            return
        
        # Send data until the ev3 programm close...
        while True:
            self.listen()
            try:
                msg = self.bluetoothSendQueue.get(timeout=1.0)
            except:
                continue
            
            debug("Get a command in the bluetoothSendQueue: %s" % msg)
            
            # Send msg...
            self.send(str(msg))
            
            # If the msg channel is 'close' exit the Thread...
            if msg.channel == "close":
                break
        
        global s
        
        # Close bluetooth server...
        s.close()
        info("Close bluetooth service")

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
        
        # Wait for a client...
        self.waitForClient()
            
    def waitForClient(self):
        """Wait for a client"""
        info("Wait for client...")
        try:
            global client
            client, clientInfo = s.accept()
            info("New Connection")
        except:
            pass
        
    def onExit(self):
        """Exit callback for bluetooth socket close"""
        global s
        if s != None:
            s.close()

    def send(self, text):
        """Send data to bluetooth device"""
        debug("Send '%s' to bluetooth device" % text)
        global client
        client.send(text)

    def listen(self):
        """Receive messages with a callback"""
        debug("Wait for msg")
        try:
            # Wait for data...
            data = client.recv(size)
        except:
            error("Client disconnected")
            self.waitForClient()
            return
        
        debug("Recived msg: %s" % str(data))
        
        # Split the data in channel and value...
        data = str(data).split("'")[1]
        fragments = str(data).split(": ")
        
        # Put recived message in the queue...
        self.bluetoothReciveQueue.put(Message(channel=fragments[0].strip(), value=fragments[1].strip()))
