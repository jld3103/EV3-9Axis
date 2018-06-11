# This is a dialog for calibrating the ev3...
# Author: Finn G.

from PyQt4 import QtCore, QtGui

from constants import *
from logger import *
from message import Message

setLogLevel(logLevel)


class CalibrateDialog(QtGui.QDialog):
    """Show dialog for selecting a bluetooth device"""

    def __init__(self, parent, mode, settings, units, sliderDifferences):
        QtGui.QDialog.__init__(self, parent)

        self.setWindowTitle("Calibrate '%s'" % mode)
        self.setMinimumSize(QtCore.QSize(400, 314))
        self.setMaximumSize(QtCore.QSize(400, 314))

        self.mode = mode
        self.parent = parent
        self.units = units
        self.sliders = []
        self.settingsKeys = []

        # Get the current settings...
        self.settings = []
        for setting, default in settings:
            self.settingsKeys.append(setting)
            self.settings.append(self.parent.settings.get(setting, default=default))

        # Set background color...
        p = self.palette()
        p.setColor(self.backgroundRole(), QtGui.QColor(255, 255, 255))
        self.setPalette(p)

        # Create the center slider...
        self.sliderCenter = QtGui.QSlider(QtCore.Qt.Vertical, self)
        self.sliderCenter.setGeometry(QtCore.QRect(180, 30, 31, 161))
        self.sliderCenter.setMinimum(sliderDifferences[2])
        self.sliderCenter.setMaximum(sliderDifferences[3])
        self.sliderCenter.setProperty("value", self.settings[0])
        self.sliderCenter.valueChanged.connect(self.onCenterSlider)
        self.sliders.append(self.sliderCenter)

        if mode != "Distance":
            # Create the speed right slider...
            self.sliderRight = QtGui.QSlider(QtCore.Qt.Vertical, self)
            self.sliderRight.setGeometry(QtCore.QRect(280, 30, 31, 191))
            self.sliderRight.setMinimum(sliderDifferences[0])
            self.sliderRight.setMaximum(sliderDifferences[1])
            self.sliderRight.setProperty("value", self.settings[1])
            self.sliderRight.valueChanged.connect(self.onRightSlider)
            self.sliders.append(self.sliderRight)
            
            if mode == "Forward":
                # Create the speed left slider...
                self.sliderLeft = QtGui.QSlider(QtCore.Qt.Vertical, self)
                self.sliderLeft.setGeometry(QtCore.QRect(80, 30, 31, 191))
                self.sliderLeft.setMinimum(sliderDifferences[0])
                self.sliderLeft.setMaximum(sliderDifferences[1])
                self.sliderLeft.setProperty("value", self.settings[2])
                self.sliderLeft.valueChanged.connect(self.onLeftSlider)
                self.sliders.append(self.sliderLeft)

        # Add Ok button...
        self.btn_ok = QtGui.QPushButton(self)
        self.btn_ok.setGeometry(10, 280, 371, 20)
        self.btn_ok.setText("OK")
        self.btn_ok.show()

        # Add Close button...
        self.btn_try = QtGui.QPushButton(self)
        self.btn_try.setGeometry(152, 247, 81, 21)
        self.btn_try.setText("Try")
        self.btn_try.show()

        # Connect buttons...
        self.connect(self.btn_ok, QtCore.SIGNAL("clicked()"), self.onOk)
        self.connect(self.btn_try, QtCore.SIGNAL("clicked()"), self.onTry)

        # Create time lable...
        self.labelCenter = QtGui.QLabel(self)
        self.labelCenter.setGeometry(QtCore.QRect(170, 210, 41, 32))
        self.labelCenter.setAlignment(QtCore.Qt.AlignCenter)
        self.labelCenter.setText("%s\n(%d)" % (self.units[0], self.settings[0]))
        
        if mode == "Distance":
            self.btn_try.setEnabled(False)
            self.labelCenter.setGeometry(QtCore.QRect(150, 210, 81, 32))

        else:
            #Create the speed right lable...
            self.labelRight = QtGui.QLabel(self)
            self.labelRight.setGeometry(QtCore.QRect(260, 240, 71, 32))
            self.labelRight.setAlignment(QtCore.Qt.AlignCenter)
            self.labelRight.setText("%s right\n(%d)" % (self.units[0], self.settings[1]))

            if mode == "Forward":
                # Create speed left lable...
                self.labelLeft = QtGui.QLabel(self)
                self.labelLeft.setGeometry(QtCore.QRect(60, 240, 71, 32))
                self.labelLeft.setAlignment(QtCore.Qt.AlignCenter)
                self.labelLeft.setText("%s left\n(%d)" % (self.units[0], self.settings[2]))

    def onLeftSlider(self):
        """Set the speed left lable on the slider value"""
        self.labelLeft.setText("%s left\n(%d)" % (self.units[2], self.sliderLeft.value()))

    def onRightSlider(self):
        """Set the speed right lable on the slider value"""
        self.labelRight.setText("%s right\n(%d)" % (self.units[1], self.sliderRight.value()))

    def onCenterSlider(self):
        """Set the time lable on the slider value"""
        self.labelCenter.setText("%s\n(%d)" % (self.units[0], self.sliderCenter.value()))

    def onOk(self):
        """Save the selected values in the settings"""
        calibrateString = ""
        for i in range(len(self.settings)):
            self.parent.settings.set(self.settingsKeys[i], self.sliders[i].value())
            calibrateString += str(self.sliders[i].value()) + ":"
        calibrateString = calibrateString[:-1]
        self.parent.bluetooth.send(Message(channel="calibrate%s" % self.mode, value=calibrateString))
        self.close()

    def onTry(self):
        """Close the dialog"""
        # Get all slider values...
        calibrateString = ""
        for i in range(len(self.settings)):
            calibrateString += str(self.sliders[i].value()) + ":"
        calibrateString = calibrateString[:-1]
        
        # Calibrate the ev3...
        self.parent.bluetooth.send(Message(channel="calibrate%s" % self.mode, value=calibrateString))
        
        # Try it out...
        self.parent.bluetooth.send(
            Message(
                channel="calibrate%s" % self.mode, value="test"))
