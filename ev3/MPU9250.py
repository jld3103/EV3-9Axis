# Read the data of the sensor...
# Author: Finn G., Jan-Luca D.

from smbus import SMBus
from constants import *
from logger import *

setLogLevel(logLevel)


address = 0x04
mag = ord("M")
accel = ord("A")
gyro = ord("G")
temp = ord("T")

class MPU9250():
    
    def __init__(self):
        # Init sensor port 2...
        try:
            self.bus = SMBus(4)
        except:
            error("Please connect the sensor to port 2")

    def readI2cData(self, registery):
        """Read the bytes and create a string"""
        
        try:
            data = self.bus.read_i2c_block_data(address, registery)
        except:
            return "Device not connected"

        # Connect the bytes to a string...
        msg = ""
        for byte in data:
            if byte != 255:
                # Convert the byte to a char and add this to the string...
                msg += str(chr(byte))
                
        return msg
        
    def readGyro(self):
        """Read the gyro data"""
        return self.readI2cData(gyro)
    
    def readMag(self):
        """Read the mag data"""
        return self.readI2cData(mag)
        
    def readAccel(self):
        """Read the accel data"""
        return self.readI2cData(accel)

    def readTemp(self):
        """Read the temp data"""
        return self.readI2cData(temp)
        
    
