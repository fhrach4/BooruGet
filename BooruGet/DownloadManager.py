"""
Frank Hrach
DownloadManager.py
"""

import httplib2
import os
import QueuedFile

from threading import Thread

class DownloadManager(Thread):
    """
    Class which manages files to download in a queue which is limited to
    a supplied number of concurrent downloads
    """

    def __init__(self, event, root):


        """
        Constructor for DownloadManager

        event -> the event manager for threading
        out_dir -> the location of the download folders
        """
        Thread.__init__(self)

        self.max_downloads = 4
        self.current_downloads = 0
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

            # if the queue is not full, signal the thread to wake
            if len(self.queue) < self.max_downloads:
                self.event.set()

    def start_downloader(self):
        """
        Manages the downloads with a queue.
        Should be started as a thread
        """

        # run until main thread says it should no longer run
        while self.should_run:

            # if the queue is empty tell the thread to wait
            if self.current_downloads > self.max_downloads or len(self.queue) == 0:
                self.event.clear()
            elif self.current_downloads <= self.max_downloads and len(self.queue) != 0:
                self.current_downloads += 1
                thread = Thread(target=self.download, \
                    args=(self.queue.pop() ,self.event))
                thread.start()
            else:
                # wait until download thread notifies all
                print("Wait", self.current_downloads)
                self.event.wait()

    def run(self):
        self.start_downloader()

    def should_download(self, queued_file):
        """
        Checks to see if a file already exists in the destination
        """
        path = os.path.join(queued_file.destination, queued_file.file_name \
            + "." + queued_file.extension)

        return not os.path.exists(path)



class WorkerThread(Thread):
    def __init__(self, event):
        self.event = event
        self.queued_file = ""
        self.should_run = True
        self.downloading = False

    def run():
        while(self.should_run):
            if self.url != "":
                self.event.wait()
            else:
                self.downloading = True;
                download()
                self.download = False;

    def download(self):
        """
        Downloads the supplied file
        """
        path = os.path.join(queued_file.destination, queued_file.file_name \
            + "." + queued_file.extension)
        connection = httplib2.Http(".cache")

        request, content = connection.request(queued_file.url, "GET")

        local_file = open(path, "wb")
        local_file.write(content)
        local_file.close()
