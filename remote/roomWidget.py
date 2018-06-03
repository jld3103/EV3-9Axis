# This widget displays the room
# Author: Finn G., Jan-Luca D.

from PyQt4 import QtCore, QtGui

from constants import *
from logger import *
from message import Message


class Square():
    """This class describes a square"""

    def __init__(self, grid, x=None, y=None, state=None):
        self.grid = grid

        self._x = x
        self._y = y

        self.state = None  # True is a wall
        self.previous = None

        self.f = 0
        self.g = 0
        self.h = 0

        # Set state...
        if state != None:
            self.updateState(state)

    def resetAlgorithmData(self):
        """Reset all the data for the algorithm"""
        self.previous = None
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
        painter.fillRect(self.rect(),
                         QtGui.QColor(color[0], color[1], color[2]))

    def drawOrientation(self, painter, orientation):
        """Draw an arrow to the current orientation"""

        # Get the square coorinates...
        rect = self.rect()
        x = rect.x()
        y = rect.y()
        xCenter = x + (x + rect.width() - x) / 2
        yCenter = y + (y + rect.height() - y) / 2

        # Set the pen...
        pen = QtGui.QPen(QtGui.QColor(255, 0, 0))  # set lineColor
        pen.setWidth(3)
        brush = QtGui.QBrush(QtGui.QColor(255, 0, 0))
        painter.setPen(pen)
        painter.setBrush(brush)

        # Create triangle for the current orientation...
        if orientation == 0:
            triangle = QtGui.QPolygon([
                x + rect.width() / 4, y + rect.height() / 4, xCenter, y,
                x + rect.width() * 3 / 4, y + rect.height() / 4
            ])
        elif orientation == 1:
            triangle = QtGui.QPolygon([
                x + rect.width() * 3 / 4, y + rect.height() / 4,
                x + rect.width(), yCenter, x + rect.width() * 3 / 4,
                y + rect.height() * 3 / 4
            ])
        elif orientation == 2:
            triangle = QtGui.QPolygon([
                x + rect.width() / 4, y + rect.height() * 3 / 4, xCenter,
                y + rect.height(), x + rect.width() * 3 / 4,
                y + rect.height() * 3 / 4
            ])
        else:
            triangle = QtGui.QPolygon([
                x + rect.width() / 4, y + rect.height() / 4, x, yCenter,
                x + rect.width() / 4, y + rect.height() * 3 / 4
            ])

        # Draw triangle...
        painter.drawPolygon(triangle)

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

        # If scaling is activated, scale the square size...
        if self.grid.scale:
            self.grid.squareSize = self.grid.scaledSquareSize

        # Multiply the square size by the zoom factor...
        squareSizeZoomed = self.grid.squareSize * self.grid.zoom

        # Calculate the border for drawing the room in the center of the image...
        borderLeft = (width - self.grid.sizeX * (squareSizeZoomed + 1)) / 2
        borderTop = (height - self.grid.sizeY * (squareSizeZoomed + 1)) / 2

        # Get the start position of the square...
        if self.grid.center:
            self.grid.startPosition = QtCore.QPoint(borderLeft + self.x() * (
                squareSizeZoomed + 1), borderTop + self.y() *
                                                    (squareSizeZoomed + 1))
            self.grid.startPos = QtCore.QPoint(borderLeft, borderTop)
        else:
            self.grid.startPosition = QtCore.QPoint(
                self.grid.startPos.x() + self.x() * (squareSizeZoomed + 1),
                self.grid.startPos.y() + self.y() * (squareSizeZoomed + 1))

        # Return the rect...
        return QtCore.QRect(self.grid.startPosition.x(),
                            self.grid.startPosition.y(), squareSizeZoomed,
                            squareSizeZoomed)

    def updateState(self, newState):
        """Update the square state"""
        self.state = newState

        if self.state:
            self.grid.getSquare(self.x()- 1, self.y())
            self.grid.getSquare(self.x(), self.y() - 1)
            self.grid.getSquare(self.x() + 1, self.y())
            self.grid.getSquare(self.x(), self.y() + 1)

class Grid():
    """This class manage the squares"""

    def __init__(self, parent):
        # Define the grid with only one floor square...
        self.grid = [[Square(self)]]

        # Store the location of the EV3...
        self.current = self.grid[0][0]
        self.currentOrientation = 0  # Top: 0 / Right: 1 / Bottom: 2 / Left: 3

        # Store sets...
        self.openSet = []
        self.closedSet = []

        # Define the grid sizes...
        self.sizeX = 1
        self.sizeY = 1

        # Define the current path...
        self.path = []
        self.previewPath = []
        self.executingPath = False

        # Define parent...
        self.parent = parent

        # Settings...
        self.zoom = 0.8
        self.center = True
        self.scale = True
        self.squareSize = 30
        self.scaledSquareSize = 20
        self.startPos = QtCore.QPoint(0, 0)

    def findOnesWay(self, end, preview = False):
        """Execute the A*"""

        # Store the data
        self.start = self.current
        self.openSet = []
        self.closedSet = []
        if not preview:
            self.path = []
            self.end = end
        self.previewPath = []
        self.finding = True
        path = []

        # Add the start square to the possible squares...
        self.openSet.append(self.start)

        # Reset the old algorithm data...
        for line in self.grid:
            for square in line:
                square.resetAlgorithmData()

        while self.finding:
            # Check if way possible
            if len(self.openSet) > 0:
                winner = 0
                for i in range(len(self.openSet)):
                    # Check if found shorter way
                    if self.openSet[i].f < self.openSet[winner].f:
                        winner = i
                # Update shortest way
                current = self.openSet[winner]
                if current == end:
                    self.finding = False

                # Shift the current square in the close sets...
                self.openSet.remove(current)
                self.closedSet.append(current)

                # Get the neighbours of the current square...
                currentNeighbours = current.getNeighbours()

                for i in range(len(currentNeighbours)):
                    neighbour = currentNeighbours[i]
                    newPath = False
                    # Check if g should be updated...
                    if not neighbour in self.closedSet and neighbour.state != True:
                        tG = current.g + 1
                        if neighbour in self.openSet:
                            if tG < neighbour.g:
                                # Update g
                                neighbour.g = tG
                                newPath = True
                        else:
                            # Update g...
                            neighbour.g = tG
                            self.openSet.append(neighbour)
                            newPath = True
                        if newPath:
                            # Update the other variables if g updated...
                            neighbour.h = self.heuristic(neighbour, end)
                            neighbour.f = neighbour.g + neighbour.h
                            neighbour.previous = current
                # Find path and store...
                path = []
                t = current
                path.append(self.start)
                while t.previous != None:
                    path.append(t)
                    t = t.previous
            else:
                self.finding = False
                # Draw the path...
                self.draw(self.parent.image)
                if not preview:
                    self.executingPath = False
                    info("No solution!")
                    QtGui.QMessageBox.warning(None, "A*", "No solution!", "Ok")
                return

        self.countTries = 0

        if preview:
            self.previewPath = path
        else:
            self.executingPath = True
            self.path = path

            self.parent.bluetooth.send(
            Message("current", "%d:%d:%d" % (
                self.current.x(), self.current.y(), self.currentOrientation)))


            # Send the commands for the path to the ev3...
            self.parent.bluetooth.send(self.getPathCommand(path))

    def getPathCommand(self, path):
        """Put all commands for the ev3 in a list"""
        # There is a solution...
        commands = []

        # Put the first square to the end...
        path.append(path[0])
        del path[0]

        # Get the current orientation...
        currentOrientation = self.currentOrientation

        i = 0

        while i < len(path):
            # Get the current and next square...
            currentSquare = path[len(path) - i - 1]
            nextSquare = path[len(path) - i - 2]
            if i == len(path) - 1:
                break

            # Get the next orientation...
            if nextSquare.x() > currentSquare.x():
                nextOrientation = 1
            elif nextSquare.x() < currentSquare.x():
                nextOrientation = 3
            elif nextSquare.y() < currentSquare.y():
                nextOrientation = 0
            elif nextSquare.y() > currentSquare.y():
                nextOrientation = 2

            # Create command...
            if nextOrientation == currentOrientation:
                if len(commands) > 0 and commands[-1].channel == "forward":
                    commands[-1].value += 1
                else:
                    commands.append(Message("forward", 1))
                i += 1
            else:
                commands.append(Message("turn", nextOrientation))
                currentOrientation = nextOrientation

        value = ""

        for command in commands:
            value += command.channel + ":" + str(command.value) + "|"

        command = Message(channel="path", value=value[:-1])

        return command

    def heuristic(self, a, b):
        """Calculate the distance to the end square"""
        return abs(a.x() - b.x()) + abs(a.y() - b.y())

    def setZoom(self, delta):
        """Set the zoom factor"""
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
            self.sizeX += x * -1

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
                self.startPos.setY(self.startPos.y() - (self.squareSize *
                                                        self.zoom + 1))
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
            if x < 0:
                x = 0
            if y < 0:
                y = 0

        return self.grid[y][x]

    def getSquareAtCoordinate(self, x, y):
        """Return the square in the grid with the given coodinate"""
        # Notice the x and y position of the square...
        squarePosX = 0
        squarePosY = 0

        # Find the square with the given coordinates...
        while True:
            # Get the rect...
            square = Square(self, x=squarePosX, y=squarePosY)
            squareBottom = Square(self, x=squarePosX, y=squarePosY+1)
            squareRight = Square(self, x=squarePosX+1, y=squarePosY)
            rect = square.rect()

            # If coordinate in rect, return the position...
            if x >= rect.x() and x < squareRight.rect().x() and y >= rect.y() and y < squareBottom.rect().y():
                return square

            # If coordinate is not in rect, set the next rect...
            else:
                if x < rect.x():
                    squarePosX -= 1
                elif x >= squareRight.rect().x():
                    squarePosX += 1

                if y < rect.y():
                    squarePosY -= 1
                elif y >= squareBottom.rect().y():
                    squarePosY += 1


    def isSquareInGrid(self, square):
        """Check if the given coordinate in the current grid"""
        x = square.x()
        y = square.y()
        if x < 0 or y < 0:
            return False
        elif x >= self.sizeX or y >= self.sizeY:
            return False
        return True

    def draw(self, image):
        """Draw the image"""

        # Reset old image...
        image.fill(QtGui.qRgb(150, 150, 150))

        # Create the painter...
        painter = QtGui.QPainter(image)

        # Draw each square...
        y = 0
        for line in self.grid:
            x = 0
            for square in line:
                if square == self.current:
                    square.draw(painter, (255, 255, 0))
                    square.drawOrientation(painter, self.currentOrientation)
                elif square.state:
                    square.draw(painter, (250, 250, 250))
                elif square in self.path:
                    square.draw(painter, (0, 0, 255))
                elif square in self.previewPath and self.parent.settings.get("showPreviewPath"):
                    square.draw(painter, (120, 120, 200))
                elif square in self.openSet and self.parent.settings.get("showSets"):
                    square.draw(painter, (0, 255, 0))
                elif square in self.closedSet and self.parent.settings.get("showSets"):
                    square.draw(painter, (255, 0, 0))
                elif square.state == False:
                    square.draw(painter, (0, 0, 0))
                elif square.state == None and self.parent.settings.get(
                        "showFloorSquare"):
                    square.draw(painter, (100, 100, 100))

                x += 1
            y += 1

        # End painter and update the image...
        painter.end()
        self.parent.modified = True
        self.parent.update()

    def load(self, filename):
        """Load the old grid from a text file"""
        try:
            # Open the file...
            file = open(filename, "r")

            # Read each line...
            for line in file:
                coordinates = line.split(":")
                x = int(coordinates[0])
                y = int(coordinates[1])

                self.addSquare(x, y, True)
        except:
            debug("Cannot find file: %s" % filename)

    def save(self, filename):
        """Save the current grid in a text file"""
        file = open(filename, "w")

        # Write a line for each wall (x:y)...
        for line in self.grid:
            for square in line:
                if square.state == True:
                    file.write("%d:%d\n" % (square.x(), square.y()))
        file.close()


class RoomWidget(QtGui.QWidget):
    """This class displays the room with all barriers and etc."""

    def __init__(self, parent, settings, bluetooth):
        super(RoomWidget, self).__init__(parent=parent)

        # Create image...
        self.image = QtGui.QImage(
            QtCore.QSize(self.width(), self.height()),
            QtGui.QImage.Format_RGB32)

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
        self.squareAtMousePos = None

        # Set mouse tracking to true...
        self.setMouseTracking(True)

        # Load the old grid
        self.grid.load(gridFile)

        # Add listener...
        self.bluetooth.addListener("current", self.setCurrent, updating=False)
        self.bluetooth.addListener("path", self.pathFeedback, updating=False)
        self.bluetooth.addListener("wall", self.setWall, updating=False)

    def pathFeedback(self, value):
        """Get the path feedback and calcutates the path new"""
        if value == "failed":
            self.grid.findOnesWay(self.grid.end)
            # Draw the image...
            self.grid.draw(self.image)
        elif value == "error":
            self.grid.executingPath = False
            QtGui.QMessageBox.warning(None, "EV3", "Unknown problem occured!", "Ok")
        elif value == "Success":
            self.grid.executingPath = False

    def setWall(self, value):
        """Set a wall in the grid"""
        x, y = value.split(":")
        square = self.grid.getSquare(int(x), int(y))
        square.updateState(True)

    def setCurrent(self, value):
        """Set the current position"""

        # Delete current position in the path...
        if self.grid.current in self.grid.path:
            del self.grid.path[self.grid.path.index(self.grid.current)]

        values = value.split(":")

        # Set the current square...
        self.grid.current = self.grid.getSquare(int(values[0]), int(values[1]))

        # Set the current orientation...
        self.grid.currentOrientation = int(values[2])

        # Update the preview path...
        self.grid.findOnesWay(self.squareAtMousePos, preview = True)

        # Draw the square...
        self.grid.draw(self.image)

    def contextMenu(self, pos):
        """show the context menu"""
        # Create the menu...
        self.menu = QtGui.QMenu(self)

        # Add the actions...
        self.menu.addAction("Set start position", self.onStartPos)
        self.menu.addAction("Set end position", self.onEndPos)
        self.menu.addAction("Stop path", self.onStopPath)
        self.menu.addAction("Center", self.onCenter)
        self.menu.addAction("Reset zoom", self.onResetZoom)
        self.menu.addAction("Reset grid", self.onResetGrid)

        # Show the menu on the click position...
        self.menu.exec_(self.mapToGlobal(pos))

    def onStartPos(self):
        """Set the start position"""
        clickedSquare = self.grid.getSquareAtCoordinate(self.mousePos.x(),
                                                        self.mousePos.y())
        self.grid.current = self.grid.getSquare(clickedSquare.x(),
                                                clickedSquare.y())

        # Draw the square...
        self.grid.draw(self.image)

    def onEndPos(self):
        """Set the end position of the algorithm"""
        if self.grid.executingPath:
            question = QtGui.QMessageBox.question(None, "EV3", "Stop EV3 and find new path?", "Ok", "Cancel")
            if question == 1:
                return

            self.bluetooth.send(Message("path", "stop"))

        clickedSquare = self.grid.getSquareAtCoordinate(self.mousePos.x(),
                                                        self.mousePos.y())
        self.grid.findOnesWay(
            self.grid.getSquare(clickedSquare.x(), clickedSquare.y()))

        # Draw the grid...
        self.grid.draw(self.image)
        
    def onStopPath(self):
        """Stop the path on the ev3"""
        self.bluetooth.send(Message("path", "stop"))
        self.grid.path = []
        
        # Draw the image...
        self.grid.draw(self.image)

    def onResetGrid(self):
        """Reset the grid"""
        self.grid = Grid(self)

        # Draw the image...
        self.grid.draw(self.image)

    def onResetZoom(self):
        """Set zoom to default"""

        # Set zoom to default...
        self.grid.zoom = 0.9

        # Scale and center the grid...
        self.grid.scale = True
        center_temp = self.grid.center
        self.grid.center = True

        # Draw the image...
        self.grid.draw(self.image)

        # Reset scaling and centering...
        self.grid.center = center_temp

    def onCenter(self):
        """Center the image"""
        # Activate centering...
        self.grid.center = True

        # Draw the image...
        self.grid.draw(self.image)

    def mouseReleaseEvent(self, event):
        """When the mouse wasn't moved, find square on the click position"""
        # Allow a small moving...
        if self.moved < 5:
            # Set the end position of the path...
            self.onEndPos()

    def mousePressEvent(self, event):
        """Called when the mouse is pressed"""

        # Update moved...
        self.moved = 0

        # Update the last click position...
        self.mousePos = event.pos()

        # If it's a right click, open the context menu...
        if event.button() == QtCore.Qt.RightButton:
            self.contextMenu(event.pos())

    def mouseMoveEvent(self, event):
        """Get difference to the last mouse event"""

        if event.buttons() == QtCore.Qt.NoButton and self.parent.settings.get("showPreviewPath"):
            pos = event.pos()
            # Get the square at the mouse position...
            square = self.grid.getSquareAtCoordinate(pos.x(), pos.y())
            # If the square is the same like the last time break up the process...
            if self.squareAtMousePos != None:
                if square.x() == self.squareAtMousePos.x() and square.y() == self.squareAtMousePos.y():
                    return
            # If the square is not in the current grid break up the process...
            if not self.grid.isSquareInGrid(square):
                return
            square = self.grid.getSquare(square.x(), square.y())
            self.squareAtMousePos = square
            # Get the path to the square...
            self.grid.findOnesWay(square, preview = True)
            # Draw the image...
            self.grid.draw(self.image)

        elif event.buttons() == QtCore.Qt.LeftButton:
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
            self.grid.draw(self.image)

    def wheelEvent(self, event):
        """Called when the mouse wheel spin"""
        self.grid.setZoom(event.delta())

        # Draw the image...
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
        self.grid.draw(self.image)

    def resizeImage(self, image, newSize):
        """Resize the image and draw it again"""
        if image.size() == newSize:
            return

        # Create a new image with new size and re-draw the rail network
        self.image = QtGui.QImage(newSize, QtGui.QImage.Format_RGB32)
        self.image.fill(QtGui.qRgb(150, 150, 150))

        # Paint the image...
        self.grid.draw(self.image)

    def closeEvent(self, event):
        """Save the grid"""
        self.grid.save(gridFile)
