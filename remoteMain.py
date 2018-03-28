#!/usr/bin/python3

# This is the main file for the remote application
# Author: Finn G.

import remote.remoteGUI as gui
from constants import *
from logger import *

setLogLevel(logLevel)

info("Started")

gui.RemoteGUI()
