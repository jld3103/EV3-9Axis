#!/usr/bin/python3

# This widget displays the room
# Author: Finn G.

from PyQt4 import QtGui,  QtCore
from constants import *
from logger import *

setLogLevel(logLevel)

class Room(QtGui.QImage):
    """This class displays the room with all barriers and etc."""
    
    def __init__(self, parent, rect, bluetooth, format=QtGui.QImage.Format_RGB32):
        size = QtCore.QSize(rect.width(), rect.height())
        super(Room,  self).__init__(size, format)
        
        self.parent = parent
        self.bluetooth = bluetooth
        
        # Fill image...
        self.fill(QtGui.qRgb(150, 150, 150))
        
        # For sending: self.bluetooth.send(Message())
        # For listener: self.bluetooth.addListener("CHANNEL", FUNCTION)
        
