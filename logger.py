# A wrapper for the logging package
# Author: Jan-Luca D.

import logging

# Create some wrapper variables for static use
INFO = logging.INFO
DEBUG = logging.DEBUG
ERROR = logging.ERROR
WARN = logging.WARN

# Save log level...
_level = None


def setLogLevel(level):
    """Configure the logger for the specific use case"""
    global _level
    _level = level
    logging.basicConfig(format='%(levelname)s: %(message)s', level=level)


def getLogLevel():
    """Return the current log level"""
    return _level


# Output the data to log
def info(msg):
    logging.info(msg)


def debug(msg):
    logging.debug(msg)


def error(msg):
    logging.error(msg)


def warn(msg):
    logging.warning(msg)
