"""
Frank Hrach
Booru.py
"""

from abc import ABCMeta, abstractmethod

class Booru(object):
    """
    Abstract class which represents a Booru site.

    I might be using python wrong
    """
    __metaclass = ABCMeta

    URL = None

    #argument variables
    any_size = False

    targetWidth = -1
    targetHeight = -1
    error = 0

    @abstractmethod
    def __init__(self, width, height, error, arguments):
        self.target_width = width
        self.target_height = height
        self.error = error

        self.any_size = arguments.anysize



    @abstractmethod
    def get_results(self):
        pass


