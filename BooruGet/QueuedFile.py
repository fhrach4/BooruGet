import os

"""
Represents a file to be downloaded, it's much cleaner as a class than a goddamn
array
"""
class QueuedFile:
    URL
    fileName
    extension
    destination
    path

    def __init__(self, URL, fileName, extension, destination):
        self.URL = URL
        self.fileName = fileName
        self.extension = extension
        self.destination = destination
        path = os.path.join(destination, fileName + extension)
