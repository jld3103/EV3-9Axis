#!/usr/bin/python3

# This widget displays the QTextEdit Commandline
# Author: Finn G.

from PyQt4 import QtGui,  QtCore
from constants import *
from logger import *

setLogLevel(logLevel)
        

class MessageTextEdit(QtGui.QTextEdit):
    """This is a specific QTextEditor"""
    
    def __init__(self,  parent=None):
        super(MessageTextEdit,  self).__init__(parent)

        self.parent = parent
        
        # Set font size...
        font = QtGui.QFont()
        font.setPointSize(12)
        self.setFont(font)
                
    def nextLine(self):
        """Insert a new line at the top of the QTextEdit"""
        # Move cursor to the start...
        self.moveCursor(QtGui.QTextCursor.Start, 0)
        
        # Insert new line...
        self.insertHtml("<br>")
        self.moveCursor(QtGui.QTextCursor.Start, 0)
        
    def newMessage(self, message):
        """Insert a msg in the first line"""
        # Move cursor to the start...
        self.moveCursor(QtGui.QTextCursor.Start, 0)
        
        # Insert the 3 parts of the string in diffrent colors...
        self.insertHtml("<br><span style='color:red;'>%s: </span><span style='color:blue;'>%s</span><span style='color:green;'> (%d)</span>" % (message.channel, message.value, message.level))
        self.moveCursor(QtGui.QTextCursor.Start, 0)

    def keyPressEvent(self,  event):
        """When Return pressed, send the first line to MainWindow"""
        
        # check if the pressed key is return...
        if event.key() == QtCore.Qt.Key_Return:
            if event.modifiers() == QtCore.Qt.ControlModifier:
                event = QtCore.QKeyEvent(QtCore.QEvent.KeyPress,  QtCore.Qt.Key_Return, QtCore.Qt.NoModifier)
            else:
                firstLine = self.toPlainText().split("\n")[0].strip()
                if len(firstLine) > 0:
                    self.emit(QtCore.SIGNAL("sendMessage"), firstLine)
                    self.nextLine()
                return

        QtGui.QTextEdit.keyPressEvent(self,  event)
