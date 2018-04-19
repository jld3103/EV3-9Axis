# This file control the EV3
# Author: Finn G., Jan-Luca D.

import ev3dev.ev3 as ev3
import ev3.ev3Communication as communication
import ev3.MPU9250 as MPU9250
from message import Message
from constants import *
from logger import *
import queue

class EV3:
    """Controls the EV3"""
    
    def __init__(self):
                    
        # Init screen...
        self.screen = ev3.Screen()
        
        # Init all snesors...
        self.touchSensor = ev3.TouchSensor()
        self.infraredSensor = ev3.InfraredSensor()
        self.colorSensor = ev3.ColorSensor()
        #self.mpu9250 = MPU9250.MPU9250()
        
        # Init all motors...
        self.motorR = ev3.LargeMotor('outC')
        self.motorL = ev3.LargeMotor('outA')
        
        # Create the queues for the bluetooth data...
        self.bluetoothReciveQueue = queue.Queue()
        
        # Start the Thread for the bluetooth connection...
        self.bluetooth = communication.BluetoothThread()
        self.bluetooth.start()
        
        # Add bluetooth listener...
        self.bluetooth.addListener("touchSensor", self.sendTouchValue)
        self.bluetooth.addListener("infraredSensor", self.sendInfraredValue)
        self.bluetooth.addListener("colorSensor", self.sendColorValue)
        self.bluetooth.addListener("screen", self.drawScreen)
        self.bluetooth.addListener("motorR", self.turnRight)
        self.bluetooth.addListener("motorL", self.turnLeft)
        self.bluetooth.addListener("accel", self.sendAccelData)
        self.bluetooth.addListener("gyro", self.sendGyroData)
        self.bluetooth.addListener("mag", self.sendMagData)
        self.bluetooth.addListener("close", self.close)
        
        # Start programm...
        self.start()
        
    def start(self):
        #TODO: Replace the if/elif with a dictionary
        
        # Execute all commands from the server...
        while self.bluetooth.isRunning:
            # Get command...
            command = self.bluetooth.listen()
            
            # Execute command...
            if command == -1:
                continue
            elif command != None:
                function = command[0]
                function(command[1])
            else:
                self.bluetooth.send(Message("Undefined channel"))
                
        info("Exit main thread")
        
    def close(self, value):
        self.bluetooth.closeServer()
        self.bluetooth.send(Message(channel="close",  value="Closed server"))
                
    def drawScreen(self, value):
        points = value.split(":")
        for point in points:
            try:
                x = int(point.split("|")[0])
                y = int(point.split("|")[1])
            except:
                self.bluetooth.send(Message(channel="screen",  value="Value has wrong format (x|y:x|y:...)"))
            self.screen.draw.point((x, y))
        self.screen.update()
        self.bluetooth.send(Message(channel="screen",  value=value))
        
    def turnRight(self, value):
        """Turn the right motor"""
        # Get time and speed...
        fragments = value.split(":")
        time=int(fragments[0].strip())
        speed=int(fragments[1].strip())
        
        # Run the motor...
        try:
            self.motorR.run_timed(time_sp=time, speed_sp=speed)
            self.bluetooth.send(Message(channel="motorR",  value=("%d:%d" % (time, speed))))
        except:
            self.bluetooth.send(Message(channel="motorR",  value="Device not connected"))
        
    def turnLeft(self, value):
        """Turn the left motor"""
        # Get time and speed...
        fragments = value.split(":")
        time=int(fragments[0].strip())
        speed=int(fragments[1].strip())
        
        # Run the motor...
        try:
            self.motorL.run_timed(time_sp=time, speed_sp=speed)
            self.bluetooth.send(Message(channel="motorL",  value=("%d:%d" % (time, speed))))
        except:
            self.bluetooth.send(Message(channel="motorL",  value="Device not connected"))  
            
    def sendColorValue(self, value):
        if value == "color":
            try:
                color = self.colorSensor.COLORS[self.colorSensor.color]
                self.bluetooth.send(Message(channel="colorSensor",  value=color))
            except:
                self.bluetooth.send(Message(channel="colorSensor",  value="Device not connected"))
        elif value == "rgb":
            try:
                red = self.colorSensor.red
                green = self.colorSensor.green
                blue = self.colorSensor.blue
                self.bluetooth.send(Message(channel="colorSensor",  value=("%d:%d:%d" % (red, green, blue))))
            except:
                self.bluetooth.send(Message(channel="colorSensor",  value="Device not connected"))

            
    def sendInfraredValue(self, value):
        """"Send the value of the infrared sensor"""
        try:
            value = self.infraredSensor.value()
            self.bluetooth.send(Message(channel="infraredSensor",  value=value))
        except:
            self.bluetooth.send(Message(channel="infraredSensor",  value="Device not connected"))
        
                
    def sendTouchValue(self, value):
        """"Send the value of the touch sensor"""
        try:
            value = self.touchSensor.value()
            self.bluetooth.send(Message(channel="touchSensor",  value=value))
        except:
            self.bluetooth.send(Message(channel="touchSensor",  value="Device not connected"))
        
    def sendAccelData(self, value):
        """"Send the values of the accelometer"""
        axes = value.split(":")
        accel = mpu9250.readAccel()
        for axis in axes:
            self.bluetooth.send(Message(channel=("accel%s" % axis.upper()),  value=accel[axis]))
            
    def sendGyroData(self, value):
        """"Send the values of the gyroscope"""
        axes = value.split(":")
        gyro = mpu9250.readGyro()
        for axis in axes:
            self.bluetooth.send(Message(channel=("gyro%s" % axis.upper()),  value=gyro[axis]))
            
    def sendMagData(self, value):
        """"Send the values of the magnetometer"""
        axes = value.split(":")
        mag = mpu9250.readMagnet()
        for axis in axes:
            self.bluetooth.send(Message(channel=("mag%s" % axis.upper()),  value=mag[axis]))
            
            
