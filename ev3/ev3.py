# This file control the EV3
# Author: Finn G., Jan-Luca D.

import ev3dev.ev3 as ev3
import ev3.ev3Communication as communication
import ev3.MPU9250 as MPU9250
from message import Message
from constants import *
from logger import *
import queue
import time

class EV3:
    """Controls the EV3"""

    def __init__(self):

        # Init screen...
        self.screen = ev3.Screen()

        self.orientation = 0 # Top: 0 / Right: 1 / Bottom: 2 / Left: 3
        self.current = (0, 0)

        # Calibration data
        self.cFT = 3000 # cFT = CalibrateForwardTime
        self.cFL = 255
        self.cFR = 255

        self.cLT = 3000
        self.cLL = 255
        self.cLR = 255

        self.cRT = 3000
        self.cRL = 255
        self.cRR = 255

        # Init all sensors...
        self.touchSensor = ev3.TouchSensor()
        self.infraredSensor = ev3.InfraredSensor()
        self.colorSensor = ev3.ColorSensor()
        self.ultraSensor = ev3.UltrasonicSensor()
        #self.mpu9250 = MPU9250.MPU9250()

        # Init all motors...
        self.motorR = ev3.LargeMotor("outC")
        self.motorL = ev3.LargeMotor("outA")

        # Create the queues for the bluetooth data...
        self.bluetoothReciveQueue = queue.Queue()

        # Start the Thread for the bluetooth connection...
        self.bluetooth = communication.BluetoothThread(self.receivedData)
        self.bluetooth.setName("BluetoothThread")
        self.bluetooth.start()

        # Add bluetooth listener...
        self.bluetooth.addListener("touchSensor", self.sendTouchValue)
        self.bluetooth.addListener("infraredSensor", self.sendInfraredValue)
        self.bluetooth.addListener("ultraSensor", self.sendUltraValue)
        self.bluetooth.addListener("distanceSensor", self.sendDistanceValue)
        self.bluetooth.addListener("colorSensor", self.sendColorValue)
        self.bluetooth.addListener("screen", self.drawScreen)
        self.bluetooth.addListener("motorR", self.turnRight)
        self.bluetooth.addListener("motorL", self.turnLeft)
        self.bluetooth.addListener("accel", self.sendAccelData)
        self.bluetooth.addListener("gyro", self.sendGyroData)
        self.bluetooth.addListener("mag", self.sendMagData)
        self.bluetooth.addListener("close", self.close)
        self.bluetooth.addListener("calibrateForward", self.calibrateForward)
        self.bluetooth.addListener("calibrateLeft", self.calibrateLeft)
        self.bluetooth.addListener("calibrateRight", self.calibrateRight)
        self.bluetooth.addListener("path", self.path)
        self.bluetooth.addListener("current", self.setCurrent)

    def calibrateForward(self, data):
        if data == "test":
            info("Testing forward...")
            self._1Forward()
        else:
            data = data.split(":")
            self.cFT = int(data[0])
            self.cFL = int(data[1])
            self.cFR = int(data[2])
        return ("calibrateForward", "Success")

    def calibrateLeft(self, data):
        if data == "test":
            info("Testing left...")
            self._90Left()
        else:
            data = data.split(":")
            self.cLT = int(data[0])
            self.cLL = int(data[1])
            self.cLR = int(data[2])
        return ("calibrateLeft", "Success")

    def calibrateRight(self, data):
        if data == "test":
            info("Testing right...")
            self._90Right()
        else:
            data = data.split(":")
            self.cRT = int(data[0])
            self.cRL = int(data[1])
            self.cRR = int(data[2])
        return ("calibrateRight", "Success")

    def _1Forward(self):
        """Drive one square forward"""
        info("1 forward")
        
        # Run the motors...
        self.motorR.run_timed(time_sp = self.cFT, speed_sp = self.cFR)
        self.motorL.run_timed(time_sp = self.cFT, speed_sp = self.cFL)
        
        # Wait until the motors stop...
        while self.motorR.is_running or self.motorL.is_running:
            time.sleep(0.1)
            

    def _90Left(self):
        """Turn 90° left"""
        info("90 left")
        
        # Run the motors...
        self.motorR.run_timed(time_sp = self.cLT, speed_sp = -self.cLR)
        self.motorL.run_timed(time_sp = self.cLT, speed_sp = self.cLL)
        
        # Wait until the motors stop...
        while self.motorR.is_running or self.motorL.is_running:
            time.sleep(0.1)

    def _90Right(self):
        """Turn 90° right"""
        info("90 right")
        
        # Run the motors...
        self.motorR.run_timed(time_sp = self.cRT, speed_sp = self.cRR)
        self.motorL.run_timed(time_sp = self.cRT, speed_sp = -self.cRL)
        
        # Wait until the motors stop...
        while self.motorR.is_running or self.motorL.is_running:
            time.sleep(0.1)

    def setCurrent(self, value):
        """Set the current square"""
        values = value.split(":")
        self.current = (int(values[0]), int(values[1]))
        self.orientation = int(values[2])
        return ("current", value)

    def path(self, value):
        """Listen to the path commands"""

        commands = value.split("|")

        # Execute all command for this path...
        for command in commands:
            channel = command.split(":")[0]
            value = command.split(":")[1]

            # If the channel is 'forward', drive the number of squares forward...
            if channel == "forward":
                for i in range(int(value)):
                    self._1Forward()
                    x = int(self.current[0])
                    y = int(self.current[1])
                    o = self.orientation
                    if o == 0:
                        y -= 1
                    elif o == 1:
                        x += 1
                    elif o == 2:
                        y += 1
                    elif o == 3:
                        x -= 1
                    self.current = (x, y)
                    self.bluetooth.send(Message(channel = "current",  value = "%d:%d:%d" % (self.current[0], self.current[1], self.orientation)))
            # If the channel is 'turn', turn the robot to position...
            elif channel == "turn":
                value = int(value)
                if self.orientation < value:
                    for i in range(value - self.orientation):
                        self._90Right()
                        self.orientation += 1
                        self.bluetooth.send(Message(channel = "current",  value = "%d:%d:%d" % (self.current[0], self.current[1], self.orientation)))
                else:
                    for i in range(self.orientation - value):
                        self._90Left()
                        self.orientation -= 1
                        self.bluetooth.send(Message(channel = "current",  value = "%d:%d:%d" % (self.current[0], self.current[1], self.orientation)))
                self.orientation = value
                

        return ("path", "Success")

    def receivedData(self, function, value):
        """Execute the listener for the channel"""

        # Check if the mode is updating...
        updating = value.split(":")[0] == "update"

        # Notice the old value...
        oldValue = None

        while self.bluetooth.connected:
            # Get the value...
            data = function(value)
            if len(data) > 1:
                channel, value = data
            else:
                channel = data[0]
                value = None

            # If the value is not the same like the last time, send the value to the remote...
            if value != oldValue:
                oldValue = value
                self.bluetooth.send(Message(channel = channel,  value = value))

            # If the mode is not updating, send the data only once...
            if not updating:
                break

            # Wait for 0.1 seconds (TODO: Set interval from the remote)
            time.sleep(0.1)

    def close(self, value):
        """Close the bluetooth server"""

        # Close the bluetooth server...
        self.bluetooth.closeServer()

        # Close all running threads...
        global alive
        alive = False

        return ("close", "Closed server")

    def drawScreen(self, value):
        """Draw point on the screen"""
        points = value.split(":")
        for point in points:
            try:
                x = int(point.split("|")[0])
                y = int(point.split("|")[1])
            except:
                return ("screen",  "Value has wrong format (x|y:x|y:...)")
            self.screen.draw.point((x, y))
        self.screen.update()
        return ("screen",  "Success")

    def forward(self, value):
        """Move forward"""
        # Get time and speed...
        fragments = value.split(":")
        time = int(fragments[0].strip())
        speed = int(fragments[1].strip())

        # Run the motor...
        try:
            self.motorR.run_timed(time_sp = time, speed_sp = speed)
            self.motorL.run_timed(time_sp = time, speed_sp = speed)
            return ("motorRL", "%d:%d" % (time, speed))
        except:
            return ("motorRL",  "Device not connected")

    def rotate(self, value):
        """Rotate around itself"""
        # Get time and speed...
        fragments = value.split(":")
        time = int(fragments[0].strip())
        speed = int(fragments[1].strip())

        # Run the motor...
        try:
            self.motorR.run_timed(time_sp = time, speed_sp = -speed)
            self.motorL.run_timed(time_sp = time, speed_sp = speed)
            return ("motorRL", "%d:%d" % (time, speed))
        except:
            return ("motorRL",  "Device not connected")

    def turnRight(self, value):
        """Turn the right motor"""
        # Get time and speed...
        fragments = value.split(":")
        time = int(fragments[0].strip())
        speed = int(fragments[1].strip())

        # Run the motor...
        try:
            self.motorR.run_timed(time_sp = time, speed_sp = speed)
            return ("motorR", "%d:%d" % (time, speed))
        except:
            return ("motorR",  "Device not connected")

    def turnLeft(self, value):
        """Turn the left motor"""
        # Get time and speed...
        fragments = value.split(":")
        time = int(fragments[0].strip())
        speed=int(fragments[1].strip())

        # Run the motor...
        try:
            self.motorL.run_timed(time_sp = time, speed_sp = speed)
            return ("motorL", "%d:%d" % (time, speed))
        except:
            return ("motorL", "Device not connected")

    def sendColorValue(self, value):
        """Send the value of the color sensor"""
        if value == "color":
            try:
                color = self.colorSensor.COLORS[self.colorSensor.color]
                return ("colorSensor", color)
            except:
                return ("colorSensor", "Device not connected")
        else:
            try:
                red = self.colorSensor.red
                green = self.colorSensor.green
                blue = self.colorSensor.blue
                return ("colorSensor", "%d:%d:%d" % (red, green, blue))
            except:
                return ("colorSensor", "Device not connected")

    def sendInfraredValue(self, value):
        """Send the value of the infrared sensor"""
        try:
            value = int(self.infraredSensor.value() * 25.5)
            return ("infraredSensor",  value)
        except:
            return ("infraredSensor",  "Device not connected")

    def sendUltraValue(self, value):
        """Send the value of the ultra sensor"""
        try:
            value = self.ultraSensor.value()
            return ("ultraSensor",  value)
        except:
            return ("ultraSensor",  "Device not connected")

    def sendDistanceValue(self, value):
        """Send the value of the ultra or infrared sensor"""
        data = self.sendUltraValue(None)
        if data[1] == "Device not connected":
            data = self.sendInfraredValue(None)
            if data[1] == "Device not connected":
                return ("distanceSensor", data[1])
        return ("distanceSensor", data[1])

    def sendTouchValue(self, value):
        """Send the value of the touch sensor"""
        try:
            value = self.touchSensor.value()
            return ("touchSensor",  value)
        except:
            return ("touchSensor",  "Device not connected")

    def sendAccelData(self, value):
        """Send the values of the accelometer"""
        accel = mpu9250.readAccel()
        return ("accel", "%f:%f:%f" % (accel["x"], accel["y"], accel["z"]))

    def sendGyroData(self, value):
        """Send the values of the gyroscope"""
        gyro = mpu9250.readGyro()
        return ("gyro", "%f:%f:%f" % (gyro["x"], gyro["y"], gyro["z"]))

    def sendMagData(self, value):
        """Send the values of the magnetometer"""
        mag = mpu9250.readMagnet()
        return ("mag", "%f:%f:%f" % (mag["x"], mag["y"], mag["z"]))
