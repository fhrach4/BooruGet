"""
Frank Hrach
DownloadManager.py
"""

import urllib
import os
import QueuedFile
import threading

class DownloadManager(object):
    """
    Download the supplied url and saves it to the supplied path
    """
    #maxDownloads
    #currentDownloads;
    #run
    #queue

    def __init__(self, event, out_dir):
        """
        Constructor for DownloadManager

        event -> the event manager for threadding
        out_dir -> the location of the download folders
        """
        self.max_downloads = 4
        self.current_downloads = 0
        self.queue = []
        self.should_run = True
        self.event = event
        self.out_dir = out_dir


    def enqueue_file(self, image, destination):
        """
        Adds a file to the queue
        """
        self.queue.append(
            QueuedFile.QueuedFile(image["url"], image["file_name"], \
            image["extension"], destination))

    def start_downloader(self):
        """
        Manages 4 downloads with a queue.
        Should be started as a thread
        """

        # run until main thread says it should no longer run
        while self.should_run:

            if self.current_downloads >= self.max_downloads:
                thread = threading.Thread(target=download, args=self.queue.pop())
            else:
                # wait until download thread notifies all
                self.event.wait()

    def init_outdir(self):
        """
        Creates the output directory if it does not already exist
        """
        if not os.path.exists(self.out_dir):
            os.mkdir(self.out_dir)


def download(queued_file, event):
    """
    Downloads
    """
    path = os.path.join(queued_file.destination, queued_file.file_name \
        + "." + queued_file.extension)

    # download only if the file does not already exist
    if not os.path.exists(path):
        urllib.urlretrieve(queued_file.url + queued_file.file_name \
            + queued_file.extension, path)

    # Notify the controller that we have finished
    event.notifyAll()
