from Booru import Booru
import Filter
import httplib2
import json
import math
import time
import os
from threading import Thread

class DanbooruDownloader(Booru, Thread):
    """
    Holds all the methods and data required to download files from Danbooru
    utalizing it's public API. A Public API key is required which should be
    provided throuhg the download_manager
    """

    page_num = 0
    number_per_page = 100
    numper_of_pages = 1000

    urlbase = "http://danbooru.donmai.us/"


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

        # Danboru specific args
        try:
            self.username = args.username
            self.password = args.password
        except:
            #TODO handle failure/error output for missing username and or
            #password
            pass

    def get_results(self):
        """
        Gets a page of results from the server
        """
        # create connection
        if self.verbose:
            print("Danbooru: Reqesting page")
        try:
            connection = httplib2.Http(".cache")
            header = "posts.json?login=" + self.username + "&api_key=" + \
                self.password + "&limit=" + str(self.number_per_page) + "&"

            # make request
            if self.verbose:
                print("Making request: " + self.urlbase + header + "tags=" + self.tags + \
                    "&page=" + str(self.page_num))
            res, content = connection.request(
                self.urlbase + header + "tags=" + self.tags + "&page=" + str(self.page_num))
            if len(content) >= 0 and res.status == 200:
                if self.verbose:
                    print("Response recieved")
                return json.loads(content.decode())
            else:
                return res.status
        except (httplib2.ServerNotFoundError):
            print("Could not contact server at danbooru.donmai.us")
            print("Retrying in 30 seconds")
            time.sleep(30)
            self.getResultsJSON()
        return None

    def download(self):

        initial = self.get_results()

        for i in range(1, self.numper_of_pages + 1):

            # sleep to ensure we are not spamming the server
            time.sleep(0.2)

            if self.verbose:
                print("Danbooru: current page: " + str(i) + " of ~1000 (" + \
                    str(i * self.number_per_page) + ")")

            result = self.get_results()

            # handle case where user has been throttled by the server
            if result == 421:
                print("You have been throttled by the server and can no longer download files")
                print("This should end in one hour")

                break

            # Handle case where there is no result
            if result is None or len(result) <= 0:
                if self.verbose:
                    print("Breaking...")
                    if result is None:
                        print("\t result was NoneType")
                    elif len(result) == 0:
                        print("\t length of result was 0")
                    else:
                        print("\t an unknown error has happened")
                break

            for j in range(self.number_per_page):
                try:
                    result[j]["md5"]

                    image = {}
                    image["md5"] = result[j]["md5"]
                    image["image_height"] = int(result[j]["image_height"])
                    image["image_width"] = int(result[j]["image_width"])
                    image["rating"] = result[j]["rating"]
                    image["tag_string"] = self.tags
                    image["file_ext"] = result[j]["file_ext"]
                    image["url"] =  self.urlbase + "/data/" + image["md5"] \
                            + "." + image["file_ext"]

                    if self.image_filter.filter_result(image):
                        if self.verbose:
                            print(image)
                        self.download_manager.enqueue_file(image, self.tags)

                except (IndexError, TypeError):
                    print("Less than 100 images in this result ("\
                        + str(len(result)) + ")")
                    i = self.numper_of_pages + 2
                    j = self.number_per_page
                    break
                except (KeyError):
                    if not os.path.exists("error.log"):
                        f = open("error.log", "w")
                        f.write('')
                        f.close()
                    f = open("error.log", 'w')
                    f.write(str(result[j]))
                    f.close()

        print("Danbooru: Finished searching")

    def run(self):
        if self.verbose:
            print("Starting Danbooru Thread")
        self.download()
