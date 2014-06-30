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
    Download the supplied url and saves it to the supplied path
    """
    #maxDownloads
    #currentDownloads;
    #run
    #queue

    def __init__(self, event, root):

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
        self.queue.append(
            QueuedFile.QueuedFile(image["url"], image["md5"], \
            image["file_ext"], path))

        if not os.path.exists(path):
            os.mkdir(path)

        self.event.set()

    def start_downloader(self):
        """
        Manages 4 downloads with a queue.
        Should be started as a thread
        """

        # run until main thread says it should no longer run
        while self.should_run:
            if self.current_downloads <= self.max_downloads and \
                len(self.queue) != 0:
                thread = Thread(target=self.download, \
                    args=(self.queue.pop(),self.event))
                thread.start()
                self.current_downloads += 1
            else:
                # wait until download thread notifies all
                self.event.wait()

    def run(self):
        self.start_downloader()


    def download(self, queued_file, event):
        """
        Downloads
        """
        print('Downloading ' + queued_file.url + '\tqueue length: ' + str(len(self.queue)))
        path = os.path.join(queued_file.destination, queued_file.file_name \
            + "." + queued_file.extension)

        # download only if the file does not already exist
        if not os.path.exists(path):

            connection = httplib2.Http(".cache")
            request, content = connection.request(queued_file.url, "GET")

            local_file = open(path, "wb")
            local_file.write(content)
            local_file.close()

            #urllib.requests..urlretrieve(queued_file.url + queued_file.file_name \
                #+ queued_file.extension, path)

        # Notify the controller that we have finished
        self.current_downloads  -= 1
        event.set()
