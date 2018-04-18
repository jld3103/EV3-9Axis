#!/usr/bin/python3

# This widget displays the QTextEdit Commandline
# Author: Finn G.

from PyQt4 import QtGui,  QtCore
from constants import *
from logger import *

setLogLevel(logLevel)
        

class CommandLine(QtGui.QTextEdit):
    """This is a specific QTextEditor"""
    
    def __init__(self,  parent=None):
        super(CommandLine,  self).__init__(parent)

        self.parent = parent
        
        # Set font size...
        font = QtGui.QFont()
        font.setPointSize(12)
        self.setFont(font)
                
        
    def newMessage(self, message):
        """Insert a msg in the first line"""
        # Move cursor to the start...
        self.moveCursor(QtGui.QTextCursor.Start, 0)
        
        # Insert the 3 parts of the string in diffrent colors...
        self.insertHtml("<br><span style='color:red;'>%s: </span><span style='color:blue;'>%s</span><br>" % (message.channel, message.value))
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
                    self.moveCursor(QtGui.QTextCursor.Start, 0)
                return

        QtGui.QTextEdit.keyPressEvent(self,  event)
