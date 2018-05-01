# This is a dialog for selecting a bloutooth deveice
# Author: Finn G.,


from PyQt4 import QtCore, QtGui

from constants import *
from logger import *

setLogLevel(logLevel)

class SelectDeviceDialog(QtGui.QDialog):
    """Show dialog for selecting a bluetooth device"""
    
    selectedDevice = None
    
    def __init__(self, parent, devices):
        QtGui.QDialog.__init__(self, parent)
        
        self.setWindowTitle("Select Device")
        self.setMinimumSize(QtCore.QSize(390, 160))
        self.setMaximumSize(QtCore.QSize(390, 160))
        
        self.parent = parent
        
        # Set background color...
        p = self.palette()
        p.setColor(self.backgroundRole(), QtGui.QColor(255, 255, 255))
        self.setPalette(p)
        
        # Get list of devices...
        self.devices = devices.split("|")
        
        # Create Combo box...
        self.comboBox = QtGui.QComboBox(self)
        self.comboBox.setGeometry(10, 20, 360, 22)
        self.comboBox.addItems(self.devices)
        self.comboBox.show()
        
        # Add OK button...
        self.btn_ok = QtGui.QPushButton(self)
        self.btn_ok.setGeometry(180, 80, 93, 28)
        self.btn_ok.setText("OK")
        self.btn_ok.show()
        
        # Add Close button...
        self.btn_close = QtGui.QPushButton(self)
        self.btn_close.setGeometry(280, 80, 93, 28)
        self.btn_close.setText("Close")
        self.btn_close.show()
        
        # Connect buttons...
        self.connect(self.btn_ok, QtCore.SIGNAL("clicked()"),  self.onOk)
        self.connect(self.btn_close, QtCore.SIGNAL("clicked()"),  self.onClose)
                
    def onOk(self):
        """Save the selected device"""
        
        # Get selected device...
        device = self.comboBox.currentText()
        info("Selected %s" % device)
        
        # Get mac address...
        mac = device.split("-")[1].strip()
        
        # Start the Thread for the bluetooth connection with the selected device...
        self.parent.bluetooth = communication.BluetoothThread(self.parent, self.parent.bluetoothEvent, macAddress=mac, channels=self.parent.bluetooth.channels)
        self.parent.bluetooth.setName("BluetoothThread")
        self.parent.bluetooth.start()
        
        # Close dialog...
        self.close()

    def onClose(self):
        """Close the dialog"""
        self.close()
