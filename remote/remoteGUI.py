#!/usr/bin/python3

# This is the main file for the Gui
# Author: Finn G.

version = "1.1"

from message import Message
import remote.remoteCommunication as communication
import queue
from PyQt4 import QtGui,  QtCore
import remote.roomWidget as roomWidget
import remote.robotWidget as robotWidget
import remote.messageTextEditWidget as messageTextEditWidget
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
                # Wait max. one second for a signal in the queue...
                msg = self.bluetoothReciveQueue.get(timeout=1.0)
            except:
                continue
                
            debug("Get a command in the bluetoothReciveQueue: %s" % msg)
            
            # Emit qt signal...
            self.bluetoothEvent.emit(str(msg.channel), str(msg.value), int(msg.level))

        logging.info("Exit BluetoothThread")
        
        
class MainWindow(QtGui.QMainWindow):
    """Controls the window"""
    
    bluetoothEvent = QtCore.pyqtSignal(str, str, int)
    
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
        self.statusBar.setGeometry(QtCore.QRect(0, self.size().height()-self.menubarHeight, self.size().width(), self.size().height()-self.menubarHeight))
        self.bluetoothConnected = QtGui.QLabel("Disonnected")
        self.statusBar.addPermanentWidget(self.bluetoothConnected)
        
        # Create menubar....
        mainMenu = self.menuBar()
        mainMenu.setGeometry(QtCore.QRect(0, 0, self.size().width(), self.menubarHeight))
        bluetoothMenu = mainMenu.addMenu('&Bluetooth')
        self.connectionAction = QtGui.QAction("&Connect", self)
        self.connectionAction.setStatusTip('Connect to EV3')
        self.connectionAction.triggered.connect(self.onConnection)
        bluetoothMenu.addAction(self.connectionAction)
        
        # Insert the widgets...
        self.room_widget = roomWidget.Room(self.getRoomImgRect())
        self.robot_widget = robotWidget.Robot(self)
        self.messageTextEdit = messageTextEditWidget.MessageTextEdit(self)
        
        # Setup the command line...
        self.messageTextEdit.setGeometry(self.getTextEditRect())
        self.connect(self.messageTextEdit, QtCore.SIGNAL("sendMessage"),  self.onSendMessage)
        
        # Create the queues for the bluetooth data...
        self.bluetoothReciveQueue = queue.Queue()
        self.bluetoothSendQueue = queue.Queue()
        
        # Connect the bluetoothEvent signal...
        self.bluetoothEvent.connect(self.onBluetoothEvent)
        
        # Start the bluetoothThread...
        bluetoothReciveThread = BluetoothReciveThread(self.bluetoothReciveQueue, self.bluetoothEvent)
        bluetoothReciveThread.setName("BluetoothReciveThread")
        bluetoothReciveThread.start()
        
        # Start the Thread for the bluetooth connection...
        self.bluetoothThread = communication.BluetoothThread(self.bluetoothReciveQueue, self.bluetoothSendQueue)
        self.bluetoothThread.setName("BluetoothThread")
        self.bluetoothThread.start()
        
        # Define all channels...
        self.channels = { "touchSensor" : self.robot_widget.setTouchSensor, 
                    "infraredSensor" : self.robot_widget.setInfraredSensor, 
                    "colorSensor" : self.robot_widget.setColorSensor, 
                    "motorR" : self.robot_widget.setMotorR, 
                    "motorL" : self.robot_widget.setMotorL, 
                    "Accel" : self.robot_widget.setAccel, 
                    "Gyrol" : self.robot_widget.setGyro, 
                    "Mag" : self.robot_widget.setMag}
        
    def getPartingLine(self):
        """Calculate the coordinates of the parting line"""
        x = self.size().width()*0.7
        line = QtCore.QLine(x, self.menubarHeight, x, self.size().height() - self.menubarHeight-1)
        return line
        
    def getRobotImgRect(self):
        """Calculate the rect of the robot img"""
        xPositionRobot = self.size().width()*0.7 + 1
        rect = QtCore.QRect(xPositionRobot, self.menubarHeight, self.size().width()*0.3, self.size().width()*0.3)
        return rect
        
    def getRoomImgRect(self):
        """Calculate the rect of the room img"""
        xPositionRoom = self.size().width()*0.7
        yPositionRoom = self.size().height() - self.menubarHeight *2
        rect = QtCore.QRect(0, self.menubarHeight,  xPositionRoom, yPositionRoom)
        return rect
        
    def getTextEditRect(self):
        """Calculate the rect of the MessageTextEdit img"""
        x = self.size().width()*0.7 + 1
        y = self.size().width()*0.3 + self.menubarHeight
        x2 = self.size().width()-self.size().width()*0.7
        y2 = self.size().height()-self.menubarHeight*2-self.size().width()*0.3
        rect = QtCore.QRect(x, y, x2, y2)
        return rect
        
    def onSendMessage(self, text):
        """Send a command of the QTextEdit"""
        info("send msg: %s" % text)
        
        # Split the text in channel and value...
        fragments = text.split(": ")
        
        # If channel and value exist spit them...
        if len(fragments) == 2:
            self.bluetoothSendQueue.put(Message(channel=fragments[0], value=fragments[1]))
        else:
            self.bluetoothSendQueue.put(Message(channel=fragments[0]))
        
    def onConnection(self):
        """Handle the connect action in the menubar"""
        info("Thread alive: %s" % self.bluetoothThread.isAlive())
        if self.connectionAction.text() == "Connect" and not self.bluetoothThread.isAlive():
            # Start the Thread for the bluetooth connection...
            info("Send connect signal")
            self.bluetoothThread = communication.BluetoothThread(self.bluetoothReciveQueue, self.bluetoothSendQueue)
            self.bluetoothThread.setName("BluetoothThread")
            self.bluetoothThread.start()

        elif self.connectionAction.text() == "Disconnect" and self.bluetoothThread.isAlive():
            # Send disconnect signal...
            info("Send disconnect signal")
        
    @QtCore.pyqtSlot(str, str, int)
    def onBluetoothEvent(self, channel, value, level):
        """Handle the bluetooth events"""
        
        self.messageTextEdit.newMessage(channel, value, level)
        
        # The client disconnected or connected...
        if channel == "connection":
            if value == "connected":
                self.connectionAction.setText("Disconnect")
                self.bluetoothConnected.setText("Connected")
                QtGui.QMessageBox.information(None, "Bluetooth", "Connected...", QtGui.QMessageBox.Ok)
            else:
                self.connectionAction.setText("Connect")
                self.bluetoothConnected.setText("Disonnected")
                QtGui.QMessageBox.information(None, "Bluetooth", "Disonnected...", QtGui.QMessageBox.Ok)
        # The server closed...
        elif channel == "close":
            self.bluetoothConnected.setText("Disonnected")
            self.bluetoothSendQueue.put(Message(channel="connection", value="disconnect"))
            QtGui.QMessageBox.information(None, "Bluetooth", "Server closed...", QtGui.QMessageBox.Ok)
        
        # Execute the function for this channel...
        elif channel in self.channels:
            self.channels[channel](value)
                
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
        self.messageTextEdit.setGeometry(self.getTextEditRect())
        
        # Update Robot widget size...
        self.robot_widget.setGeometry(self.getRobotImgRect())

    def closeEvent(self, event):
        """When the window close, close the server, too"""
        
        if self.bluetoothConnected.text() == "Connected":
            question = QtGui.QMessageBox.question(None, "Connection", "Close server?", "Yes", "No")

            # Close the server...
            if question == 0:
                self.bluetoothSendQueue.put(Message(channel="close"))
                
        
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
