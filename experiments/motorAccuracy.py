#!/usr/bin/python3

# This is a experimentto improve the accuracy of the motors 
# For more detailed information you can read the wiki article 'Improve the accuracy of the robot' on the page 'experiments'

import ev3dev.ev3 as ev3
from time import sleep
import sys

# Init the motors...
motorR = ev3.LargeMotor("outC")
motorL = ev3.LargeMotor("outA")

def timeAndSpeed(time, speedR, speedL):
    """Driving forward with the given time and speed"""
    print ("Drive %d ms forward with the speed: %d and %d" % (time, speedR, speedL))
    
    # Run the motors...
    motorR.run_timed(time_sp = time, speed_sp = speedR)
    motorL.run_timed(time_sp = time, speed_sp = speedL)
    
    # Wait until the motors stop...
    while motorR.is_running or motorL.is_running:
        sleep(0.1)

def tachoPosition(speed, unitsR, unitsL):
    """Driving forward to the given position"""
    print ("Drive %d and %d units forward" % (unitsR, unitsL))
    
    # Get the new tacho position...
    absPositionR = motorR.position + unitsR
    absPositionL = motorL.position + unitsL

    motorR.run_to_abs_pos(position_sp=absPositionR, speed_sp=speed)
    motorL.run_to_abs_pos(position_sp=absPositionL, speed_sp=speed)
    
    # Wait until the motors stop...
    while motorR.is_running or motorL.is_running:
        sleep(0.1)

# Choose which example should be execute...
print(sys.argv)
tachoPosition(int(sys.argv[1]), int(sys.argv[2]), int(sys.argv[3]))

print("Ready!")
