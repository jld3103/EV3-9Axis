# Utils file
# Author: Jan-Luca D.

import os.path
import platform
import subprocess


def writeFile(filename, text):
    """Write some data to a file"""
    file = open(filename, "w")
    file.write(text)
    file.close()


def readFile(filename):
    """Read data from file"""
    file = open(filename, "r")
    return file.read()


def existsFile(filename):
    """Check if file exists"""
    return os.path.isfile(filename)


def getOS():
    """Get the OS of the device"""
    return platform.system()


def runCommand(cmd):
    """Runs a command from the OS"""
    return subprocess.getoutput(cmd).split()[0]
