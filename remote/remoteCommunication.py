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
    """Control the bluetooth connection"""

    def __init__(self, parent, bluetoothEvent, macAddress = None, channels = {}):
        threading.Thread.__init__(self)

        self.bluetoothEvent = bluetoothEvent
        self.parent = parent

        self.connected = False

        # Define all channels...
        self.channels = channels

        self.macAddress = macAddress

    def run(self):
        """Start connection in a new Thread"""

        # Connect to bluetooth device...
        info("Connecting to EV3")
        try:
            self.connectByLastConnection()
        except Exception as e:
            debug("Failed to connect (Debug message): %s" % str(e).strip())
            error("Failed to connect")
            self.bluetoothEvent.emit(Message(channel = "connection", value = "Failed to connect"))
            info("Close bluetooth service")
            return

    def addListener(self, channel, callback):
        """Add a listener for a channel"""

        debug("Add new listener for the channel '%s': %s" % (channel, callback))

        # Add the listener...
        if not channel in self.channels:
            self.channels[channel] = [callback]
        else:
            self.channels[channel].append(callback)

    def searchDevices(self):
        """Search for bluetooth devices"""
        info("Searching for devices")

        # Inform the GUI...
        self.bluetoothEvent.emit(Message(channel = "connection", value = "Search devices"))

        # Search devices
        try:
            nearby_devices = discover_devices(lookup_names = True)
        except:
            raise Exception("Please activate bluetooth")
            return

        # List devices
        if len(nearby_devices) == 0:
            error("Found 0 devices")
        else:
            info("Found %d devices" % len(nearby_devices))
        i = 1

        devices = ""
        for name, addr in nearby_devices:
            devices += "%s - %s|" % (addr, name)
            debug("%s. %s - %s" % (i, addr, name))
            i += 1
        devices = devices[:-1]

        # Select and return the MAC of device
        if len(nearby_devices) == 0:
            exit()
        if len(nearby_devices) == 1:
            return nearby_devices[0][0]
        else:
            self.bluetoothEvent.emit(Message(channel = "selectDevice", value = devices))
            return None

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
        # Connect to the given mac address...
        if self.macAddress != None:
            self.connect(self.macAddress)
        # Connect to stored mac address...
        elif self.hasStoredMAC():
            try:
                # Connect to stored device mac...
                self.connect(self.readStoredMAC())
            except:
                # If device not visible or online search for others
                error("Couldn't connect to device with stored MAC")
                try:
                    device = self.searchDevices()
                    if device != None:
                        self.connect(device)
                except Exception as e:
                    raise e
        # Connect to a selected device...
        else:
            device = self.searchDevices()
            if device != None:
                self.connect(device)

    def connect(self, mac):
        """Connect to a bluetooth device"""
        info("Connecting to MAC " + mac)
        self.storeMAC(mac)

        # Inform the GUI...
        self.bluetoothEvent.emit(Message(channel = "connection", value = "Connecting..."))

        # Connect...
        global s
        s = BluetoothSocket(RFCOMM)
        s.connect((mac, port))
        info("Connected")

        # Save new status...
        self.connected = True

        # Listen for messages...
        listenThread = threading.Thread(target = self.listen)
        listenThread.setName("ListenThread")
        listenThread.start()
        
        # Inform the GUI...
        self.bluetoothEvent.emit(Message(channel = "connection", value = "Connected"))

    def getAllUpdates(self):
        """Get all updates in the listener channels"""
        for channel in self.channels:
            self.send(Message(channel = channel,  value = "update"))

    def calibrateEV3(self):
        """Calibrate the ev3..."""
        self.send(Message(channel = "calibrateForward", value = "%d:%d:%d" % (self.parent.settings.get("calibrateForwardTime", default = 3000), self.parent.settings.get("calibrateForwardSpeedR", default = 255), self.parent.settings.get("calibrateForwardSpeedL", default = 255))))
        self.send(Message(channel = "calibrateRight", value = "%d:%d:%d" % (self.parent.settings.get("calibrateRightTime", default = 3000), self.parent.settings.get("calibrateRightSpeedR", default = 255), self.parent.settings.get("calibrateRightSpeedL", default = 255))))
        self.send(Message(channel = "calibrateLeft", value = "%d:%d:%d" % (self.parent.settings.get("calibrateLeftTime", default = 3000), self.parent.settings.get("calibrateLeftSpeedR", default = 255), self.parent.settings.get("calibrateLeftSpeedL", default = 255))))

    def disconnect(self):
        """Disconnect from bluetooth device"""
        info("Disconnect from bluetooth device")
        global s

        try:
            s.close()
        except Exception as e:
            error("Faild to disconnect: %s" % e)

        info("Close bluetooth service")

        # Save new status...
        self.connected = False

        # Inform the GUI...
        self.bluetoothEvent.emit(Message(channel = "connection", value = "Disconnected"))

    def send(self, message):
        """Send data to bluetooth device"""

        # Inform the command line...
        self.parent.commandLine.newMessage(message, sent = True)

        text = str(message) + ";"
        debug("Send '%s' to bluetooth device" % text)
        global s
        try:
            # Send the message...
            s.send(text)
        except OSError as e:
            debug("Failed to send (DEBUG): %s" % e)
            error("Failed to send")

            # Save new status...
            if self.connected:
                self.connected = False

                # Inform the GUI...
                self.bluetoothEvent.emit(Message(channel = "connection", value = "Disconnected"))

    def listen(self):
        """Receive messages with a callback"""
        global s
        global MSGLEN

        info("Listening...")

        while self.connected:
            try:
                # Get the data...
                data = s.recv(MSGLEN)
            except OSError:
                error("Failed to Receive")

                if self.connected:
                    # Update status...
                    self.connected = False

                    # Inform the GUI...
                    self.bluetoothEvent.emit(Message(channel = "connection", value = "Disconnected"))

                # Stop listening...
                info("Stop listening")
                return

            debug("Received: %s" % (data))
            data = str(data).split("'")[1]
            fragments = str(data).split(": ")

            # Inform the GUI...
            if len(fragments) == 2:
                self.bluetoothEvent.emit(Message(channel = fragments[0].strip(), value = fragments[1].strip()))

        info("Stop listening")
