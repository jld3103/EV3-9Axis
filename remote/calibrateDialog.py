# This is a dialog for calibrating the ev3...
# Author: Finn G.


from PyQt4 import QtCore, QtGui

from constants import *
from logger import *
from message import Message

setLogLevel(logLevel)

class CalibrateDialog(QtGui.QDialog):
    """Show dialog for selecting a bluetooth device"""

    def __init__(self, parent, mode):
        QtGui.QDialog.__init__(self, parent)

        self.setWindowTitle("Calibrate '%s'" % mode)
        self.setMinimumSize(QtCore.QSize(400, 314))
        self.setMaximumSize(QtCore.QSize(400, 314))

        self.mode = mode
        self.parent = parent

        # Get the current values...
        self.time = self.parent.settings.get("calibrate%sTime" % mode, default = 3000)
        self.speedR = self.parent.settings.get("calibrate%sSpeedR" % mode, default = 255)
        self.speedL = self.parent.settings.get("calibrate%sSpeedL" % mode, default = 255)

        # Set background color...
        p = self.palette()
        p.setColor(self.backgroundRole(), QtGui.QColor(255, 255, 255))
        self.setPalette(p)

        # Create the time slider...
        self.time_slider = QtGui.QSlider(QtCore.Qt.Vertical, self)
        self.time_slider.setGeometry(QtCore.QRect(180, 30, 31, 161))
        self.time_slider.setMinimum(1000)
        self.time_slider.setMaximum(5000)
        self.time_slider.setProperty("value", self.time)
        self.time_slider.valueChanged.connect(self.onTimeSlider)

        # Create the speed right slider...
        self.speedR_slider = QtGui.QSlider(QtCore.Qt.Vertical, self)
        self.speedR_slider.setGeometry(QtCore.QRect(280, 30, 31, 191))
        self.speedR_slider.setMinimum(200)
        self.speedR_slider.setMaximum(300)
        self.speedR_slider.setProperty("value", self.speedR)
        self.speedR_slider.valueChanged.connect(self.onSpeedRSlider)

        # Create the speed left slider...
        self.speedL_slider = QtGui.QSlider(QtCore.Qt.Vertical, self)
        self.speedL_slider.setGeometry(QtCore.QRect(80, 30, 31, 191))
        self.speedL_slider.setMinimum(200)
        self.speedL_slider.setMaximum(300)
        self.speedL_slider.setProperty("value", self.speedL)
        self.speedL_slider.valueChanged.connect(self.onSpeedLSlider)

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
        self.connect(self.btn_ok, QtCore.SIGNAL("clicked()"),  self.onOk)
        self.connect(self.btn_try, QtCore.SIGNAL("clicked()"),  self.onTry)

        # Create time lable...
        self.time_label = QtGui.QLabel(self)
        self.time_label.setGeometry(QtCore.QRect(170, 210, 41, 32))
        self.time_label.setAlignment(QtCore.Qt.AlignCenter)
        self.time_label.setText("Time\n(%d)" % self.time)

        # Create speed left lable...
        self.speedL_label = QtGui.QLabel(self)
        self.speedL_label.setGeometry(QtCore.QRect(60, 240, 71, 32))
        self.speedL_label.setAlignment(QtCore.Qt.AlignCenter)
        self.speedL_label.setText("Speed left\n(%d)" % self.speedL)

        # Create the speed right lable...
        self.speedR_label = QtGui.QLabel(self)
        self.speedR_label.setGeometry(QtCore.QRect(260, 240, 71, 32))
        self.speedR_label.setAlignment(QtCore.Qt.AlignCenter)
        self.speedR_label.setText("Speed right\n(%d)" % self.speedR)

    def onSpeedLSlider(self):
        """Set the speed left lable on the slider value"""
        self.speedL_label.setText("Speed left\n(%d)" % self.speedL_slider.value())

    def onSpeedRSlider(self):
        """Set the speed right lable on the slider value"""
        self.speedR_label.setText("Speed right\n(%d)" % self.speedR_slider.value())

    def onTimeSlider(self):
        """Set the time lable on the slider value"""
        self.time_label.setText("Time\n(%d)" % self.time_slider.value())

    def onOk(self):
        """Save the selected device"""
        self.parent.bluetooth.send(Message(channel = "calibrate%s" % self.mode, value = "%d:%d:%d" % (self.time_slider.value(), self.speedL_slider.value(), self.speedR_slider.value())))
        self.parent.settings.set("calibrate%sTime" % self.mode, self.time_slider.value())
        self.parent.settings.set("calibrate%sSpeedR" % self.mode, self.speedR_slider.value())
        self.parent.settings.set("calibrate%sSpeedL" % self.mode, self.speedL_slider.value())
        self.close()

    def onTry(self):
        """Close the dialog"""
        self.parent.bluetooth.send(Message(channel = "calibrate%s" % self.mode, value = "%d:%d:%d" % (self.time_slider.value(), self.speedL_slider.value(), self.speedR_slider.value())))
        self.parent.bluetooth.send(Message(channel = "calibrate%s" % self.mode, value = "test"))
