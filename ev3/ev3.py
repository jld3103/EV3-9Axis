# This file controls the EV3
# Author: Finn G., Jan-Luca D.

print("Importing libraries...")
import queue
import time

import ev3.ev3Communication as communication
import ev3.MPU9250 as MPU9250
import ev3dev.ev3 as ev3
from constants import *
from logger import *
from message import Message

setLogLevel(logLevel)

class EV3:
    """Controls the EV3"""

    def __init__(self):

        # Init screen...
        self.screen = ev3.Screen()

        self.orientation = 0  # Top: 0 / Right: 1 / Bottom: 2 / Left: 3
        self.current = (0, 0)
        
        self.runningPath = False
        self.stopPath = False

        # Calibration data
        self.calibrateForwardTime = 3000
        self.calibrateForwardLeft = 255
        self.calibrateForwardRight = 255
        self.calibrateWallDistance = 2300
        self.calibrateLeftSpeed = 60
        self.calibrateLeftDegrees = -90
        self.calibrateRightSpeed = 60
        self.calibrateRightDegrees = 90

        # Init all sensors...
        self.touchSensor = ev3.TouchSensor()
        self.infraredSensor = ev3.InfraredSensor()
        self.colorSensor = ev3.ColorSensor()
        self.ultraSensor = ev3.UltrasonicSensor()
        self.gyroSensor = ev3.GyroSensor()
        self.mpu9250 = MPU9250.MPU9250()

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
        self.bluetooth.addListener("motorR", self.turnRight)
        self.bluetooth.addListener("motorL", self.turnLeft)
        self.bluetooth.addListener("accel", self.sendAccelData)
        #self.bluetooth.addListener("gyro", self.sendGyroData)
        self.bluetooth.addListener("mag", self.sendMagData)
        self.bluetooth.addListener("temp", self.sendTemData)
        self.bluetooth.addListener("close", self.close)
        self.bluetooth.addListener("calibrateForward", self.calibrateForward)
        self.bluetooth.addListener("calibrateDistance", self.calibrateDistance)
        self.bluetooth.addListener("calibrateRight", self.calibrateRight)
        self.bluetooth.addListener("calibrateLeft", self.calibrateLeft)
        self.bluetooth.addListener("path", self.path)
        self.bluetooth.addListener("current", self.setCurrent)
        self.bluetooth.addListener("gyroSensor", self.sendGyroValue)

    def receivedData(self, function, value):
        """Execute the listener for the channel"""

        # Check if the mode is updating...
        updating = value.split(":")[0] == "update"

        # Notice the old value...
        oldValue = None

        while self.bluetooth.connected:
            # Get the value...
            data = function(value)
            if data == None:
                break
            elif len(data) > 1:
                channel, value = data
            else:
                channel = data[0]
                value = None

            # If the value is not the same like the last time, send the value to the remote...
            if value != oldValue:
                oldValue = value
                self.bluetooth.send(Message(channel=channel, value=value))

            # If the mode is not updating, send the data only once...
            if not updating:
                break

            # Wait for 0.1 seconds (TODO: Set interval from the remote)
            time.sleep(0.1)
            
    def sendGyroValue(self, data):
        """Send the gyro value to the remote"""
        try:
            return ("gyroSensor", self.gyroSensor.value())
        except:
            self.gyroSensor = ev3.GyroSensor()
            return ("gyroSensor", "Device not connected")

    def calibrateForward(self, data):
        """Calibrate the time and speed to drive forward"""
        if data == "test":
            info("Testing forward...")
            self._1Forward()
        else:
            data = data.split(":")
            self.calibrateForwardTime = int(data[0])
            self.calibrateForwardLeft = int(data[2])
            self.calibrateForwardRight = int(data[1])
            info("Got calibrating data for forward: " + str.join(":", data))
        return ("calibrateForward", "Success")
        
    def calibrateRight(self, data):
        """Calibrate the time and speed to drive forward"""
        if data == "test":
            info("Testing right...")
            self.turn(self.calibrateRightSpeed, self.calibrateRightDegrees)
        else:
            data = data.split(":")
            self.calibrateRightSpeed = int(data[0])
            self.calibrateRightDegrees = int(data[1])
            info("Got calibrating data for right: " + str.join(":", data))
        return ("calibrateRight", "Success")
    
    def calibrateLeft(self, data):
        """Calibrate the time and speed to drive forward"""
        if data == "test":
            info("Testing left...")
            self.turn(self.calibrateLeftSpeed, self.calibrateLeftDegrees)
        else:
            data = data.split(":")
            self.calibrateRightSpeed = int(data[0])
            self.calibrateRightDegrees = int(data[1])
            info("Got calibrating data for left: " + str.join(":", data))
        return ("calibrateLeft", "Success")

    def calibrateDistance(self, data):
        """Calibrate the maximum distance to detect an obstacle"""
        if data == "test":
            print("Testing distance...")
            self.isWall()
        else:
            self.calibrateWallDistance = int(data)
            info("Got calibrating data for distance: " + data)
            return ("calibrateDistance", "Success")
        
    def turn(self, speed, degrees):
        """Turn the robot by the given number of degrees"""
        
        startOrientation = "Device not connected"
        while startOrientation == "Device not connected":
            startOrientation = self.sendGyroValue(None)[1]
            if startOrientation == "Device not connected":
                time.sleep(0.1)
        aimOrientation = startOrientation + degrees
        driving = 0 # -1: turning right; 0: not turning; 1: turning left; -10: turning back to start orientation
        result = "success"
        while True:
            # Get the current orientation...
            orientation = "Device not connected"
            while orientation == "Device not connected":
                orientation = self.sendGyroValue(None)[1]
            if speed < 0:
                if speed < -1050:
                    speed = -1050
            else:
                if speed > 1050:
                    speed = 1050
            # If the current orientation is bigger than the aim orientation and the robot is not turning left already turn left...
            if orientation > aimOrientation and driving != 1:
                self.motorR.run_forever(speed_sp = speed)
                self.motorL.run_forever(speed_sp = -speed)
                driving = 1
            # If the current orientation is smaler than the aim orientation and the robot is not turning left already turn right...
            elif orientation < aimOrientation and driving != -1:
                self.motorR.run_forever(speed_sp = -speed)
                self.motorL.run_forever(speed_sp = speed)
                driving = -1
            # If the current orientation is the aim orientation stop turning...
            elif orientation == aimOrientation:
                self.motorR.stop()
                self.motorL.stop()
                break
                
            if self.stopPath:
                # Stop the motors...
                self.motorR.stop()
                self.motorL.stop()
                driving = -10
                result = "stopped"
                
                aimOrientation = startOrientation
                    
            # Check if the touch sensor is pressed...
            if driving != -10:
                tsValue = self.sendTouchValue(None)[1]
                if tsValue == "Device not connected":
                    continue
                elif tsValue:
                    # Stop the motors...
                    self.motorR.stop()
                    self.motorL.stop()
                    driving = -10
                    result = "error"
                    
                    aimOrientation = startOrientation
                    
        return result

    def _1Forward(self, orientation = None):
        """Drive one square forward"""
        info("1 forward")
        
        # Notice the current orientation...
        if orientation == None:
            orientation = "Device not connected"
            while orientation == "Device not connected":
                orientation = self.sendGyroValue(None)[1]
                if orientation == "Device not connected":
                    time.sleep(0.1)

        # Notice the current tacho Spostion...
        absPositionR = self.motorR.position
        absPositionL = self.motorL.position
        
        # Run the motors...
        self.motorR.run_timed(time_sp=self.calibrateForwardTime, speed_sp=self.calibrateForwardRight)
        self.motorL.run_timed(time_sp=self.calibrateForwardTime, speed_sp=self.calibrateForwardLeft)
        mode = "forward"
        result = "success"
        # Wait until the motors stop...
        while self.motorL.is_running:
            tsValue = self.sendTouchValue(None)[1]
            if tsValue == "Device not connected":
                time.sleep(0.1)
                continue
            currentOrientation = self.sendGyroValue(None)[1]
            if currentOrientation == "Device not connected":
                time.sleep(0.1)
                continue
                
            # If the touch sensor is pressed or the path is stopped drive back to start position...
            if tsValue or self.stopPath:
                # Stop turning...
                self.motorR.stop()
                self.motorL.stop()
                result = "failed"
                if self.stopPath:
                    self.stopPath = False
                    result = "stopped"
                # Drive to old postion...
                self.motorR.run_to_abs_pos(position_sp=absPositionR, speed_sp=self.calibrateForwardRight)
                self.motorL.run_to_abs_pos(position_sp=absPositionL, speed_sp=self.calibrateForwardLeft)
                mode = "backward"
            
            #TODO: This is the correction with the gyro sensor, but it's not very helpful yet...
            # Set the speed of the right motor to drive forward...
#            if mode == "forward":
#                newSpeed = self.calibrateForwardRight + (currentOrientation-orientation) * 10
#                self.motorR.run_forever(speed_sp=newSpeed)
                
            time.sleep(0.1)
            
        #self.motorR.stop()

        return result
        
    def isWall(self):
        """Check if the next square is a wall"""
        distance = self.sendDistanceValue(None)[1]
        if distance != "Device not connected":
            if distance <= self.calibrateWallDistance:
                info("There is a wall")
                return True
        else:
            error(
                "Cannot check if there is a wall (Distance sensor not connected)"
            )
            return False
        info("There is no wall")
        return False

    def setCurrent(self, value):
        """Set the current square"""
        values = value.split(":")
        self.current = (int(values[0]), int(values[1]))
        self.orientation = int(values[2])
        return ("current", value)

    def getNextSquare(self):
        """Returns the next square"""

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

        return x, y

    def path(self, value):
        """Listen to the path commands"""
        
        if value.strip() == "stop":
            self.stopPath = True
            info("Stop path")
            return
        
        # Wait until the old path is excecuted...
        while self.runningPath:
            time.sleep(0.1)
            
        self.runningPath = True
        self.stopPath = False
        commands = value.split("|")

        # Execute all command for this path...
        for command in commands:
            channel = command.split(":")[0]
            value = command.split(":")[1]

            # If the channel is 'forward', drive the number of squares forward...
            if channel == "forward":
                # Get current orientation...
                orientation = "Device not connected"
                while orientation == "Device not connected":
                    orientation = self.sendGyroValue(None)[1]
                    time.sleep(0.1)
                    
                for i in range(int(value)):
                    # Ckeck if there is a wall...
                    if self.isWall():
                        self.bluetooth.send(Message(channel="wall", value="%d:%d" % self.getNextSquare()))
                        self.runningPath = False
                        return ("path", "failed")
                    move = self._1Forward(orientation = orientation)
                    # Check if 1Forard was successfull...
                    if move != "success":
                        self.bluetooth.send(Message(channel="wall", value="%d:%d" % self.getNextSquare()))
                        self.runningPath = False
                        return ("path", move)
                    
                    # Get next position...
                    self.current = self.getNextSquare()
                    self.bluetooth.send(Message(channel="current", value="%d:%d:%d" % (self.current[0], self.current[1], self.orientation)))
                    
            # If the channel is 'turn', turn the robot to position...
            elif channel == "turn":
                value = int(value)
                newOrientation = self.orientation
                while newOrientation != value:
                    # Turn in the correct dircection...
                    if newOrientation == 3 and value == 0:
                        move = self.turn(self.calibrateRightSpeed, -self.calibrateRightDegrees)
                        newOrientation = 0
                    elif newOrientation == 0 and value == 3:
                        move = self.turn(self.calibrateLeftSpeed, self.calibrateLeftDegrees)
                        newOrientation = 3
                    elif newOrientation < value:
                        move = self.turn(self.calibrateRightSpeed, -self.calibrateRightDegrees)
                        newOrientation += 1
                    elif newOrientation > value:
                        move = self.turn(self.calibrateLeftSpeed, self.calibrateLeftDegrees)
                        newOrientation -= 1
                    # Check if the turning failed...
                    if  move != "success":
                        self.runningPath = False
                        return ("path", move)
                    
                    # Set the new orientation...
                    self.orientation = newOrientation
                        
                    # Inform the GUI...
                    self.bluetooth.send(Message(channel="current", value="%d:%d:%d" % (self.current[0], self.current[1], self.orientation)))
        
        self.runningPath = False
        return ("path", "Success")

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
                return ("screen", "Value has wrong format (x|y:x|y:...)")
            self.screen.draw.point((x, y))
        self.screen.update()
        return ("screen", "Success")

    def forward(self, value):
        """Move forward"""
        # Get time and speed...
        fragments = value.split(":")
        time = int(fragments[0].strip())
        speed = int(fragments[1].strip())

        # Run the motor...
        try:
            self.motorR.run_timed(time_sp=time, speed_sp=speed)
            self.motorL.run_timed(time_sp=time, speed_sp=speed)
            return ("motorRL", "%d:%d" % (time, speed))
        except:
            return ("motorRL", "Device not connected")

    def rotate(self, value):
        """Rotate around itself"""
        # Get time and speed...
        fragments = value.split(":")
        time = int(fragments[0].strip())
        speed = int(fragments[1].strip())

        # Run the motor...
        try:
            self.motorR.run_timed(time_sp=time, speed_sp=-speed)
            self.motorL.run_timed(time_sp=time, speed_sp=speed)
            return ("motorRL", "%d:%d" % (time, speed))
        except:
            return ("motorRL", "Device not connected")

    def turnRight(self, value):
        """Turn the right motor"""
        # Get time and speed...
        fragments = value.split(":")
        time = int(fragments[0].strip())
        speed = int(fragments[1].strip())

        # Run the motor...
        try:
            self.motorR.run_timed(time_sp=time, speed_sp=speed)
            return ("motorR", "%d:%d" % (time, speed))
        except:
            return ("motorR", "Device not connected")

    def turnLeft(self, value):
        """Turn the left motor"""
        # Get time and speed...
        fragments = value.split(":")
        time = int(fragments[0].strip())
        speed = int(fragments[1].strip())

        # Run the motor...
        try:
            self.motorL.run_timed(time_sp=time, speed_sp=speed)
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
                # Try to reconnect...
                self.colorSensor = ev3.ColorSensor()
                return ("colorSensor", "Device not connected")
        else:
            try:
                red = self.colorSensor.red
                green = self.colorSensor.green
                blue = self.colorSensor.blue
                return ("colorSensor", "%d:%d:%d" % (red, green, blue))
            except:
                # Try to reconnect...
                self.colorSensor = ev3.ColorSensor()
                return ("colorSensor", "Device not connected")

    def sendInfraredValue(self, value):
        """Send the value of the infrared sensor"""
        try:
            value = int(self.infraredSensor.value() * 25.5)
            return ("infraredSensor", value)
        except:
            # Try to reconnect...
            self.infraredSensor = ev3.InfraredSensor()
            return ("infraredSensor", "Device not connected")

    def sendUltraValue(self, value):
        """Send the value of the ultra sensor"""
        try:
            value = self.ultraSensor.value()
            return ("ultraSensor", value)
        except:
            # Try to reconnect...
            self.ultraSensor = ev3.UltrasonicSensor()
            return ("ultraSensor", "Device not connected")

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
            return ("touchSensor", value)
        except:
            # Try to reconnect...
            self.touchSensor = ev3.TouchSensor()
            return ("touchSensor", "Device not connected")

    def sendAccelData(self, value):
        """Send the values of the accelometer"""
        accel = self.mpu9250.readAccel()
        return ("accel", accel)

    def sendGyroData(self, value):
        """Send the values of the gyroscope"""
        gyro = self.mpu9250.readGyro()
        return ("gyro", gyro)

    def sendMagData(self, value):
        """Send the values of the magnetometer"""
        mag = self.mpu9250.readMag()
        return ("mag", mag)

    def sendTemData(self, value):
        """Send the values of the thermometer"""
        temp = self.mpu9250.readTemp()
        return ("temp", temp)
