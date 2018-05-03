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
                    # Try to convert the value in an integer...
                    value = int(value)
                except:
                    # If converting in an integer failed, convert the value in a boolean...
                    if value == "True":
                        value = True
                    elif value == "False":
                        value = False
                
                # Add the key and value to the dictionary...
                self.settings[fragments[0]] = value
            file.close()
        except:
            error("Cannot find the settings file")

    def get(self, key, default = None):
        """Get a value in the settings"""
        # If the key is in the settings, return the value...
        if key in self.settings:
            return self.settings[key]
            
        # If the key is not in the settings, return the default value...
        else:
            if default != None: 
                self.settings[key] = default
            return default

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
