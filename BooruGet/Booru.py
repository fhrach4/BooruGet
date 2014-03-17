"""
Frank Hrach
Booru.py
Sun Mar  9 22:29:53 EDT 2014
"""

from abc import ABCMeta, abstractmethod


class Booru:
    __metaclass = ABCMeta

    URL = None

    #argument variables
    anySize = false;

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
    def Download(self):
        pass

    @abstractmethod
    def getResults(self):
        pass


