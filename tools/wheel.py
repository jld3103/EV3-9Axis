import math

filename = "robot/wheel_right_new.obj"

center_x = 2.25
center_y = 2.225
center_z = 15.375
r = 2.1
thickness = 2.2
steps_count = 10

u = 2 * math.pi * r

print("Start...")

# Open file...
f = open(filename, "w")

# Calculate all points in front...
for i in range(steps_count):
        angle = 360 / steps_count * i
    
        # Get point...
        x = r*math.sin(math.radians(angle)) + center_x
        y = center_y - r*math.cos(math.radians(angle))
        z = center_z - thickness/2
        
		# Write line...
        f.write("v %f %f %f\n" % (x, y, z))
        
# Calculate all points on backsite...
f.write("# Backsite\n")
for i in range(steps_count):
		
		# Get point...
        angle = 360 / steps_count * i
        x = r*math.sin(math.radians(angle)) + center_x
        y = center_y - r*math.cos(math.radians(angle))
        z = center_z + thickness/2  
        
		# Write line...
        f.write("v %f %f %f\n" % (x, y, z))
        
# Define the front and back site...
f.write("# Sites\n")
string = ""
for i in range(steps_count):
    string = str(i+1)+ " " + string
string.strip()
f.write("f "+string+"\n")
string = "f "
for i in range(steps_count):
    string += str(i+steps_count+1)+" "
string.strip()
f.write(string+"\n")

# Define the faces around the wheel...
f.write("# Wheel faces\n")
i = 1
while i < steps_count:
    a = i
    b = i+1
    c = b + steps_count
    d  = a + steps_count
    f.write("f %d %d %d %d\n" % (a, b, c, d))
    i += 1
a = steps_count
b = 1
c = steps_count+1
d  = steps_count*2
f.write("f %d %d %d %d\n" % (a, b, c, d))

# Close file...
f.close()
