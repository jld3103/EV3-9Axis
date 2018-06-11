# This is the main file for the Gui
# Author: Finn G., Jan-Luca D.

version = "1.2"

import signal

# Import the GUI library PyQt4...
from PyQt4 import QtCore, QtGui

import remote.calibrateDialog as calibrateDialog
# Import all widget...
import remote.commandLineWidget as commandLineWidget
import remote.filterDialog as filterDialog
# Import the bluetooth communication...
import remote.remoteCommunication as communication
import remote.robotWidget as robotWidget
import remote.roomWidget as roomWidget
# Import all dialogs...
import remote.selectDeviceDialog as selectDeviceDialog
from constants import *
from logger import *
from message import Message
from settings import Settings

setLogLevel(logLevel)

# Close the window when CTRL+C is pressed...
signal.signal(signal.SIGINT, signal.SIG_DFL)


class MainWindow(QtGui.QMainWindow):
    """Controls the window"""

    bluetoothEvent = QtCore.pyqtSignal(Message)

    def __init__(self, version):
        QtGui.QMainWindow.__init__(self)

        self.alive = True

        # Set the window title...
        self.setWindowTitle("EV3 Navigator - v%s" % (version))
        self.setWindowIcon(QtGui.QIcon(windowIcon))

        # Set window size...
        self.resize(630, 420)
        self.setMinimumSize(QtCore.QSize(630, 530))

        # Set background color...
        palette = self.palette()
        palette.setColor(self.backgroundRole(), QtCore.Qt.white)
        self.setPalette(palette)

        # Read setting...
        self.settings = Settings()

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

        # Create all main menu entries...
        bluetoothMenu = mainMenu.addMenu('&Bluetooth')
        roomMenu = mainMenu.addMenu('&Room')
        cmdMenu = mainMenu.addMenu('&Command line')
        ev3Menu = mainMenu.addMenu('&EV3')

        # Create all actions of the main menu...
        self.connectionAction = QtGui.QAction("&Connect", self)
        self.showFloorSquareAction = QtGui.QAction("&%s floor squares" % ("Hide" if self.settings.get("showFloorSquare", default=True) else "Show"), self)
        self.showSetsAction = QtGui.QAction("&%s sets" % ("Hide" if self.settings.get("showSets", default=False) else "Show"), self)
        self.showPreviewPathAction = QtGui.QAction("&%s preview path" % ("Hide" if self.settings.get("showPreviewPath", default=True) else "Show"), self)
        self.showSentMsgAction = QtGui.QAction("&%s sent messages" % ("Hide" if self.settings.get("showSentMsg", default=True) else "Show"), self)
        self.showReceivedMsgAction = QtGui.QAction("&%s received messages" % ("Hide" if self.settings.get("showReceivedMsg", default=True) else "Show"), self)
        self.channelFilterAction = QtGui.QAction("&Manage channel filter",self)
        self.calibrateFAction = QtGui.QAction("&Calibrate forward", self)
        self.calibrateRAction = QtGui.QAction("&Calibrate turn right", self)
        self.calibrateLAction = QtGui.QAction("&Calibrate turn left", self)
        self.calibrateDAction = QtGui.QAction("&Calibrate distance sensor", self)

        # Connect all actions of the main menu...
        self.connectionAction.triggered.connect(self.onConnection)
        self.showFloorSquareAction.triggered.connect(self.onShowFloorSquare)
        self.showSetsAction.triggered.connect(self.onShowSets)
        self.showPreviewPathAction.triggered.connect(self.onShowPreviewPath)
        self.showSentMsgAction.triggered.connect(self.onShowSentMsg)
        self.showReceivedMsgAction.triggered.connect(self.onShowReceivedMsg)
        self.channelFilterAction.triggered.connect(self.onManageChannelFilter)
        self.calibrateFAction.triggered.connect(self.onCalibrateF)
        self.calibrateRAction.triggered.connect(self.onCalibrateR)
        self.calibrateLAction.triggered.connect(self.onCalibrateL)
        self.calibrateDAction.triggered.connect(self.onCalibrateD)

        # Add all actions to the main menu entries...
        bluetoothMenu.addAction(self.connectionAction)
        roomMenu.addAction(self.showFloorSquareAction)
        roomMenu.addAction(self.showSetsAction)
        roomMenu.addAction(self.showPreviewPathAction)
        cmdMenu.addAction(self.showSentMsgAction)
        cmdMenu.addAction(self.showReceivedMsgAction)
        cmdMenu.addAction(self.channelFilterAction)
        ev3Menu.addAction(self.calibrateFAction)
        ev3Menu.addAction(self.calibrateLAction)
        ev3Menu.addAction(self.calibrateRAction)
        ev3Menu.addAction(self.calibrateDAction)

        # Add the status tips......
        self.connectionAction.setStatusTip('Connect to EV3')

        # Connect the bluetoothEvent signal...
        self.bluetoothEvent.connect(self.onBluetoothEvent)

        # Start the Thread for the bluetooth connection...
        self.bluetooth = communication.BluetoothThread(self,
                                                       self.bluetoothEvent)
        self.bluetooth.setName("BluetoothThread")
        self.bluetooth.start()

        # Insert the widgets...
        self.room_widget = roomWidget.RoomWidget(self, self.settings,
                                                 self.bluetooth)
        self.robot_widget = robotWidget.Robot(self, self.bluetooth)
        self.commandLine = commandLineWidget.CommandLine(self, self.bluetooth)

        # Setup the command line...
        self.commandLine.setGeometry(self.getTextEditRect())

        # Add bluetooth listener...
        self.bluetooth.addListener("connection", self.handleConnection)
        self.bluetooth.addListener("close", self.handleClose, updating = False)
        self.bluetooth.addListener("selectDevice", self.handleSelectDevice)

    def getPartingLine(self):
        """Calculate the coordinates of the parting line"""
        x = self.size().width() * 0.7
        line = QtCore.QLine(x, self.menubarHeight, x,
                            self.size().height() - self.menubarHeight - 1)
        return line

    def getRobotWidgetRect(self):
        """Calculate the rect of the robot img"""
        xPositionRobot = self.size().width() * 0.7 + 1
        rect = QtCore.QRect(xPositionRobot, self.menubarHeight,
                            self.size().width() * 0.3,
                            self.size().width() * 0.2)
        return rect

    def getRoomWidgetRect(self):
        """Calculate the rect of the room img"""
        xPositionRoom = self.size().width() * 0.7
        yPositionRoom = self.size().height() - self.menubarHeight * 2
        rect = QtCore.QRect(0, self.menubarHeight, xPositionRoom,
                            yPositionRoom)
        return rect

    def getTextEditRect(self):
        """Calculate the rect of the MessageTextEdit img"""
        x = self.size().width() * 0.7 + 1
        y = self.size().width() * 0.2 + self.menubarHeight + 2
        x2 = self.size().width() - self.size().width() * 0.7
        y2 = self.size().height() - self.menubarHeight * 2 - self.size().width(
        ) * 0.2 - 2
        rect = QtCore.QRect(x, y, x2, y2)
        return rect

    def onManageChannelFilter(self):
        """Show the filter dialog"""
        dialog = filterDialog.FilterDialog(self)
        dialog.show()

    def onShowReceivedMsg(self):
        """Show the received messages in the command line"""
        if self.settings.get("showReceivedMsg"):
            self.settings.set("showReceivedMsg", False)
            self.showReceivedMsgAction.setText("Show received messages")
        else:
            self.settings.set("showReceivedMsg", True)
            self.showReceivedMsgAction.setText("Hide received messages")

    def onShowSentMsg(self):
        """Show the sent messages in the command line"""
        if self.settings.get("showSentMsg"):
            self.settings.set("showSentMsg", False)
            self.showSentMsgAction.setText("Show sent messages")
        else:
            self.settings.set("showSentMsg", True)
            self.showSentMsgAction.setText("Hide sent messages")

    def onShowSets(self):
        """Show the sets of the algorithm in the room widget"""
        if self.settings.get("showSets"):
            self.settings.set("showSets", False)
            self.showSetsAction.setText("Show sets")
        else:
            self.settings.set("showSets", True)
            self.showSetsAction.setText("Hide sets")
        self.room_widget.updateImage()
        
    def onShowPreviewPath(self):
        """Show or hid the example path to the current mouse position"""
        if self.settings.get("showPreviewPath"):
            self.settings.set("showPreviewPath", False)
            self.showPreviewPathAction.setText("Show preview path")
        else:
            self.settings.set("showPreviewPath", True)
            self.showPreviewPathAction.setText("Hide preview path")
        self.room_widget.updateImage()


    def onShowFloorSquare(self):
        """Show the floor squares in the room widget"""
        if self.settings.get("showFloorSquare"):
            self.settings.set("showFloorSquare", False)
            self.showFloorSquareAction.setText("Show floor squares")
        else:
            self.settings.set("showFloorSquare", True)
            self.showFloorSquareAction.setText("Hide floor squares")
        self.room_widget.updateImage()

    def onConnection(self):
        """Handle the connect action in the menubar"""
        debug("Thread alive: %s" % self.bluetooth.isAlive())
        if not self.bluetooth.connected and not self.bluetooth.isAlive():
            # Start the Thread for the bluetooth connection...
            info("Send connect signal")
            self.bluetooth = communication.BluetoothThread(
                self,
                self.bluetoothEvent,
                bluetoothData=self.bluetooth.bluetoothData)
            self.bluetooth.setName("BluetoothThread")
            self.bluetooth.start()

        elif self.bluetooth.connected:
            # Send disconnect signal...
            info("Send disconnect signal")
            self.bluetooth.disconnect()

    def onBluetoothEvent(self, message):
        """Handle the bluetooth events"""

        # Inform the command line...
        self.commandLine.newMessage(message)

        # Execute the function for this channel...
        if message.channel in self.bluetooth.bluetoothData.channels and not message.value == "Device not connected":
            for function in self.bluetooth.bluetoothData.channels[message.
                                                                  channel]:
                function(message.value)
                
    def handleClose(self, value):
        """Hande the bluetooth connection"""
        
        if value == "Closed server":
            self.bluetooth.disconnect()

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
            # Init the ev3...
            self.bluetooth.calibrateEV3()
            self.bluetooth.getAllUpdates()
            # Show the connected dialog...
            QtGui.QMessageBox.information(None, "Bluetooth", "Connected",
                                          QtGui.QMessageBox.Ok)
        elif value == "Disconnected":
            QtGui.QMessageBox.information(None, "Bluetooth", "Disconnected",
                                          QtGui.QMessageBox.Ok)
        elif value == "Failed to connect":
            QtGui.QMessageBox.information(
                None, "Bluetooth", "Failed to connect!", QtGui.QMessageBox.Ok)

    def onCalibrateF(self):
        """Calibrate froward on the ev3"""
        dialog = calibrateDialog.CalibrateDialog(self, mode = "Forward", settings = (("calibrateForwardTime", 3000), ("calibrateForwardSpeedR", 255), ("calibrateForwardSpeedL", 255)), units = ("Time", "Speed", "Speed"), sliderDifferences = (100, 300, 100, 5000))
        dialog.show()

    def onCalibrateR(self):
        """Calibrate right on the ev3"""
        dialog = calibrateDialog.CalibrateDialog(self, mode = "Right", settings = (("calibrateRightSpeed", 60), ("calibrateRightDegrees", 90)), units = ("Speed", "Degrees"), sliderDifferences = (20, 150, 10, 200))
        dialog.show()

    def onCalibrateL(self):
        """Calibrate left on the ev3"""
        dialog = calibrateDialog.CalibrateDialog(self, mode = "Left", settings = (("calibrateLeftSpeed", 60), ("calibrateLeftDegrees", -90)), units = ("Speed", "Degrees"), sliderDifferences = (-150, -20, 10, 200))
        dialog.show()

    def onCalibrateD(self):
        """Calibrate distance sensor"""
        dialog = calibrateDialog.CalibrateDialog(self, mode = "Distance", settings = [("calibrateDistance", 2000)], units = ["Distance"], sliderDifferences = (0, 0, 10, 2499))
        dialog.show()

    def handleSelectDevice(self, value):
        """Show a dialog for selecting a bluetooth device"""
        dialog = selectDeviceDialog.SelectDeviceDialog(self, value)
        dialog.show()

    def paintEvent(self, event):
        """Paint the window."""

        # Draw parting line...
        painter = QtGui.QPainter(self)
        painter.drawLine(self.getPartingLine())

    def resizeEvent(self, event):
        """Called if the windowsize changed"""

        # Update TextEdit sizes...
        self.commandLine.setGeometry(self.getTextEditRect())
        self.robot_widget.setGeometry(self.getRobotWidgetRect())
        self.room_widget.setGeometry(self.getRoomWidgetRect())

    def closeEvent(self, event):
        """When the window close, close the server, too"""

        # Save the current grid...
        self.room_widget.closeEvent(event)

        # Save the settings...
        self.settings.save()

        if self.bluetooth.connected:
            question = QtGui.QMessageBox.question(None, "Connection",
                                                  "Close server?", "Yes", "No")

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
        self.window.alive = False
        info("RemoteGUI finished with status %d" % status)
