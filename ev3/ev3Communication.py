# The EV3 communication socket
# Author: Jan-Luca D., Finn G.


import threading
from bluetooth import *
from constants import *
from logger import *
from message import Message
from utils import *

setLogLevel(logLevel)

s = None
client = None
size = MSGLEN


class BluetoothThread(threading.Thread):
    """Control the bluetooth connection"""

    def __init__(self, receivedData, channels = {}):
        threading.Thread.__init__(self)

        self.connected = False
        self.isRunning = True

        self.receivedData = receivedData

        # Define all channels...
        self.channels = channels

    def run(self):
        """Create the server in another thread"""

        # Create the bluetooth server...
        info("Create Bluetooth server")
        try:
            self.creatServer()
        except Exception as e:
            error("Failed to create server: %s" % e)
            return

    def addListener(self, channel, callback):
        """Add a listener for a channel"""

        debug("Add new listener for the channel '%s': %s" % (channel, callback))

        if not channel in self.channels:
            self.channels[channel] = [callback]
        else:
            self.channels[channel].append(callback)

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

        # Listen for messages...
        listenThread = threading.Thread(target=self.listen)
        listenThread.setName("ListenThread")
        listenThread.start()

    def creatServer(self):
        """Start the bluetooth server socket"""
        # Get MAC from device...
        try:
            mac = runCommand("hcitool dev | grep -o \"[[:xdigit:]:]\{11,17\}\"")
        except:
            error("Failed to create Server.")
            return -1

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

    def closeServer(self):
        """Close the server"""

        info("Close bluetooth server")

        # Close bluetooth server...
        s.close()

        # Set status to disconnected...
        self.connected = False
        self.isRunning = False

    def send(self, message):
        """Send data to bluetooth device"""

        # Get string of the message...
        text = str(message)

        debug("Send '%s' to bluetooth device" % text)
        global s
        try:
            client.send(text)
        except OSError as e:
            error("Failed to send: %s" % e)

            # Save new status...
            self.connected = False

    def listen(self):
        """Receive messages"""
        global s
        global MSGLEN

        info("Listening...")

        while self.connected:
            try:
                # Wait for data...
                data = client.recv(size)
            except OSError:
                error("Failed to Receive")

                if self.connected:
                    # Update status...
                    self.connected = False

                    error("Client disconnected")

                # Wait for a new client...
                self.waitForClient()

                # Stop listening...
                info("Stop listening")
                return

            msg = str(data).split(";")
            for i in range(len(msg)):
                if msg[i] != "'":
                    if msg[i].startswith("b'"):
                        msg[i] = msg[i][2:]

                    # Split the data in channel and value...
                    fragments = str(msg[i]).split(": ")
                    if len(fragments) == 2:
                        channel = fragments[0].strip()
                        value = fragments[1].strip()

                        debug("Received: %s" % (msg[i]))

                        # Check if the channel is in channels...
                        if channel in self.channels:
                            for i in range(len(self.channels[channel])):
                                listener = threading.Thread(target = self.receivedData, args = (self.channels[channel][i], value))
                                listener.start()
                    elif len(fragments) == 1:
                        self.closeServer()

        info("Stop listening")
