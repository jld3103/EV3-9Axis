#!/usr/bin/python3

# This is the main file for the 3D Gui
# Author: Finn G.

version = "1.1"

from message import Message
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
    """Controls the window"""
    
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
        self.connectionAction = QtGui.QAction("&Connect", self)
        self.connectionAction.setStatusTip('Connect to EV3')
        self.connectionAction.triggered.connect(self.onConnection)
        bluetoothMenu.addAction(self.connectionAction)
        
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
            self.bluetoothSendQueue.put(Message(channel="connection", value="disconnect"))
        
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
        
    def closeEvent(self, event):
        """When the window close, close the server, too"""
        
        # If the bluetooth connection is disconnected, reconnect...
        if not self.bluetoothThread.isAlive():
            self.bluetoothThread = communication.BluetoothThread(self.bluetoothReciveQueue, self.bluetoothSendQueue)
            self.bluetoothThread.setName("BluetoothThread")
            self.bluetoothThread.start()
        
        # Close the server...
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
