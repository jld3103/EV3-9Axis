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
        
        # Init all snesors...
        self.touchSensor = ev3.TouchSensor()
        self.infraredSensor = ev3.InfraredSensor()
        
        # Create the queues for the bluetooth data...
        self.bluetoothReciveQueue = queue.Queue()
        self.bluetoothSendQueue = queue.Queue()
        
        # Start the Thread for the bluetooth connection...
        bluetoothThread = communication.BluetoothThread(self.bluetoothReciveQueue, self.bluetoothSendQueue)
        bluetoothThread.setName("BluetoothThread")
        bluetoothThread.start()
        
        # Start programm...
        self.start()

        # Search the mpu9250 9-axis sensor...
        #self.mpu9250 = MPU9250.MPU9250()
        
    def start(self):
        #TODO: Replace the if/elif with a dictionary
        
        # Execute all commands from the server...
        while True:
            data = self.bluetoothReciveQueue.get()
            info("Get data in ReciveQueue: %s" % data)
            if data.channel == "close":
                self.bluetoothSendQueue.put(Message(channel="close", value="True"))
                break
                
            # EV3 sensors...
            elif data.channel == "touchSensor":
                self.sendTouchValue()
            elif data.channel == "infraredSensor":
                self.sendInfraredValue()
                
            # All accel datas...
            elif data.channel == "Accel":
                self.sendAccelData()
            elif data.channel == "AccelX":
                self.sendAccelData(axes=['x'])
            elif data.channel == "AccelY":
                self.sendAccelData(axes=['y'])
            elif data.channel == "AccelZ":
                self.sendAccelData(axes=['z'])  
                
            # All gyro datas...
            elif data.channel == "Gyrol":
                self.sendAccelData() 
            elif data.channel == "GyrolX":
                self.sendAccelData(axes=['x']) 
            elif data.channel == "GyroY":
                self.sendAccelData(axes=['y']) 
            elif data.channel == "GyroZ":
                self.sendAccelData(axes=['z']) 
                
            # All mag datas...
            elif data.channel == "Mag":
                self.sendAccelData() 
            elif data.channel == "MagX":
                self.sendAccelData(axes=['x']) 
            elif data.channel == "MagY":
                self.sendAccelData(axes=['y']) 
            elif data.channel == "MagZ":
                self.sendAccelData(axes=['z']) 
                
            else:
                #Echo...
                self.bluetoothSendQueue.put(data)
                
        info("Exit main thread")
        
    def sendInfraredValue(self):
        """"Send the value of the infrared sensor"""
        value = self.infraredSensor.value()
        self.bluetoothSendQueue.put(Message(channel="InfraredSensor",  value=value))
                
    def sendTouchValue(self):
        """"Send the value of the touch sensor"""
        value = self.touchSensor.value()
        self.bluetoothSendQueue.put(Message(channel="TouchSensor",  value=value))
        
    def sendAccelData(self, axes=['x', 'y', 'z']):
        """"Send the values of the accelometer"""
        accel = mpu9250.readAccel()
        for axis in axes:
            self.bluetoothSendQueue.put(Message(channel=("Accel%s" % axis.upper()),  value=accel[axis]))
            
    def sendGyroData(self, axes=['x', 'y', 'z']):
        """"Send the values of the gyroscope"""
        gyro = mpu9250.readGyro()
        for axis in axes:
            self.bluetoothSendQueue.put(Message(channel=("Gyro%s" % axis.upper()),  value=gyro[axis]))
            
    def sendMagData(self, axes=['x', 'y', 'z']):
        """"Send the values of the magnetometer"""
        mag = mpu9250.readMagnet()
        for axis in axes:
            self.bluetoothSendQueue.put(Message(channel=("Mag%s" % axis.upper()),  value=mag[axis]))
            
            
