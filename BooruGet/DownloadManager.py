"""
Frank Hrach
DownloadManager.py
"""

import urllib
import os
import QueuedFile
import threadding

Queued_Files

"""
Download the supplied url and saves it to the supplied path
"""
class DownloadManager:
    maxDownloads
    run
    queue

    def __init__(self):
        self.maxDownloads = 4
        run = True;

    def download(self, url, fileName, extension,  destination):
        path = os.path.join(destination, fileName + "." + extension)
        if not os.path.exists(path):
            urllib.urlretrieve(url + fileName + extension, path)

    def enqueueFile( self, URL, fileName, extension, destination):
        queue.add(File(URL, fileName, extension, destination))

    def main():

