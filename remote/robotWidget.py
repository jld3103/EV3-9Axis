#!/usr/bin/python3

# This widget displays the robot in 3D
# Author: Finn G.

from PyQt4 import QtGui,  QtCore, QtOpenGL
from OpenGL import GLU
from OpenGL.GL import *
from constants import *
from logger import *
import threading
import math

setLogLevel(logLevel)

moveX = -8.4
moveY = 0
moveZ = -9.75

defaultColor = [0.39, 0.39, 0.39, 1.0]


class ObjLoader(threading.Thread):
    def __init__(self, filename, updateEvent):
        threading.Thread.__init__(self)

        self.filename = filename
        self.updateEvent = updateEvent
        self.changeYZ = False

        self.color = defaultColor

        self.vertices = []
        self.triangle_faces = []
        self.quad_faces = []
        self.polygon_faces = []
        self.normals = []

    def run(self):
        """Read the file and calculate the normals in a second thread"""
        try:
            # Try to open file...
            f = open(self.filename)

            # Read each line in the file...
            for line in f:

                # Check if the line define a vertix...
                if line[:2] == "v ":
                    # Split the line in 'v ' and the three values (x, y, z)...
                    values = line.split(" ")

                    # Define the vertex...
                    if self.changeYZ:
                        vertex = (float(values[1]) + moveX, float(values[3]) + moveY, float(values[2]) + moveZ)
                    else:
                        vertex = (float(values[1]) + moveX, float(values[2]) + moveY, float(values[3]) + moveZ)

                    # Round the values...
                    vertex = (round(vertex[0],2),round(vertex[1],2),round(vertex[2],2))

                    # Append the vertex to the list of the vertices...
                    self.vertices.append(vertex)

                # Check if the line define a face...
                elif line[0] == "f":
                    # Replace all "//" with "/", because both syntxes are correct... 
                    string = line.replace("//","/").strip()

                    # Split the line in 'f' and the values (Point 1, Point 2, ...)...
                    items = string.split(" ")
                    del items[0]

                    # Calculate normal of the face (For the lightning)...
                    normal = self.getNormal(self.vertices[int(items[0].split("/")[0]) - 1], self.vertices[int(items[1].split("/")[0]) - 1], self.vertices[int(items[2].split("/")[0]) - 1])
                    index = len(self.normals) + 1

                    # Check if normal already exist...
                    if normal in self.normals:
                        index = self.normals.index(normal) + 1
                        debug("%s: Old Normal:       %d" % (self.filename, index))
                    else:
                        debug("%s: New Normal: %f %f %f" % (self.filename, normal[0], normal[1], normal[2]))
                        self.normals.append(normal)

                    # Define the face...
                    face  = []
                    for item in items:
                        if len(item) == 0:
                            continue
                        face.append(item.split("/")[0] + "/" + str(index))

                    # Add face to the correct list...
                    if len(face) == 3:
                        self.triangle_faces.append(tuple(face))
                    elif len(face) == 4:
                        self.quad_faces.append(tuple(face))
                    else:
                        self.polygon_faces.append(tuple(face))

            f.close()

            # Update the GUI...
            self.updateEvent.emit()

        except IOError:
            error("Could not open the .obj file...")

    def setColor(self, r = defaultColor[0], g = defaultColor[1], b = defaultColor[2]):
        self.color = [r, g, b, 1.0]

    def getNormal(self, a, b, c):
        """Calculate the normal of a triangles face"""

        # Calculate the normal...
        d = [a[0] - b[0],
            a[1] - b[1],
            a[2] - b[2]]
        e = [b[0] - c[0],
            b[1]-c[1],
            b[2]-c[2]]

        normal = [d[1] * e[2] - d[2] * e[1],
                        d[2] * e[0] - d[0] * e[2],
                        d[0] * e[1] - d[1] * e[0]]

        # Norm the normal...
        normal_length = float(math.sqrt(normal[0] ** 2 + normal[1] ** 2 + normal[2] ** 2))
        normed = [(normal[0]) / normal_length,
                         (normal[1]) / normal_length,
                         (normal[2]) / normal_length]

        return normed

    def render_scene(self):
        """Render the scene with PyOpenGL"""

        # Render all triangle faces...
        if len(self.triangle_faces) > 0:
            # Start rendering...
            glBegin(GL_TRIANGLES)
            for face in (self.triangle_faces):
                # Get normal...
                n = face[0]
                normal = self.normals[int(n[n.find("/") + 1:]) - 1]
                # Set normal...
                glNormal3fv(normal)
                # Set color...
                glMaterialfv(GL_FRONT, GL_DIFFUSE, self.color)
                for f in (face):
                    # Set vertex...
                    glVertex3fv(self.vertices[int(f[:f.find("/")]) - 1])
            glEnd()

        # Render all quad faces...
        if len(self.quad_faces) > 0:
            # Start rendering...
            glBegin(GL_QUADS)
            for face in (self.quad_faces):
                # Get normal...
                n = face[0]
                normal = self.normals[int(n[n.find("/") + 1:]) - 1]
                # Set normal...
                glNormal3fv(normal)
                # Set color...
                glMaterialfv(GL_FRONT, GL_DIFFUSE, self.color)
                for f in (face):
                    # Set vertex...
                    glVertex3fv(self.vertices[int(f[:f.find("/")]) - 1])
            glEnd()

        # Render all polygon faces...
        if len(self.polygon_faces) > 0:
            for face in (self.polygon_faces):
                # Start rendering...
                glBegin(GL_POLYGON)
                n = face[0]
                normal = self.normals[int(n[n.find("/") + 1:]) - 1]
                # Set normal...
                glNormal3fv(normal)
                # Set color...
                glMaterialfv(GL_FRONT, GL_DIFFUSE, self.color)
                for f in (face):
                    # Set vertex...
                    glVertex3fv(self.vertices[int(f[:f.find("/")]) - 1])
                glEnd()

class Robot(QtOpenGL.QGLWidget):

    updateEvent = QtCore.pyqtSignal()

    def __init__(self, parent, bluetooth):
        self.parent = parent
        QtOpenGL.QGLWidget.__init__(self, parent)
        self.yRotDeg = 45

        self.objects = { "brick" : "brick.obj",
                                "distanceSensorConnector" : "distance_sensor_connector.obj",
                                "distanceSensor" : "distance_sensor.obj",
                                "motorR" : "motor_right.obj",
                                "motorL" : "motor_left.obj",
                                "wheelR" : "wheel_right.obj",
                                "wheelL" : "wheel_left.obj",
                                "wheelBack" : "wheel_back.obj",
                                "wheelBackConnector" : "wheel_back_connector.obj",
                                "motorsConnectorTop" : "motors_connector_top.obj",
                                "motorsConnectorBottem" : "motors_connector_bottem.obj",
                                "touchSensorConnector" : "touch_sensor_connector.obj",
                                "touchSensorHead" : "touch_sensor_head.obj", 
                                "touchSensor" : "touch_sensor.obj",
                                "colorSensor" : "color_sensor.obj"}

        self.updateEvent.connect(self.paintGL)

        # Add all listener...
        bluetooth.addListener("touchSensor", self.setTouchSensor)
        bluetooth.addListener("colorSensor", self.setColorSensor)
        bluetooth.addListener("infraredSensor", self.setDistanceSensor)

        self.oldMousePosition = 0

    def setTouchSensor(self, value):
        """Set touch sensor value"""

        # If the touch sensor is pressed, set the color to red...
        if int(value) == 1:
            self.objects["touchSensorHead"].setColor(1, 0, 0)
        # If the color sensor is not pressed, set the color to default...
        else:
            self.objects["touchSensorHead"].setColor()
        
        # Update image...
        self.paintGL()

    def setColorSensor(self, value):
        """Set the color of the color sensor"""

        # Get the rgb values...
        rgb = value.split(":")
        if len(rgb) == 3:
            # Put the values in the correct format...
            r = int(rgb[0]) / 255
            g = int(rgb[1]) / 255
            b = int(rgb[2]) / 255

            # Set the color of the color sensor...
            self.objects["colorSensor"].setColor(r, g, b)
            
        # Update image...
        self.paintGL()

    def setDistanceSensor(self, value):
        """Set the color of the distance sensor (green = far / red = near)"""

        # Convert value in an interger...
        value = int(value)

        # Set the max value of the sensor...
        maxValue = 100

        # Calculate the color steps for each value...
        steps = 510 / maxValue

        # Calculate the color (From red to green)...
        colorG = min((value * steps) / 255, 1.0)
        colorR = 1
        if colorG == 1:
            colorR = (255 - (value -50) * steps) / 255

        # Set the color...
        self.objects["distanceSensor"].setColor(colorR, colorG, 0)
        
        # Update image...
        self.paintGL()

    def initializeGL(self):
        """Init the 3D graphic"""

        # Set background color...
        self.qglClearColor(QtGui.QColor(255, 255, 255))

        # Init all 3D objects...
        self.initGeometry()

        # Set the object not transparent...
        glEnable(GL_DEPTH_TEST)

        # Add lighting..
        glEnable(GL_LIGHTING)
        glEnable(GL_LIGHT0)
        glEnable(GL_NORMALIZE)

    def resizeGL(self, width, height):
        """Resize the 3D graphic"""

        # Prevent division by ziro...
        if height == 0:
            height = 1

        # Set size...
        glViewport(0, 0, width, height)
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        aspect = width / float(height)

        # Set perspective...
        GLU.gluPerspective(45.0, aspect, 8, 100.0)

        # Set mode...
        glMatrixMode(GL_MODELVIEW)

    def paintGL(self):
        """Draw the 3D graphic"""
        # Clear old image...
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

        # Set point of view...
        glLoadIdentity()
        glTranslate(0, -8, -29)

        # Rotate the object...
        glRotate(self.yRotDeg, 0, -10, 00)

        # Render each object...
        for object in self.objects:
            self.objects[object].render_scene()

        # Add ambient light...
        glLightModelfv(GL_LIGHT_MODEL_AMBIENT,[1, 1, 1, 0.1])

        # Add positioned light...
        glLightfv(GL_LIGHT0,GL_DIFFUSE,[1,1,1,0.1])

    def initGeometry(self):
        """Init the geometry"""

        # Load each file in another thread...
        for object in self.objects:
            objFile = ObjLoader("remote/textures/%s" % self.objects[object], self.updateEvent)
            objFile.setName(self.objects[object] + " Thread")
            objFile.start()
            self.objects[object] = objFile

    def spin(self, degrees=None):
        """Spin the 3D object"""
        self.yRotDeg =  (self.yRotDeg - degrees) % 360.0
        self.updateGL()

    def mousePressEvent(self, event):
        """Set the old mouse position on the click position"""
        self.oldMousePosition = event.x()

    def mouseMoveEvent(self, event):
        """Spin the robot"""
        self.spin((event.x() - self.oldMousePosition) / 4)
        self.oldMousePosition = event.x()
