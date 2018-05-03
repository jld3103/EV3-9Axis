# This is a dialog to manage the channel filter in the command line...
# Author: Finn G.


from PyQt4 import QtCore, QtGui

from constants import *
from logger import *
from message import Message

setLogLevel(logLevel)

class FilterDialog(QtGui.QDialog):
    """Show dialog for selecting a bluetooth device"""

    def __init__(self, parent):
        QtGui.QDialog.__init__(self, parent)

        self.setWindowTitle("Channel filter")
        self.setMinimumSize(QtCore.QSize(404, 348))
        self.setMaximumSize(QtCore.QSize(404, 348))

        self.parent = parent
        
        # Get the current channels...
        self.channels = self.parent.settings.get("commandLineFilter", default = "").split("|")
        if len(self.channels[0]) == 0:
            self.channels = []

        # Set background color...
        p = self.palette()
        p.setColor(self.backgroundRole(), QtGui.QColor(255, 255, 255))
        self.setPalette(p)
        
        # Create line edit...
        self.input = QtGui.QLineEdit(self)
        self.input.setGeometry(QtCore.QRect(20, 20, 256, 31))
        
        # Create the list view...
        self.channes_listWidget = QtGui.QListWidget(self)
        self.channes_listWidget.setGeometry(QtCore.QRect(20, 55, 256, 271))
        self.channes_listWidget.addItems(self.channels)
        
        # Create the add button...
        self.add_button = QtGui.QPushButton(self)
        self.add_button.setGeometry(QtCore.QRect(290, 20, 93, 31))
        self.add_button.setText("Add")
        
        # Create the delete button...
        self.delete_button = QtGui.QPushButton(self)
        self.delete_button.setGeometry(QtCore.QRect(290, 55, 93, 31))
        self.delete_button.setText("Delete")
        
        # Create the ok button...
        self.ok_button = QtGui.QPushButton(self)
        self.ok_button.setGeometry(QtCore.QRect(290, 260, 93, 31))
        self.ok_button.setText("Ok")
        
        # Create the close button...
        self.close_button = QtGui.QPushButton(self)
        self.close_button.setGeometry(QtCore.QRect(290, 300, 93, 28))
        self.close_button.setText("Close")

        # Connect the buttons...
        self.connect(self.add_button, QtCore.SIGNAL("clicked()"),  self.onAdd)
        self.connect(self.delete_button, QtCore.SIGNAL("clicked()"),  self.onDelete)
        self.connect(self.ok_button, QtCore.SIGNAL("clicked()"),  self.onOk)
        self.connect(self.close_button, QtCore.SIGNAL("clicked()"),  self.onClose)


    def onAdd(self):
        """Add the input to the list of channels"""
        # Get the input...
        input = self.input.text().strip()
        
        # Add the item...
        self.channes_listWidget.addItem(input)
        
        # Reset the input...
        self.input.setText("")

    def onDelete(self):
        """Delete the slected channel"""
        # Get the selected line number...
        currentRow = self.channes_listWidget.currentRow()
        
        # Delete the line...
        self.channes_listWidget.takeItem(currentRow)
        
    def onOk(self):
        """Save the selected device"""
        # Create a string of all channels...
        channels = ""
        for index in range(self.channes_listWidget.count()):
             channels += self.channes_listWidget.item(index).text() + "|"
             
        # Delete the last lettre...
        channels = channels[:-1]
        
        # Update the settings...
        self.parent.settings.set("commandLineFilter", channels)
        
        # Close the dialog...
        self.close()

    def onClose(self):
        """Close the dialog"""
        # Close the dialog...
        self.close()
