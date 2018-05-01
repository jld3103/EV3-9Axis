# Settings file
# Author: Finn G.

from utils import *
from constants import *

setLogLevel(logLevel)

class Settings():

    settings = {}

    def __init__(self):
        try:
            # Open the file...
            file = open(".settings.txt", "r")

            # Read each line and put the settings in the dictionary...
            for line in file:
                fragments = line.strip().split(":")
                value = fragments[1]
                try:
                    value = int(value)
                except:
                    if value == "True":
                        value = True
                    elif value == "False":
                        value = False

                self.settings[fragments[0]] = value
            file.close()
        except:
            error("Cannot found the settings file")

    def get(self, key):
        """Get a value in the settings"""
        try:
            return self.settings[key]
        except:
            return None

    def set(self, key, value):
        """Set a value in the dictionary"""
        self.settings[key] = value

    def save(self):
        """"Write the settings"""

        # Open the file...
        file = open(".settings.txt", "w")

        # Write all settings in the file...
        for key in self.settings:
            file.write("%s:%s\n" % (key, self.settings[key]))
