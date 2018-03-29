#!/usr/bin/python3

# This file control the EV3
# Author: Finn G.

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
        
        # Define all channels...
        self.channels = { "touchSensor" : self.sendTouchValue, 
                    "infraredSensor" : self.sendInfraredValue, 
                    "colorSensor" : self.sendColorValue, 
                    "screen" : self.drawScreen, 
                    "motorR" : self.turnRight, 
                    "motorL" : self.turnLeft, 
                    "Accel" : self.sendAccelData, 
                    "Gyrol" : self.sendAccelData, 
                    "Mag" : self.sendAccelData}
                    
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
        self.bluetoothSendQueue = queue.Queue()
        
        # Start the Thread for the bluetooth connection...
        bluetoothThread = communication.BluetoothThread(self.bluetoothReciveQueue, self.bluetoothSendQueue)
        bluetoothThread.setName("BluetoothThread")
        bluetoothThread.start()
        
        # Start programm...
        self.start()
        
    def start(self):
        #TODO: Replace the if/elif with a dictionary
        
        # Execute all commands from the server...
        while True:
            data = self.bluetoothReciveQueue.get()
            info("Get data in ReciveQueue: %s" % data)
            
            # If the channel is 'close', close server...
            if data.channel == "close":
                self.bluetoothSendQueue.put(Message(channel="close", value="True"))
                break
                
            # If given channel in channels, execute function...
            elif data.channel in self.channels:
                self.channels[data.channel](data.value)
                
            # If not, send echo...
            else:
                self.bluetoothSendQueue.put(data)
                
        info("Exit main thread")
        
    def drawScreen(self, value):
        points = value.split(":")
        for point in points:
            try:
                x = int(point.split("|")[0])
                y = int(point.split("|")[1])
            except:
                self.bluetoothSendQueue.put(Message(channel="Screen",  value="Value has wrong format (x|y:x|y:...)"))
            self.screen.draw.point((x, y))
        self.screen.update()
        self.bluetoothSendQueue.put(Message(channel="Screen",  value=value))
        
    def turnRight(self, value):
        """Turn the right motor"""
        # Get time and speed...
        fragments = value.split(":")
        time=int(fragments[0].strip())
        speed=int(fragments[1].strip())
        
        # Run the motor...
        try:
            self.motorR.run_timed(time_sp=time, speed_sp=speed)
            self.bluetoothSendQueue.put(Message(channel="MotorR",  value=("%d:%d" % (time, speed))))
        except:
            self.bluetoothSendQueue.put(Message(channel="MotorR",  value="Device not connected"))
        
    def turnLeft(self, value):
        """Turn the left motor"""
        # Get time and speed...
        fragments = value.split(":")
        time=int(fragments[0].strip())
        speed=int(fragments[1].strip())
        
        # Run the motor...
        try:
            self.motorL.run_timed(time_sp=time, speed_sp=speed)
            self.bluetoothSendQueue.put(Message(channel="MotorL",  value=("%d:%d" % (time, speed))))
        except:
            self.bluetoothSendQueue.put(Message(channel="MotorL",  value="Device not connected"))  
            
    def sendColorValue(self, value):
        if value == "color":
            try:
                color = self.colorSensor.COLORS[self.colorSensor.color]
                self.bluetoothSendQueue.put(Message(channel="ColorSensor",  value=color))
            except:
                self.bluetoothSendQueue.put(Message(channel="ColorSensor",  value="Device not connected"))
        elif value == "rgb":
            try:
                red = self.colorSensor.red
                green = self.colorSensor.green
                blue = self.colorSensor.blue
                self.bluetoothSendQueue.put(Message(channel="ColorSensor",  value=("%d:%d:%d" % (red, green, blue))))
            except:
                self.bluetoothSendQueue.put(Message(channel="ColorSensor",  value="Device not connected"))

            
    def sendInfraredValue(self, value):
        """"Send the value of the infrared sensor"""
        try:
            value = self.infraredSensor.value()
            self.bluetoothSendQueue.put(Message(channel="InfraredSensor",  value=value))
        except:
            self.bluetoothSendQueue.put(Message(channel="InfraredSensor",  value="Device not connected"))
        
                
    def sendTouchValue(self, value):
        """"Send the value of the touch sensor"""
        try:
            value = self.touchSensor.value()
            self.bluetoothSendQueue.put(Message(channel="TouchSensor",  value=value))
        except:
            self.bluetoothSendQueue.put(Message(channel="TouchSensor",  value="Device not connected"))
        
    def sendAccelData(self, value):
        """"Send the values of the accelometer"""
        axes = value.split(":")
        accel = mpu9250.readAccel()
        for axis in axes:
            self.bluetoothSendQueue.put(Message(channel=("Accel%s" % axis.upper()),  value=accel[axis]))
            
    def sendGyroData(self, value):
        """"Send the values of the gyroscope"""
        axes = value.split(":")
        gyro = mpu9250.readGyro()
        for axis in axes:
            self.bluetoothSendQueue.put(Message(channel=("Gyro%s" % axis.upper()),  value=gyro[axis]))
            
    def sendMagData(self, value):
        """"Send the values of the magnetometer"""
        axes = value.split(":")
        mag = mpu9250.readMagnet()
        for axis in axes:
            self.bluetoothSendQueue.put(Message(channel=("Mag%s" % axis.upper()),  value=mag[axis]))
            
            
