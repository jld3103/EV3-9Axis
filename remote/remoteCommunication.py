# The remote communication socket
# Author: Jan-Luca D., Finn G.

import threading

from bluetooth import *

from constants import *
from logger import *
from message import Message
from utils import *

s = None
setLogLevel(logLevel)


class BluetoothThread(threading.Thread):
    """Take all signals from outside pyqt and send it to pyqt"""

    def __init__(self, bluetoothEvent):
        threading.Thread.__init__(self)

        self.bluetoothEvent = bluetoothEvent
        
        # Define all channels...
        self.channels = {
        }
        
    def run(self):
        # Connect to bluetooth device...
        info("Connecting to EV3")
        try:
            self.connectByLastConnection()
        except Exception as e:
            error(e)
            info("Close bluetooth service")
            return

    def addListener(self, channel, callback):
        if not channel in self.channels:
            self.channels[channel] = [callback]
        else:
            self.channels[channel].append(callback)            

    def searchDevices(self):
        """Search for bluetooth devices"""
        info("Searching for devices")

        # Search devices
        try:
            nearby_devices = discover_devices(lookup_names=True)
        except:
            raise Exception("Please activate bluetooth")
            return

        # List devices
        if len(nearby_devices) == 0:
            error("Found 0 devices")
        else:
            info("Found %d devices" % len(nearby_devices))
        i = 1
        for name, addr in nearby_devices:
            info("%s. %s - %s" % (i, addr, name))
            i += 1

        # Select and return the MAC of device
        if len(nearby_devices) == 0:
            exit()
        if len(nearby_devices) == 1:
            return nearby_devices[0][0]
        else:
            info("Select the device to connect to:")
            return nearby_devices[int(input()) - 1][0]

    def readStoredMAC(self):
        """Read the stored MAC from file"""
        return readFile(".mac.txt")

    def storeMAC(self, mac):
        """Store the MAC in a file"""
        writeFile(".mac.txt", mac)

    def hasStoredMAC(self):
        """Check if MAC stored previously"""
        return existsFile(".mac.txt")

    def connectByLastConnection(self):
        """Read stored MAC and connect to it or search for a device and connect to it"""
        if self.hasStoredMAC():
            try:
                # Connect to stored device mac
                self.connect(self.readStoredMAC())
            except:
                # If device not visible or online search for others
                error("Couldn't connect to device with stored MAC")
                #traceback.print_exc()
                try:
                    self.connect(self.searchDevices())
                except Exception as e:
                    raise e
        else:
            self.connect(self.searchDevices())

    def connect(self, mac):
        """Connect to a bluetooth device"""
        info("Connecting to MAC " + mac)
        self.storeMAC(mac)

        # Connect...
        global s
        s = BluetoothSocket(RFCOMM)
        s.connect((mac, port))
        info("Connected")

        # Inform the GUI...
        self.bluetoothEvent.emit(Message(channel="connection", value="connected"))
                
    def disconnect(self):
        """Disconnect from bluetooth device"""
        info("Disconnect from bluetooth device")
        global s
        
        try:
            s.close()
        except Exception as e:
            error("Faild to disconnect: %s" % e)
            
        info("Close bluetooth service")

        # Inform the GUI...
        self.bluetoothEvent.emit(Message(channel="connection", value="disconnected"))

    def send(self, message):
        """Send data to bluetooth device"""
        text = str(message)
        debug("Send '%s' to bluetooth device" % text)
        global s
        try:
            s.send(text)
        except OSError as e:
            error("Failed to send: %s" % e)

            # Inform the GUI...
            self.bluetoothEvent.emit(Message(channel="connection", value="disconnected"))
            
        # Listen for answer...
        self.listen()

    def listen(self):
        """Receive messages with a callback"""
        global s
        global MSGLEN

        info("Wait for msg...")
        try:
            data = s.recv(MSGLEN)
        except OSError as e:
            error("Failed to Receive: %s" % e)

            self.bluetoothEvent.emit(Message(channel="connection", value="disconnected"))
            return

        info("Received: %s" % (data))
        data = str(data).split("'")[1]
        fragments = str(data).split(": ")
        
        # Inform the GUI...
        self.bluetoothEvent.emit(Message(channel=fragments[0].strip(), value=fragments[1].strip()))
