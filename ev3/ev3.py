#!/usr/bin/python3

# This file control the EV3
# Author: Finn G.

import ev3.ev3Communication as communication
import ev3.MPU9250 as MPU9250
from constants import *
from logger import *
import queue

class EV3:
    """Controls the EV3"""
    
    def __init__(self):
        # create the queues for the bluetooth data...
        self.bluetoothReciveQueue = queue.Queue()
        self.bluetoothSendQueue = queue.Queue()
        
        # start the Thread for the bluetooth connection...
        bluetoothThread = communication.BluetoothThread(self.bluetoothReciveQueue, self.bluetoothSendQueue)
        bluetoothThread.setName("BluetoothThread")
        bluetoothThread.start()

        # Search the mpu9250 9-axis sensor...
        #self.mpu9250 = MPU9250.MPU9250()
        
        # Log the sensor data...
        #self.logSensorData()

    def logSensorData(self):
        """Send each second via bluetooth the sensor data"""
        # Send each second the sensor data to the bluetooth device...
        try:
            while True:
                accel = mpu9250.readAccel()
                send("Accel: %d, %d, %d" % (accel['x'], accel['y'], accel['y']))
                gyro = mpu9250.readGyro()
                send("Gyro:  %d, %d, %d" % (gyro['x'], gyro['y'], gyro['y']))
                mag = mpu9250.readMagnet()
                send("Mag:   %d, %d, %d" % (mag['x'], mag['y'], mag['y']))
                time.sleep(1)
        except KeyboardInterrupt:
            error("KeyboardInterrupt")
            
            
