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
        self.thread_pool = ThreadPool(4, event)


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
        while self.should_run:
            # if the queue is empty tell the thread to wait
            if len(self.queue) != 0 and self.thread_pool.can_downlaod():
                    self.thread_pool.assign_download(self.queue.pop())
            else:
                # check the queue every 5 seconds
                time.sleep(5)
        self.thread_pool.stop_all()

    def run(self):
        self.start_downloader()

    def should_download(self, queued_file):
        """
        Checks to see if a file already exists in the destination
        """
        path = os.path.join(queued_file.destination, queued_file.file_name \
            + "." + queued_file.extension)

        return not os.path.exists(path)



class ThreadPool:
    """
    TODO write docstring
    """
    threads = []
    event = None

    def __init__(self, num_threads, event):
        for i in range(0,num_threads):
            self.threads.append(WorkerThread(event))
            self.event = event

        for thread in self.threads:
            thread.start()

    def assign_download(self, q_file):
        """
        TODO write docstring
        """
        for thread in self.threads:
            if not thread.downloading:
                thread.queued_file = q_file
                self.event.set()
                break

    def can_downlaod(self):
        """
        Returns if there is a free download thread to handle the download
        """
        for thread in self.threads:
            if not thread.downloading:
                return True
        return False

    def stop_all(self):
        for thread in self.threads:
            thread.should_run = False
            self.event.set()

class WorkerThread(Thread):
    """
    TODO write docstring
    """
    queued_file = None

    def __init__(self, event):

        Thread.__init__(self)

        self.event = event
        self.queued_file = None
        self.should_run = True
        self.downloading = False

    def run(self):
        while self.should_run:
            if self.queued_file is None:
                self.downloading = False
                self.event.wait()
            else:
                self.downloading = True
                self.download()
                self.downloading = False

    def download(self):
        """
        Downloads the supplied file
        """
        path = os.path.join(self.queued_file.destination, self.queued_file.file_name \
            + "." + self.queued_file.extension)
        connection = httplib2.Http(".cache")

        request, content = connection.request(self.queued_file.url, "GET")

        local_file = open(path, "wb+")
        local_file.write(content)
        local_file.close()
        self.queued_file = None
