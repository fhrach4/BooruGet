"""
Frank Hrach
QueuedFile.py
"""

import os

class QueuedFile(object):
    """
    Represents a file to be downloaded, it's much cleaner as a class than a goddamn
    array
    """

    def __init__(self, url, file_name, extension, destination):
        self.url = url
        self.file_name = file_name
        self.extension = extension
        self.destination = destination
        self.path = os.path.join(destination, file_name + extension)
