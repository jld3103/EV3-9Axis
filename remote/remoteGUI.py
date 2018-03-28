#!/usr/bin/python3

# This is the main file for the 3D Gui
# Author: Finn G.

version = "1.0"

import remote.remoteCommunication as communication
import queue
from PyQt4 import QtGui,  QtCore
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
        
class MessageTextEdit(QtGui.QTextEdit):
    """This is a specific QTextEditor"""
    
    def __init__(self,  parent):
        super(MessageTextEdit,  self).__init__(parent)

        self.parent = parent
        
        # Set font size...
        font = QtGui.QFont()
        font.setPointSize(12)
        self.setFont(font)
        
    def nextLine(self):
        """Insert a new line in the start of the QTextEdit"""
        # Move cursor to the start...
        self.moveCursor(QtGui.QTextCursor.Start, 0)
        # Insert new line...
        self.insertHtml("<br>")
        self.moveCursor(QtGui.QTextCursor.Start, 0)
        
    def newMessage(self, channel, value, level):
        """Insert a msg in the first line"""
        # Move cursor to the start...
        self.moveCursor(QtGui.QTextCursor.Start, 0)
        
        # Insert the 3 parts of the strin in diffrent colors...
        self.insertHtml("<br><span style='color:red;'>%s: </span><span style='color:blue;'>%s</span><span style='color:green;'> (%d)</span>" % (channel, value, level))
        self.moveCursor(QtGui.QTextCursor.Start, 0)

    def keyPressEvent(self,  event):
        """When Return pressed, send the first line to MainWindow"""
        # check if the pressed key is return...
        if event.key() == QtCore.Qt.Key_Return:
            if event.modifiers() == QtCore.Qt.ControlModifier:
                event = QtCore.QKeyEvent(QEvent.KeyPress,  Qt.Key_Return,Qt.NoModifier)
            else:
                self.emit(QtCore.SIGNAL("sendMessage"), self.toPlainText().split("\n")[0].strip())
                self.nextLine()
                return

        QtGui.QTextEdit.keyPressEvent(self,  event)

class MainWindow(QtGui.QMainWindow):
    """Stellt die Hauptbenutzeroberfläche dar"""
    
    bluetoothEvent = QtCore.pyqtSignal(str, str, int)
    
    def __init__(self, version, parent=None):
        QtGui.QMainWindow.__init__(self, parent=None)
        
        # Set the window title...
        self.setWindowTitle("EV3 Gui - v%s" % (version))
        
        # Set window size...
        self.resize(630, 420)
        self.setMinimumSize(QtCore.QSize(630, 420))
        
        # Set background color...
        self.menubarHeight = 26
        palette = self.palette()
        palette.setColor(self.backgroundRole(), QtCore.Qt.white)
        self.setPalette(palette)
        
        # Create statusbar...
        self.statusBar = self.statusBar()
        self.statusBar.setGeometry(QtCore.QRect(0, self.size().height()-self.menubarHeight, self.size().width(), self.size().height()-self.menubarHeight))
        self.bluetoothConnected = QtGui.QLabel("Disonnected")
        self.statusBar.addPermanentWidget(self.bluetoothConnected)
        
        # Create menubar....
        mainMenu = self.menuBar()
        mainMenu.setGeometry(QtCore.QRect(0, 0, self.size().width(), self.menubarHeight))
        bluetoothMenu = mainMenu.addMenu('&Bluetooth')
        connectAction = QtGui.QAction("&Connect", self)
        connectAction.setStatusTip('Connect to EV3')
        connectAction.triggered.connect(self.onConnect)
        bluetoothMenu.addAction(connectAction)
        
        # Create the images for drawing...
        roomImgSize = QtCore.QSize(self.size().width()*0.7, self.size().height()-(self.menubarHeight*2))
        self.room_image = QtGui.QImage(roomImgSize, QtGui.QImage.Format_RGB32)
        self.room_image.fill(QtGui.qRgb(150, 150, 150))
        robotImgSize = QtCore.QSize(self.size().width()*0.3, self.size().width()*0.3)
        self.robot_image = QtGui.QImage(robotImgSize, QtGui.QImage.Format_RGB32)
        self.robot_image.fill(QtGui.qRgb(150, 150, 150))
        
        # Create the command line...
        self.messageTextEdit = MessageTextEdit(self)
        self.messageTextEdit.setGeometry(QtCore.QRect(self.size().width()*0.7, self.size().width()*0.3, self.size().width()-self.size().width()*0.7, self.size().height()-self.menubarHeight-self.size().width()*0.3))
        self.connect(self.messageTextEdit, QtCore.SIGNAL("sendMessage"),  self.onSendMessage)
        
        # create the queues for the bluetooth data...
        self.bluetoothReciveQueue = queue.Queue()
        self.bluetoothSendQueue = queue.Queue()
        
        # Connect the bluetoothEvent signal...
        self.bluetoothEvent.connect(self.onBluetoothEvent)
        
        # start the bluetoothThread...
        bluetoothReciveThread = BluetoothReciveThread(self.bluetoothReciveQueue, self.bluetoothEvent)
        bluetoothReciveThread.setName("BluetoothReciveThread")
        bluetoothReciveThread.start()
        
        # start the Thread for the bluetooth connection...
        bluetoothThread = communication.BluetoothThread(self.bluetoothReciveQueue, self.bluetoothSendQueue)
        bluetoothThread.setName("BluetoothThread")
        bluetoothThread.start()
        
    def onSendMessage(self, text):
        info("send msg: %s" % text)
        self.bluetoothSendQueue.put(Message(channel="user input", value=text))
        
    def onConnect(self):
        """Handle the connect action in the menubar"""
        pass
        
    @QtCore.pyqtSlot(str, str, int)
    def onBluetoothEvent(self, channel, value, level):
        """Handle the bluetooth events"""
        
        self.messageTextEdit.newMessage(channel, value, level)
        
        if channel == "connection":
            if value == "connected":
                self.bluetoothConnected.setText("Connected")
            else:
                self.bluetoothConnected.setText("Disonnected")
                
    def paintEvent(self, event):
        """Paint the window."""
        
        # Calculate the image sizes....
        xPositionRobot = self.size().width()*0.7 + 1
        rectRobot = QtCore.QRect(xPositionRobot, self.menubarHeight, self.size().width()*0.3, self.size().width()*0.3)
        xPositionRoom = self.size().width()*0.7
        yPositionRoom = self.size().height() - self.menubarHeight *2
        rectRoom = QtCore.QRect(0, self.menubarHeight,  xPositionRoom, yPositionRoom)
        
        # Paint the images...
        painter = QtGui.QPainter(self)
        painter.drawImage(rectRobot, self.robot_image)
        painter.drawImage(rectRoom, self.room_image)
        
        # Draw parting line...
        painter.drawLine(xPositionRoom, self.menubarHeight, xPositionRoom, self.size().height() - self.menubarHeight-1)

    def resizeEvent(self, event):
        """Called if the windowsize changed"""
        
        # Uptdata TextEdit size...
        self.messageTextEdit.setGeometry(QtCore.QRect(self.size().width()*0.7, self.size().width()*0.3, self.size().width()-self.size().width()*0.7, self.size().height()-self.menubarHeight-self.size().width()*0.3))

        # Create a new image with new size and re-draw the rail network
        roomImgSize = QtCore.QSize(self.size().width()*0.7, self.size().height()-(self.menubarHeight*2))
        self.room_image = QtGui.QImage(roomImgSize, QtGui.QImage.Format_RGB32)
        self.room_image.fill(QtGui.qRgb(150, 150, 150))
        robotImgSize = QtCore.QSize(self.size().width()*0.3, self.size().width()*0.3)
        self.robot_image = QtGui.QImage(robotImgSize, QtGui.QImage.Format_RGB32)
        self.robot_image.fill(QtGui.qRgb(150, 150, 150))
        
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
