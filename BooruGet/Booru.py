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
    __metaclass__ = ABCMeta

    URL = None

    #argument variables
    any_size = False

    searchString = ""
    targetWidth = -1
    targetHeight = -1
    error = 0

    @abstractmethod
    def __init__(self, arguments, download_manager):
        self.target_width = arguments.target_width
        self.target_height = arguments.target_height
        self.error = arguments.error
        self.any_size = arguments.any_size



    @abstractmethod
    def get_results(self):
        pass


