"""
Frank Hrach
Booru.py
"""

from abc import ABCMeta, abstractmethod
import urllib
import os

class Booru:
    __metaclass = ABCMeta

    URL = None

    #argument variables
    anySize = False;

    targetWidth = -1
    targetHeight = -1
    error = 0

    @abstractmethod
    def __init__(self, width, height, error, arguments):
        self.targetWidth = width
        self.targetHeight = height
        self.error = error

        self.anySize = arguments.anysize



    @abstractmethod
    def getResults(self):
        pass


