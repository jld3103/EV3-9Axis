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

    def __init__(self, channels={}):
        threading.Thread.__init__(self)

        self.connected = False
        self.isRunning = True
        
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

    def searchDevices(self):
        """Search for bluetooth devices"""
        info("Searching for devices")
        
        # Inform the GUI...
        self.bluetoothEvent.emit(Message(channel="connection", value="Search devices"))

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
            self.bluetoothEvent.emit(Message(channel="selectDevice", value=devices))
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
        if self.hasStoredMAC():
            try:
                # Connect to stored device mac...
                if self.macAddress == None:
                    self.connect(self.readStoredMAC())
                # Connect to given address...
                else:
                    self.connect(self.macAddress)
            except:
                # If device not visible or online search for others
                error("Couldn't connect to device with stored MAC")
                #traceback.print_exc()
                try:
                    device = self.searchDevices()
                    if device != None:
                        self.connect(device)
                except Exception as e:
                    raise e
        else:
            self.connect(self.searchDevices())
            
    def selectedDevice(self, device):
        """Get the selected device from the GUI"""
        try:
            # Try to connect...
            self.connect(device)
        except Exception as e:
            error(e)
            
            # Inform the GUI about failing to connect...
            self.bluetoothEvent.emit(Message(channel="connection", value="Failed to connect"))
            
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
            info("Wait for msg...")
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

            info("Received: %s" % (data))
            
            # Split the data in channel and value...
            data = str(data).split("'")[1]
            fragments = str(data).split(": ")
            channel = fragments[0].strip()
            value = fragments[1].strip()
            
            # Check if the channel is in channels...
            if channel in self.channels:
                for function in self.channels[channel]:
                    listener = threading.Thread(target=function, args=(value))
                    listener.start()
                
        info("Stop listening")
