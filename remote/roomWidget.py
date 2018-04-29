# This widget displays the room
# Author: Finn G., Jan-Luca D.

from PyQt4 import QtGui, QtCore
from constants import *
from logger import *



class Square():
    """This class describes a square"""
    def __init__(self, grid, x = None, y = None, state = None):
        self.grid = grid

        self._x = x
        self._y = y
        
        self.modified = True

        self.state = state # None is not discovered, True is a wall, False is floor
        self.inPath = False
        self.previous = None
        self.neighbours = []

        self.f = 0
        self.g = 0
        self.h = 0
        
    def getNeighbours(self):
        x = self.x()
        y = self.y()
        cols = self.grid.sizeX
        rows = self.grid.sizeY
        neighbours = []

        # Check if in coordinate system
        if x < cols - 1:
            neighbours.append(self.grid.getSquare(x + 1, y))
        if y < rows - 1:
            neighbours.append(self.grid.getSquare(x, y + 1))
        if x > 0:
            neighbours.append(self.grid.getSquare(x - 1, y))
        if y > 0:
            neighbours.append(self.grid.getSquare(x, y - 1))
            
        return neighbours

    def x(self):
        """Get x coordinate in the room"""
        if self._x == None:
            # Get x position in the grid...
            for line in self.grid.grid:
                if self in line:
                    return line.index(self)
        else:
            return self._x

    def y(self):
        """Get y coordinate in the room"""
        if self._y == None:
            # Get y position in the grid...
            for line in self.grid.grid:
                if self in line:
                    return self.grid.grid.index(line)
        else:
            return self._y

    def draw(self, painter, color):
        """Draw yourself"""
        painter.fillRect(self.rect(), QtGui.QColor(color[0], color[1], color[2]))

    def rect(self):
        """Calculate the rect of the square"""

        # Get size of the image...
        width = self.grid.parent.width()
        height = self.grid.parent.height()

        # Get the size of the squares...
        squareWidth = int(width / (self.grid.sizeX))
        squareHeight = int(height / (self.grid.sizeY))

        # Take the smaller side for the width and height of the squares...

        self.grid.scaledSquareSize = (min(squareWidth, squareHeight))

        if self.grid.scale:
            self.grid.squareSize = self.grid.scaledSquareSize

        squareSizeZoomed = self.grid.squareSize * self.grid.zoom

        # Calculate the border for drawing the room in the center of the image...
        borderLeft = (width - self.grid.sizeX*(squareSizeZoomed + 1)) / 2
        borderTop = (height - self.grid.sizeY*(squareSizeZoomed + 1)) / 2

        # Get the start position of the square...
        if self.grid.center:
            self.grid.startPosition = QtCore.QPoint(borderLeft + self.x() * (squareSizeZoomed + 1), borderTop + self.y() * (squareSizeZoomed + 1))
            self.grid.startPos = QtCore.QPoint(borderLeft, borderTop)
        else:
            self.grid.startPosition = QtCore.QPoint(self.grid.startPos.x() + self.x() * (squareSizeZoomed + 1), self.grid.startPos.y() + self.y() * (squareSizeZoomed + 1))

        # Return the rect...
        return QtCore.QRect(self.grid.startPosition.x(), self.grid.startPosition.y(), squareSizeZoomed, squareSizeZoomed)


    def updateState(self, newState):
        """Update the square state"""
        if newState != self.state:
            self.state = newState
            self.modified = True

class Grid():
    """This class manage the squares"""
    def __init__(self, parent):
        # Define the grid with only one undefined square...
        self.grid = [[Square(self)]]

        # Store the location of the EV3...
        self.current = self.grid[0][0]
        self.current.updateState(False)

        # Store sets...
        self.openSet = []
        self.closedSet = []

        # Define the grid sizes...
        self.sizeX = 1
        self.sizeY = 1

        # Define parent...
        self.parent = parent
        
        # Notice if the grid is modified...
        self.modified = True

        # Settings...
        self.zoom = 0.8
        self.center = True
        self.scale = True
        self.squareSize = 20
        self.scaledSquareSize = 20
        self.startPos = QtCore.QPoint(0, 0)


    def findOnesWay(self, start, end):
        """Execute the A*"""

        # Store the data
        self.start = start
        self.end = end
        self.openSet = []
        self.closedSet = []
        self.path = []
        self.finding = True

        self.openSet.append(self.start)

        while self.finding: #TODO: Go the shortest way with the fewest corners (Turning the robot need much time and can be incorrect)
            # Check if way possible
            if len(self.openSet) > 0:
                winner = 0
                for i in range(len(self.openSet)):
                    # Check if found shorter way
                    if self.openSet[i].f < self.openSet[winner].f:
                        winner = i
                # Update shortest way
                current = self.openSet[winner]
                if current == self.end:
                    info("Done!")
                    self.finding = False
                    # Draw the path
                    for i in range(len(self.path)):
                       self.path[i].inPath = True
                    self.draw(self.parent.image)

                self.openSet.remove(current)
                self.closedSet.append(current)
                
                currentNeighbours = current.getNeighbours()

                for i in range(len(currentNeighbours)):
                    neighbour = currentNeighbours[i]
                    newPath = False
                    # Check if g should be updated
                    if not neighbour in self.closedSet and neighbour.state != True:
                        tG = current.g + 1
                        if neighbour in self.openSet:
                            if tG < neighbour.g:
                                # Update g
                                neighbour.g = tG
                                newPath = True
                        else:
                            # Update g
                            neighbour.g = tG
                            self.openSet.append(neighbour)
                            newPath = True
                        if newPath:
                            # Update the other variables if g updated
                            neighbour.h = self.heuristic(neighbour, self.end)
                            neighbour.f = neighbour.g + neighbour.h
                            neighbour.previous = current
                # Find path and store
                self.path = []
                t = current
                self.path.append(self.start)
                while t.previous != None:
                    self.path.append(t)
                    t = t.previous
            else:
                self.finding = False
                # Draw the path
                for i in range(len(self.path)):
                    self.path[i].inPath = True
                self.draw(self.parent.image)
                info("No solution!")

    def heuristic(self, a, b):
        """Calculate the distance"""
        return abs(a.x() - b.x()) + abs(a.y() - b.y())

    def setZoom(self, delta):
        # Zoom in or out...
        if delta < 0:
            self.zoom -= 0.1
        else:
            self.zoom += 0.1

        # Set zoom bigger than 0.1...
        if self.zoom < 0.1:
            self.zoom = 0.1
        if self.zoom > 5:
            self.zoom = 5

        # Update zoom factor to the scaled square size...
        factor = self.scaledSquareSize / self.squareSize

        self.zoom /= factor

        # Scale the grid...
        self.squareSize = self.scaledSquareSize

    def addSquare(self, x, y, state):
        """Add a square with the state in the grid"""

        # If the x coordinate is bigger than the current grid, increase the grid...
        if x > self.sizeX - 1:
            for i in range(x - self.sizeX + 1):
                for line in self.grid:
                    line.append(Square(self))
                self.sizeX += 1

        # If the y coordinate is bigger than the current grid, increase the grid...
        if y > self.sizeY - 1:
            for i in range(y - self.sizeY + 1):
                line = []
                for j in range(self.sizeX):
                    line.append(Square(self))
                self.grid.append(line)
                self.sizeY += 1

        # If the x coordinate is smaller than zero, add columns at the left site...
        if x < 0:
            index = 0
            for line in self.grid:
                for i in range(x * -1):
                    line.insert(0, Square(self))
                index += 1
            self.sizeX += x* -1

            # Set start position...
            self.startPos.setX(self.startPos.x() - ((self.squareSize * self.zoom + 1) * (x * -1)))
            # Set the x coordinate to zero...
            x = 0

        # If the y coordinate is smaller than zero, add rows at the top...
        if y < 0:
            for i in range(y * -1):
                line = []
                for j in range(self.sizeX):
                    line.append(Square(self))
                self.grid.insert(0, line)
                self.sizeY += 1
                # Set start position...
                self.startPos.setY(self.startPos.y() - (self.squareSize * self.zoom + 1))
            y = 0
        # Set the square on the given state...
        self.updateSquareState(x, y, state)
        # Update image...
        self.draw(self.parent.image)

    def updateSquareState(self, x, y, state):
        """Update square and add neighbours"""
        self.getSquare(x, y).updateState(state)

    def getSquare(self, x, y):
        """Get a square from x and y"""
        if x > self.sizeX - 1 or x < 0 or y > self.sizeY - 1 or y < 0:
            # Add square if not existing
            self.addSquare(x, y, None)
        return self.grid[y][x]

    def getSquareAtCoordinate(self, x, y):
        """Return the square in the grid with the given coodinate"""
        # Notice the x and y position of the square...
        squarePosX = 0
        squarePosY = 0

        # Find the square with the given coordinates...
        while True:
            # Get the rect...
            square = Square(self, x = squarePosX, y = squarePosY)
            rect =  square.rect()

            # If coordinate in rect, return the position...
            if x >= rect.x() and x <= (rect.x() + rect.width() + 1) and y >= rect.y() and y <= (rect.y() + rect.height() + 1):
                    return square

            # If coordinate is not in rect, set the next rect...
            else:
                if x < rect.x():
                    squarePosX -= 1
                elif x > (rect.x() + rect.width()):
                    squarePosX += 1

                if y < rect.y():
                    squarePosY -= 1
                elif y > (rect.y() + rect.height()):
                    squarePosY += 1

    def draw(self, image):
        """Draw the image"""

        # Reset old image...
        if self.modified:
            image.fill(QtGui.qRgb(150, 150, 150))

        # Create the painter...
        painter = QtGui.QPainter(image)

        # Draw each square...
        y = 0
        for line in self.grid:
            x = 0
            for square in line:
                if self.modified or square.modified:
                    if square.state == 1:
                        square.draw(painter, (250, 250, 250))
                    elif square.inPath:
                        square.draw(painter, (0, 0, 255))
                    elif square in self.openSet and self.parent.settings.get("showSets"):
                        square.draw(painter, (0, 255, 0))
                    elif square in self.closedSet and self.parent.settings.get("showSets"):
                        square.draw(painter, (255, 0, 0))
                    elif square.state == 0:
                        square.draw(painter, (0, 0, 0))
                    elif square.state == None and self.parent.settings.get("showUndefinedSquares"):
                        square.draw(painter, (100, 100, 100))
                        
                    square.modified = False
                    
                x += 1
            y += 1
            
        self.modified = False

        # End painter and update the image...
        painter.end()
        self.parent.modified = True
        self.parent.update()

    def load(self, filename):
        try:
            file = open(filename, "r")

            for line in file:
                values = line.split(" - ")
                coordinates = values[0].split(":")
                x = int(coordinates[0])
                y = int(coordinates[1])
                state = bool(values[1].strip())

                self.addSquare(x, y, state)
        except:
            debug("Cannot find file: %s" % filename)

    def save(self, filename):
        file = open(filename, "w")

        for line in self.grid:
            for square in line:
                if square.state != None:
                    file.write("%d:%d - %d\n" % (square.x(), square.y(), square.state))
        file.close()

class RoomWidget(QtGui.QWidget):
    """This class displays the room with all barriers and etc."""

    def __init__(self, parent, settings, bluetooth):
        super(RoomWidget,  self).__init__(parent=parent)

        # Create image...
        self.image = QtGui.QImage(QtCore.QSize(self.width(), self.height()), QtGui.QImage.Format_RGB32)

        self.parent = parent
        self.settings = settings
        self.bluetooth = bluetooth

        # Create grid...
        self.grid = Grid(self)

        # Check if mouse moved...
        self.moved = 0

        # Fill image...
        self.image.fill(QtGui.qRgb(150, 150, 150))

        # Save old mouse position...
        self.mousePos = None

        # Load the old grid
        self.grid.load(gridFile)

        # Run the A*
        self.grid.findOnesWay(self.grid.getSquare(5, 5), self.grid.getSquare(10, 10))

    def contextMenu(self, pos):
        """show the context menu"""
        # Create the menu...
        self.menu = QtGui.QMenu(self)

        # Add the actions...
        self.menu.addAction("Center", self.onCenter)
        self.menu.addAction("Reset zoom", self.onResetZoom)
        self.menu.addAction("Reset grid", self.onResetGrid)

        # Show the menu on the click position...
        self.menu.exec_(self.mapToGlobal(pos))

    def onResetGrid(self):
        """Reset the grid"""
        self.grid = Grid(self)

        # Draw the image...
        self.grid.modified = True
        self.grid.draw(self.image)

    def onResetZoom(self):
        """Set zoom to default"""

        # Set zoom to default...
        self.grid.zoom = 1.0

        # Scale and center the grid only one time...
        scale_temp = self.grid.scale
        self.grid.scale = True
        center_temp = self.grid.center
        self.grid.center = True

        # Draw the image...
        self.grid.modified = True
        self.grid.draw(self.image)

        # Reset scaling and centering...
        self.grid.scale = scale_temp
        self.grid.center = center_temp

    def onCenter(self):
        """Center the image"""
        
        self.grid.center = True
        
        # Draw the image...
        self.grid.modified = True
        self.grid.draw(self.image)

    def mouseReleaseEvent(self, event):
        """When the mouse wasn't moved, find square on the click position"""
        if self.moved < 5:
            square = self.grid.getSquareAtCoordinate(event.x(), event.y())

            if not square == None:
                # Update new state...
                self.grid.center = False
                self.grid.scale = False
                self.moved = False

                # Add the square...
                self.grid.addSquare(square.x(), square.y(), 1)

                # Draw the image...
                self.grid.draw(self.image)

    def mousePressEvent(self, event):
        """Called when the mouse is pressed"""

        # Update moved...
        self.moved = 0

        if event.button() == QtCore.Qt.RightButton:
            # If it's a right click, open the context menu...
            self.contextMenu(event.pos())
        else:
            # Update the last click position...
            self.mousePos = event.pos()

    def mouseMoveEvent(self, event):
        """Get difference to the last mouse event"""

        # Get difference to the last position...
        difference = event.pos() - self.mousePos

        # Update moved...
        if difference.x() + difference.y() < 0:
            self.moved -= difference.x() + difference.y()
        else:
            self.moved += difference.x() + difference.y()

        # Update start position...
        self.grid.startPos += difference

        # Save current mouse position...
        self.mousePos = event.pos()

        # Update centering...
        self.grid.center = False

        # Draw the image...
        self.grid.modified = True
        self.grid.draw(self.image)

    def wheelEvent(self, event):
        """Called when the mouse wheel spin"""
        self.grid.setZoom(event.delta())

        # Draw the image...
        self.grid.modified = True
        self.grid.draw(self.image)

    def paintEvent(self, event):
        """Paint the image, with all the rails and switches."""
        painter = QtGui.QPainter(self)
        painter.drawImage(event.rect(), self.image)

    def resizeEvent(self, event):
        """Called when the window is resized"""
        self.resizeImage(self.image, event.size())
        super(RoomWidget, self).resizeEvent(event)
        
    def updateImage(self):
        """Update the image"""
        
        # Draw the image...
        self.grid.modified = True
        self.grid.draw(self.image)

    def resizeImage(self, image, newSize):
        """Resize the image and draw it again"""
        if image.size() == newSize:
            return

        # Create a new image with new size and re-draw the rail network
        self.image = QtGui.QImage(newSize, QtGui.QImage.Format_RGB32)
        self.image.fill(QtGui.qRgb(150, 150, 150))
        
        # Paint the image...
        self.grid.modified = True
        self.grid.draw(self.image)

    def closeEvent(self, event):
        self.grid.save(gridFile)
