# This experiment read the sensor data from the arduino
# Author: Finn G., Jan-Luca D.

import sys

from smbus import SMBus

# Init sensor port 2...
bus = SMBus(4)

# Read all bytes from the Arduino... (All bytes:    A = accel data
#                                                   M = magnetometer data
#                                                   G = gyro data
#                                                   T = temperature
data = bus.read_i2c_block_data(0x04, ord(sys.argv[1]))

# Connect the bytes to a string...
msg = ""
for byte in data:
    if byte != 255:
        # Convert the byte to a char and add this to the string...
        msg += str(chr(byte))

# Print the message...
print(msg)
