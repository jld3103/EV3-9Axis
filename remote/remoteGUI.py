#!/usr/bin/python3

# This is the main file for the 3D Gui
# Author: Finn G.

version = "1.0"

import remote.remoteCommunication as communication
import queue
from PyQt4 import QtGui,  QtCore, uic
from constants import *
from logger import *
import threading

setLogLevel(logLevel)

class BluetoothReciveThread(threading.Thread):
    """Take all signals from outside pyqt and send it to pyqt"""
    def __init__(self, bluetoothReciveQueue, bluetoothEvent):
        threading.Thread.__init__(self) 
        
        self.bluetoothReciveQueue = bluetoothReciveQueue
        self.bluetoothEvent = bluetoothEvent
        
    def run(self):
        info("run BluetoothReciveThread")
        
        # wait for bluetooth signals...
        global alive
        while alive:
            try:
                msg = self.bluetoothReciveQueue.get(timeout=1.0)
            except:
                continue
                
            debug("Get a command in the bluetoothReciveQueue: %s" % msg)

            self.bluetoothEvent.emit(str(msg.channel), str(msg.value), int(msg.level))

        logging.info("Exit BluetoothThread")

class MainWindow(QtGui.QMainWindow):
    """Stellt die Hauptbenutzeroberfläche dar"""
    
    bluetoothEvent = QtCore.pyqtSignal(str, str, int)
    
    def __init__(self, version, parent=None):
        QtGui.QMainWindow.__init__(self, parent=None)
        
        # Load ui file from the qt designer...
        uic.loadUi('remote/MainWindow.ui', self)
        
        # Set the window settings...
        self.setWindowTitle("EV3 Gui - v%s" % (version))
        
        # Create the image for drawing...
        self.imageSize = QtCore.QSize(630, 420)
        self.image = QtGui.QImage(self.imageSize, QtGui.QImage.Format_RGB32)
        self.image.fill(QtGui.qRgb(150, 150, 150))
        
        # start bluetooth connection...
        # create the queues for the bluetooth data...
        self.bluetoothReciveQueue = queue.Queue()
        self.bluetoothSendQueue = queue.Queue()
        
        # start the bluetoothThread...
        bluetoothReciveThread = BluetoothReciveThread(self.bluetoothReciveQueue, self.bluetoothEvent)
        bluetoothReciveThread.setName("BluetoothReciveThread")
        bluetoothReciveThread.start()
        
        # start the Thread for the bluetooth connection...
        bluetoothThread = communication.BluetoothThread(self.bluetoothReciveQueue, self.bluetoothSendQueue)
        bluetoothThread.setName("BluetoothThread")
        bluetoothThread.start()
                
    def paintEvent(self, event):
        """Paint the image."""
        painter = QtGui.QPainter(self)
        painter.drawImage(event.rect(), self.image)

    def resizeEvent(self, event):
        """Called if the windowsize changed"""
        newSize = event.size()
        
        #check if the imagesize changed...
        if self.image.size() == newSize:
            return

        # Create a new image with new size and re-draw the rail network
        self.image = QtGui.QImage(newSize, QtGui.QImage.Format_RGB32)
        self.image.fill(QtGui.qRgb(150, 150, 150))
        
class RemoteGUI():
    """Create the window"""
    
    def __init__(self):
        """Create the window"""
        self.app = QtGui.QApplication([])
        self.window = MainWindow(version)
        self.window.show()

        status = self.app.exec_()
        global alive
        alive = False
        info("RemoteGUI finished with status %d" % status)
