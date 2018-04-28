#!/usr/bin/python3

# This widget displays the room
# Author: Finn G.

from PyQt4 import QtGui,  QtCore
from constants import *
from logger import *

setLogLevel(logLevel)


class Square():
    """This class describes a square"""
    def __init__(self, grid, x=None, y=None, state=None):
        self.grid = grid
        
        self._x = x
        self._y = y

        self.state = state
        
    def x(self):
        """Get x coordinate in the room"""
        if self._x == None:
            # Get position in the grid...
            for line in self.grid.grid:
                if self in line:
                    return line.index(self)
        else:
            return self._x
        
    def y(self):
        """Get y coordinate in the room"""
        if self._y == None:
            # Get position in the grid...
            for line in self.grid.grid:
                if self in line:
                    return self.grid.grid.index(line)
        else:
            return self._y
                
    def rect(self):
        """Calculate the rect of the square"""
        
        # Get size of the image...
        width = self.grid.parent.width()
        height = self.grid.parent.height()
        
        # Get the size of the squares...
        squareWidht = int(width / (self.grid.sizeX))
        squareHeight = int(height / (self.grid.sizeY))
        
        # Take the smaller site for the width and height of the squares...
        
        self.grid.scaledSquareSize = (min(squareWidht, squareHeight) - 3)
        
        if self.grid.scale:
            self.grid.squareSize = self.grid.scaledSquareSize
            
        squareSizeZoomed = self.grid.squareSize * self.grid.zoom
        
        # Calculate the border for drawing the romm in the center of the image...
        borderLeft = (width - self.grid.sizeX*(squareSizeZoomed+1)) / 2
        borderTop = (height - self.grid.sizeY*(squareSizeZoomed+1)) / 2
        
        # Get start position of the square...
        if self.grid.center:
            self.grid.startPosition = QtCore.QPoint(borderLeft+self.x()*(squareSizeZoomed+1), borderTop+self.y()*(squareSizeZoomed+1))
            self.grid.startPos = QtCore.QPoint(borderLeft, borderTop)
        else:
            self.grid.startPosition = QtCore.QPoint(self.grid.startPos.x()+self.x()*(squareSizeZoomed+1), self.grid.startPos.y()+self.y()*(squareSizeZoomed+1))
        
        # Return the rect...
        return QtCore.QRect(self.grid.startPosition.x(), self.grid.startPosition.y(), squareSizeZoomed, squareSizeZoomed)

        
    def updateState(self, newState):
        self.state = newState

class Grid():
    """This class manage the squares"""
    def __init__(self, parent):
        # Define the grid with only one undefined square...
        self.grid = [[Square(self)]]
        
        # Define the grid sizes...
        self.sizeX = 1
        self.sizeY = 1
        
        # Define parent...
        self.parent = parent
        
        # Settings...
        self.showUndefinedSquares = False
        self.zoom = 0.8
        self.center = True
        self.scale = True
        self.squareSize = 20
        self.scaledSquareSize = 20
        self.startPos = QtCore.QPoint(0, 0)
        
    def setZoom(self, delta):
        # Zoom in or out...
        if delta < 0:
            self.zoom -= 0.1
        else:
            self.zoom += 0.1
        
        # Set zoom bigger than 0.1...
        if self.zoom < 0.1:
            self.zoom = 0.1
            
        # Update zoom factor to the scaled square size...
        factor = self.scaledSquareSize / self.squareSize
        self.zoom /= factor
        
        # Scale the grid...
        self.squareSize = self.scaledSquareSize
        
    def addSquare(self, x, y, state):
        """Add a square with the state in the grid"""
        
        # If the x coordinate bigger than the current grid, increase the grid...
        if x > self.sizeX-1:
            for i in range(x-self.sizeX+1):
                for line in self.grid:
                    line.append(Square(self))
                self.sizeX += 1
        
        # If the y coordinate bigger than the current grid, increase the grid...
        if y > self.sizeY-1:
            for i in range(y-self.sizeY+1):
                line = []
                for j in range(self.sizeX):
                    line.append(Square(self))
                self.grid.append(line)
                self.sizeY += 1
        
        # If the x coordinate smaller than zero, add columns at the left site...
        if x < 0:
            index = 0
            for line in self.grid:
                for i in range(x*-1):
                    line.insert(0, Square(self))
                index += 1
            self.sizeX += x*-1
            
            # Set start position...
            self.startPos.setX(self.startPos.x()-((self.squareSize*self.zoom+1)*(x*-1)))
            
            # Set the x coordinate to zero...
            x = 0

        # If the y coordinate smaller than zero, add columns at the top...
        if y < 0:
            for i in range(y*-1):
                line = []
                for j in range(self.sizeX):
                    line.append(Square(self))
                self.grid.insert(0, line)
                self.sizeY += 1
                # Set start position...
                self.startPos.setY(self.startPos.y()-(self.squareSize*self.zoom+1))
            y = 0
        
        # Set the square on the given state...
        if self.grid[y][x].state == None:
            self.grid[y][x].updateState(state)
            # Update image...
            self.draw(self.parent.image)
        else:
            error("Square already defined")
            return
            
    def updateSquareState(self, x, y, state):
        # Set the square on the given state...
        try:
            self.grid[y][x].updateState(state)
        except:
            error("Square is not defined")
            
    def getSquareAtCoordinate(self, x, y):
        """Return the square in the grid with the given coodinate"""
        # Notice the x and y position of the square...
        squarePosX = 0
        squarePosY = 0
                        
        # Find the square with the given coordinates...
        for i in range(1000):            # TODO: Do not stop after 1000 trys...
            # Get the rect...
            square = Square(self, x=squarePosX, y=squarePosY)
            rect =  square.rect()
            
            # If coordinate in rect, return the position...
            if x >= rect.x() and x <= (rect.x() + rect.width()) and y >= rect.y() and y <= (rect.y() + rect.height()):
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
                    
        return None
            
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
                if square.state == None and self.showUndefinedSquares:
                    painter.fillRect(square.rect(), QtGui.QColor(100, 100, 100)) 
                if square.state == 0:
                    painter.fillRect(square.rect(), QtGui.QColor(0, 0, 0)) 
                if square.state == 1:
                    painter.fillRect(square.rect(), QtGui.QColor(250, 250, 250))
                x += 1
            y += 1
            
        # End painter and update the image...
        painter.end()
        self.parent.modified = True
        self.parent.update()
        
    def load(self, filename):
        file = open(filename, "r")
        
        for line in file:
            values = line.split(" - ")
            coordinates = values[0].split(":")
            x = int(coordinates[0])
            y = int(coordinates[1])
            state = int(values[1].strip())
            
            self.addSquare(x, y, state)
        
    def save(self, filename):
        file = open(filename, "w")
        
        for line in self.grid:
            for square in line:
                if square.state != None:
                    file.write("%d:%d - %d\n" % (square.x(), square.y(), square.state))
        file.close()

class RoomWidget(QtGui.QWidget):
    """This class displays the room with all barriers and etc."""
    
    def __init__(self, parent, bluetooth):
        super(RoomWidget,  self).__init__(parent=parent)
        
        # Create image...
        self.image = QtGui.QImage(QtCore.QSize(self.width(), self.height()), QtGui.QImage.Format_RGB32)
        
        self.parent = parent
        self.bluetooth = bluetooth
        
        # Create grid...
        self.grid = Grid(self)
        
        # Check if mouse moved...
        self.moved = 0
        
        # Fill image...
        self.image.fill(QtGui.qRgb(150, 150, 150))
        
        # Save old mouse position...
        self.mousePos = None
        
        # Load old grid...
        self.grid.load("remote/textures/grid.txt")
                
    def contextMenu(self, pos):
        """show the context menu"""
        # Create the menu...
        self.menu = QtGui.QMenu(self)
        
        # Add the actions...
        self.menu.addAction("center", self.onCenter)
        self.menu.addAction("scale", self.onScale)
        self.menu.addAction("reset zoom", self.onResetZoom)
        self.menu.addAction("reset grid", self.onResetGrid)
        
        # Show the menu on the click position...
        self.menu.exec_(self.mapToGlobal(pos))
        
    def onResetGrid(self):
        """Reset the grid"""
        self.grid = Grid(self)
        
        # Draw the image...
        self.grid.draw(self.image)
        
    def onResetZoom(self):
        """Set zoom to default"""
        
        # Set zoom to defaul...
        self.grid.zoom = 1.0
        
        # Scale and center the grid only one time...
        scale_temp = self.grid.scale
        self.grid.scale = True
        center_temp = self.grid.center
        self.grid.center = True
        
        # Draw the image...
        self.grid.draw(self.image)
        
        # Reset scaling and centering...
        self.grid.scale = scale_temp
        self.grid.center = center_temp
        
    def onScale(self):
        """Scale the image"""
        
        # Set zoom to default and activate scaling...
        self.grid.zoom = 1.0
        self.grid.scale = True
        
        # Center the grid...
        center_temp = self.grid.center
        self.grid.center = True
        
        # Draw the image...
        self.grid.draw(self.image)
        
        # Reset centering...
        self.grid.center = center_temp
        
    def onCenter(self):
        """Center the image"""
        
        self.grid.center = True
        
        # Draw the image...
        self.grid.draw(self.image)
        
    def mouseReleaseEvent(self, event):
        """When the mouse wasn't moved, find square on the click position"""
        if self.moved < 2:
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

    def resizeImage(self, image, newSize):
        """Resize the image and draw it again"""
        if image.size() == newSize:
            return

        # Create a new image with new size and re-draw the rail network
        self.image = QtGui.QImage(newSize, QtGui.QImage.Format_RGB32)
        self.image.fill(QtGui.qRgb(150, 150, 150))
        
        self.grid.draw(self.image)
        
    def closeEvent(self, event):
        self.grid.save("remote/textures/grid.txt")
