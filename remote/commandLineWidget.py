#!/usr/bin/python3

# This widget displays the QTextEdit Commandline
# Author: Finn G.

from PyQt4 import QtGui,  QtCore
from message import Message
from constants import *
from logger import *

setLogLevel(logLevel)


class CommandLine(QtGui.QTextEdit):
    """This is a specific QTextEditor"""

    def __init__(self,  parent, bluetooth):
        super(CommandLine,  self).__init__(parent)

        self.bluetooth = bluetooth

        # Set font size...
        font = QtGui.QFont()
        font.setPointSize(12)
        self.setFont(font)

        # Insert '>>> '...
        self.insertHtml("<span>>>> <span><br>")
        txtCursor = self.textCursor()
        txtCursor.setPosition(4)
        self.setTextCursor(txtCursor)

        # All messages...
        self.allMessages = [">>> "]
        self.currentMessage = 0

    def newMessage(self, message, sended = False):
        """Insert a message in the second line"""

        # Get first line of the QTextEdit
        firstLine = self.toPlainText().split("\n")[0]

        # Set the cursor to the start of the second line...
        txtCursor = self.textCursor()
        txtCursor.setPosition(len(firstLine)+1)
        self.setTextCursor(txtCursor)

        # Insert the message...
        if sended:
            self.insertHtml("<span>>>> </span><span style='color:green;'>%s: </span><span style='color:blue;'>%s</span><br>" % (message.channel, message.value))
        else:
            self.insertHtml("<span>>>> </span><span style='color:red;'>%s: </span><span style='color:blue;'>%s</span><br>" % (message.channel, message.value))
        
        # Set the cursor to the end of the first line...
        txtCursor.setPosition(len(firstLine))
        self.setTextCursor(txtCursor)

    def sendMessage(self, text):
        """Send the message to ev3"""
        info("Send message: %s" % text)

        # Split the text in channel and value...
        fragments = text.split(": ")

        # If channel and value exist spit them...
        if len(fragments) == 2:
            self.bluetooth.send(Message(channel = fragments[0], value = fragments[1]))
        else:
            self.bluetooth.send(Message(channel = fragments[0]))

    def selectFirstLine(self):
        """Select the first line of the QTextEdit"""

        # Get first line...
        firstLine = self.toPlainText().split("\n")[0]

        # Get cursor...
        cursor = self.textCursor()
        # Set first cursor position...
        cursor.setPosition(0)
        # Set second cursor position...
        cursor.setPosition(len(firstLine), QtGui.QTextCursor.KeepAnchor)
        # Set the cursor in the QTextEdit...
        self.setTextCursor(cursor)

    def keyPressEvent(self,  event):
        """Handle the keys"""

        # Check if the pressed key is return...
        if event.key() == QtCore.Qt.Key_Return:
            if event.modifiers() == QtCore.Qt.ControlModifier:
                event = QtCore.QKeyEvent(QtCore.QEvent.KeyPress,  QtCore.Qt.Key_Return, QtCore.Qt.NoModifier)
            else:
                # Get first line...
                firstLine = self.toPlainText().split("\n")[0].strip()
                if len(firstLine) > 0:
                    # Send the message...
                    self.sendMessage(firstLine[3:])
                    # Insert a new line...
                    self.moveCursor(QtGui.QTextCursor.Start, 0)
                    self.insertHtml("<br>")
                    self.moveCursor(QtGui.QTextCursor.Start, 0)
                    self.insertHtml("<span>>>> <span>")
                    # Update messages...
                    if firstLine in self.allMessages:
                        del self.allMessages[self.allMessages.index(firstLine)]
                    self.allMessages.insert(0, firstLine)
                    self.currentMessage = 0
                return

        # If the pressed key is key up, take one of the last messages...
        elif event.key() == QtCore.Qt.Key_Up:
            if self.currentMessage == 0:
                self.allMessages[-1] =  self.toPlainText().split("\n")[0]
            if len(self.allMessages) != 0:
                self.selectFirstLine()
                self.insertHtml("<span>%s</span>" % self.allMessages[self.currentMessage])
                # Update current message...
                self.currentMessage += 1
                if self.currentMessage >= len(self.allMessages):
                    self.currentMessage = 0
            return

        # If the pressed key is key down, take one of the last messages...
        elif event.key() == QtCore.Qt.Key_Down:
            if len(self.allMessages) != 0:
                self.selectFirstLine()
                self.insertHtml("<span>%s</span>" % self.allMessages[self.currentMessage])
                # Update current message...
                self.currentMessage -= 1
                if self.currentMessage * -1 > len(self.allMessages):
                    self.currentMessage = -1
            return

        # Always allow key left and right...
        elif event.key() == QtCore.Qt.Key_Left:
            pass
        elif event.key() == QtCore.Qt.Key_Right:
            pass

        # Ignore backspace outsite the write area...
        elif event.key() == QtCore.Qt.Key_Backspace:
            firstLine = self.toPlainText().split("\n")[0]
            if self.textCursor().position() < 5 or self.textCursor().position() > len(firstLine):
                return

        # Ignore all keys outside the write area...
        else:
            # If the cursor is not in the edit area, ignore all key events...
            firstLine = self.toPlainText().split("\n")[0]
            if self.textCursor().position() < 4 or self.textCursor().position() > len(firstLine):
                return

        # Set selection...
        firstLine = self.toPlainText().split("\n")[0]
        if self.textCursor().anchor() < 4:
             # Get cursor...
            cursor = self.textCursor()
            # Set second cursor position...
            cursor.setPosition(4, QtGui.QTextCursor.MoveAnchor)
            self.setTextCursor(cursor)
        elif self.textCursor().anchor() > len(firstLine):
             # Get cursor...
            cursor = self.textCursor()
            # Set second cursor position...
            cursor.setPosition(len(firstLine), QtGui.QTextCursor.MoveAnchor)
            self.setTextCursor(cursor)
            

        # Give Qt the signal...
        QtGui.QTextEdit.keyPressEvent(self,  event)
