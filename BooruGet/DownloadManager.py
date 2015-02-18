"""
Frank Hrach
DownloadManager.py
"""

import httplib2
import os
import QueuedFile
import time

from threading import Thread

class DownloadManager(Thread):
    """
    Class which manages files to download in a queue which is limited to
    a supplied number of concurrent downloads
    """

    thread_pool = None

    def __init__(self, event, root):


        """
        Constructor for DownloadManager

        event -> the event manager for threading
        out_dir -> the location of the download folders
        """
        Thread.__init__(self)

        self.queue = []
        self.should_run = True
        self.event = event
        self.root = root


    def enqueue_file(self, image, destination):
        """
        Adds a file to the queue
        """
        path = os.path.join(self.root, destination)

        image_to_apend = QueuedFile.QueuedFile(image["url"], image["md5"], \
            image["file_ext"], path)

        if self.should_download(image_to_apend):
            self.queue.append(image_to_apend)

    def start_downloader(self):
        """
        Manages the downloads with a queue.
        Should be started as a thread
        """

        # run until main thread says it should no longer run
        while self.should_run or len(self.queue) > 0:
            # if the queue is empty tell the thread to wait
            if len(self.queue) != 0:
                    self.download(self.queue.pop())
            else:
                # check the queue every 5 seconds
                time.sleep(5)

    def run(self):
        self.start_downloader()

    def should_download(self, queued_file):
        """
        Checks to see if a file already exists in the destination
        """
        path = os.path.join(queued_file.destination, queued_file.file_name \
            + "." + queued_file.extension)

        return not os.path.exists(path)


    def download(self, queued_file):
        """
        Downloads the supplied file
        """
        path = os.path.join(queued_file.destination, queued_file.file_name \
            + "." + queued_file.extension)
        connection = httplib2.Http(".cache")

        request, content = connection.request(queued_file.url, "GET")

        local_file = open(path, "wb+")
        local_file.write(content)
        local_file.close()
