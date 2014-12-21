"""
Frank Hrach
Gelbooru.py
Sun Mar  9 22:29:53 EDT 2014
"""

from Booru import Booru
import Filter
import httplib2
import math
import time
import datetime
import os
import xml.etree.ElementTree as ET

from threading import Thread
from urllib.parse import urlparse


class GelbooruDownloader(Booru, Thread):
    """
    Holds all the methods and data required to download files from gelbooru
    """

    url = "http://gelbooru.com/index.php?page=dapi&s=post&q=index"
    number_per_page = 100

    searchString = ""
    target_width = -1
    target_height = -1

    page_num = 0
    number_of_pages = 1000
    number_per_page = 100

    def __init__(self, args, download_manager):
        """
        """

        Booru.__init__(self, args, download_manager)
        Thread.__init__(self)

        self.search_string = args.search_string
        self.target_width = args.target_width
        self.target_height = args.target_height
        self.error = args.error
        self.verbose = args.verbose
        self.tags = args.search_string
        self.download_manager = download_manager
        self.image_filter = Filter.Filter(args)


    def get_results(self):
        """
        Connects to the server and gets a page worth of results
        """
        if self.verbose:
            print("Gelbooru: Reqesting page")
        try:
            connection = httplib2.Http(".cache")
            res, content = connection.request(
                self.url + "&tags=" + self.search_string + "&pid=" +
                str(self.page_num) + "&limit=" + str(self.number_per_page))
            if self.verbose:
                print("\tResults recieved")
            if not res.status == 200:
                if self.verbose:
                    print("\tResponse was not 200 (" + res.status + ")")
                else:
                    print("Error with search, trying again")
                time.sleep(5000)
                self.get_results()
            if len(content) >= 0:
                if self.verbose:
                    print("\tResponse was 200")
                    print("Done")
                return ET.fromstring(content)
            else:
                return None
        except httplib2.ServerNotFoundError:
            print("Could not contact server at gelbooru.com")
            print("Retrying in 30 seconds")
            time.sleep(30)
            self.get_results()
        return None

    def download(self):
        """
        """
        #TODO write documentation for download
        # connect once to get the number of pages for the search
        root = self.get_results()
        self.number_of_pages = int(
            math.ceil(int(root.attrib["count"]) / float(len(root))))

        for i in range(0, self.number_of_pages + 1):
            # sleep to ensure we are not spamming the server
            time.sleep(0.2)

            # Get page from the server
            root = self.get_results()

            if self.verbose:
                print("Gelbooru: current page: " + str(i) + " (" + \
                    str(i * self.number_per_page) + ") out of " + \
                    str(self.number_of_pages) + \
                    " pages(" + root.attrib["count"] + ")")

            try:
                for child in root:
                    image = {}
                    image["md5"] = child.attrib["md5"]
                    image["image_height"] = int(child.attrib["height"])
                    image["image_width"] = int(child.attrib["width"])
                    image["rating"] = child.attrib["rating"]
                    image["tag_string"] = child.attrib["tags"]
                    url = urlparse(child.attrib["file_url"]).path
                    image["file_ext"] = (os.path.splitext(url)[1]).strip('.')
                    image["url"] = child.attrib["file_url"]


                    if self.image_filter.filter_result(image):
                        if self.verbose:
                            print(image["md5"])
                        self.download_manager.enqueue_file(image, self.tags)
            except(IndexError):
                print("Unexpected End of results")
                break

            except KeyError as e:
                if not os.path.exists("error.log"):
                    f = open("error.log", "w")
                    f.write('')
                    f.close()
                f = open("error.log", 'w')
                f.write("Gelbooru " + str(datetime.datetime.now()))
                f.write(" ~ ")
                f.write(str(result[j]))
                f.write(" ~ ")
                f.write("KeyError:" +  str(e))
                f.write('\n')
                f.close()
                print("A key error has occured for Gelbooru and the search on the site has been terminted")
                print("Please consider sending the results of error.txt to the developer")
                break

            self.page_num += 1

        print("Gelbooru: Finished searching")


    def run(self):
        if self.verbose:
            print("Starting Gelbooru Thread")
        self.download()
