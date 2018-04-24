# This is the main file for the Gui
# Author: Finn G., Jan-Luca D.

version = "1.1"

from PyQt4 import QtCore, QtGui

import remote.commandLineWidget as commandLineWidget
import remote.remoteCommunication as communication
import remote.robotWidget as robotWidget
import remote.roomWidget as roomWidget
from constants import *
from logger import *
from message import Message

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
        
        # Create Combo bock...
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
        self.parent.bluetooth = communication.BluetoothThread(self.parent.bluetoothEvent, macAddress=mac)
        self.parent.bluetooth.setName("BluetoothThread")
        self.parent.bluetooth.start()
        
        # Close dialog...
        self.close()

    def onClose(self):
        """Close the dialog"""
        self.close()

class MainWindow(QtGui.QMainWindow):
    """Controls the window"""

    bluetoothEvent = QtCore.pyqtSignal(Message)

    def __init__(self, version):
        QtGui.QMainWindow.__init__(self)

        # Set the window title...
        self.setWindowTitle("EV3 Gui - v%s" % (version))

        # Set window size...
        self.resize(630, 420)
        self.setMinimumSize(QtCore.QSize(630, 420))

        # Set background color...
        palette = self.palette()
        palette.setColor(self.backgroundRole(), QtCore.Qt.white)
        self.setPalette(palette)

        # Create statusbar...
        self.menubarHeight = 26
        self.statusBar = self.statusBar()
        self.statusBar.setGeometry(
            QtCore.QRect(0,
                         self.size().height() - self.menubarHeight,
                         self.size().width(),
                         self.size().height() - self.menubarHeight))
        self.bluetoothConnected = QtGui.QLabel("Disonnected")
        self.statusBar.addPermanentWidget(self.bluetoothConnected)

        # Create menubar....
        mainMenu = self.menuBar()
        mainMenu.setGeometry(
            QtCore.QRect(0, 0, self.size().width(), self.menubarHeight))
        bluetoothMenu = mainMenu.addMenu('&Bluetooth')
        self.connectionAction = QtGui.QAction("&Connect", self)
        self.connectionAction.setStatusTip('Connect to EV3')
        self.connectionAction.triggered.connect(self.onConnection)
        bluetoothMenu.addAction(self.connectionAction)

        # Connect the bluetoothEvent signal...
        self.bluetoothEvent.connect(self.onBluetoothEvent)

        # Start the Thread for the bluetooth connection...
        self.bluetooth = communication.BluetoothThread(self.bluetoothEvent)
        self.bluetooth.setName("BluetoothThread")
        self.bluetooth.start()

        # Insert the widgets...
        self.room_widget = roomWidget.Room(self, self.getRoomImgRect(), self.bluetooth)
        self.robot_widget = robotWidget.Robot(self, self.bluetooth)
        self.commandLine = commandLineWidget.CommandLine(self)
        
        # Setup the command line...
        self.commandLine.setGeometry(self.getTextEditRect())
        self.connect(self.commandLine, QtCore.SIGNAL("sendMessage"), self.onSendMessage)
        
        # Add listener...
        self.bluetooth.addListener("connection", self.handleConnection)
        self.bluetooth.addListener("close", self.bluetoothServerClosed)
        self.bluetooth.addListener("selectDevice", self.handleSelectDevice)

    def getPartingLine(self):
        """Calculate the coordinates of the parting line"""
        x = self.size().width() * 0.7
        line = QtCore.QLine(x, self.menubarHeight, x,
                            self.size().height() - self.menubarHeight - 1)
        return line

    def getRobotImgRect(self):
        """Calculate the rect of the robot img"""
        xPositionRobot = self.size().width() * 0.7 + 1
        rect = QtCore.QRect(xPositionRobot, self.menubarHeight,
                            self.size().width() * 0.3,
                            self.size().width() * 0.3)
        return rect

    def getRoomImgRect(self):
        """Calculate the rect of the room img"""
        xPositionRoom = self.size().width() * 0.7
        yPositionRoom = self.size().height() - self.menubarHeight * 2
        rect = QtCore.QRect(0, self.menubarHeight, xPositionRoom,
                            yPositionRoom)
        return rect

    def getTextEditRect(self):
        """Calculate the rect of the MessageTextEdit img"""
        x = self.size().width() * 0.7 + 1
        y = self.size().width() * 0.3 + self.menubarHeight
        x2 = self.size().width() - self.size().width() * 0.7
        y2 = self.size().height() - self.menubarHeight * 2 - self.size().width(
        ) * 0.3
        rect = QtCore.QRect(x, y, x2, y2)
        return rect

    def onSendMessage(self, text):
        """Send a command of the QTextEdit"""
        info("send msg: %s" % text)

        # Split the text in channel and value...
        fragments = text.split(": ")

        # If channel and value exist spit them...
        if len(fragments) == 2:
            self.bluetooth.send(Message(channel=fragments[0], value=fragments[1]))
        else:
            self.bluetooth.send(Message(channel=fragments[0]))

    def onConnection(self):
        """Handle the connect action in the menubar"""
        debug("Thread alive: %s" % self.bluetooth.isAlive())
        if not self.bluetooth.connected and not self.bluetooth.isAlive():
            # Start the Thread for the bluetooth connection...
            info("Send connect signal")
            self.bluetooth = communication.BluetoothThread(self.bluetoothEvent, self.bluetooth.channels)
            self.bluetooth.setName("BluetoothThread")
            self.bluetooth.start()

        elif self.bluetooth.connected:
            # Send disconnect signal...
            info("Send disconnect signal")
            self.bluetooth.disconnect()

    def onBluetoothEvent(self, message):
        """Handle the bluetooth events"""
        
        self.commandLine.newMessage(message)

        # Execute the function for this channel...
        if message.channel in self.bluetooth.channels and not message.value == "Device not connected":
            for function in self.bluetooth.channels[message.channel]:
                function(message.value)
                
    def handleConnection(self, value):
        """Handle the bluetooth connection"""
        
        # Set statusbar on value...
        self.bluetoothConnected.setText(value)
        
        # Update bluetooth action in menubar...
        if self.bluetooth.connected:
            self.connectionAction.setText("Disconnect")
        else:
            self.connectionAction.setText("Connect")
        
        # Show push up window...
        if value == "Connected":
            QtGui.QMessageBox.information(None, "Bluetooth", "Connected...", QtGui.QMessageBox.Ok)
        elif value == "Disconnected":
            QtGui.QMessageBox.information(None, "Bluetooth", "Disconnected...", QtGui.QMessageBox.Ok)
        elif value == "Failed to connect":
            QtGui.QMessageBox.information(None, "Bluetooth", "Failed to connect!", QtGui.QMessageBox.Ok)
            
    def handleSelectDevice(self, value):
        """Show a dialog for selecting a bluetooth device"""
        dialog = SelectDeviceDialog(self, value)
        dialog.show()
                
    def bluetoothServerClosed(self, value):
        """Inform the user about the closed server"""
        self.bluetoothConnected.setText("Disonnected")
        QtGui.QMessageBox.information(
            None, "Bluetooth", "Server closed...", QtGui.QMessageBox.Ok)
        
        # Update connection...
        self.handleConnection("Disconnected")

    def paintEvent(self, event):
        """Paint the window."""

        # Paint the images...
        painter = QtGui.QPainter(self)
        painter.drawImage(self.getRoomImgRect(), self.room_widget)

        # Draw parting line...
        painter.drawLine(self.getPartingLine())

    def resizeEvent(self, event):
        """Called if the windowsize changed"""

        # Update TextEdit size...
        self.commandLine.setGeometry(self.getTextEditRect())

        # Update Robot widget size...
        self.robot_widget.setGeometry(self.getRobotImgRect())

    def closeEvent(self, event):
        """When the window close, close the server, too"""

        if self.bluetooth.connected:
            question = QtGui.QMessageBox.question(None, "Connection", "Close server?", "Yes", "No")

            # Close the server...
            if question == 0:
                self.bluetooth.send(Message(channel="close"))
                
            self.bluetooth.disconnect()


class RemoteGUI():
    """Create the window"""

    def __init__(self):
        """Create the window"""

        # Create the window...
        self.app = QtGui.QApplication([])
        self.window = MainWindow(version)
        self.window.show()

        # Show the window...
        status = self.app.exec_()

        # Close programm...
        global alive
        alive = False
        info("RemoteGUI finished with status %d" % status)
