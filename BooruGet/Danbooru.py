from Booru import Booru
import Filter
import httplib2
import math
import time
from threading import thread

class DanbooruDownloader(Booru, Thread):
    """
    """
    #TODO write docstring

    number_per_page = 100
    urlbase = "http://danbooru.donmai.us/"


    def __init__(self, args, download_manager):

        Booru.__init__(self, args, download_manager)
        Thread.__init__self(self)

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
        if self.args.verbose:
            print("Danbooru: Reqesting page")
        try:
            connection = httplib2.Http(".cache")
            header = "posts.json?login=" + self.username + "&api_key=" + \
                self.password + "&limit=" + str(numPerPage) + "&"
            # make request
            if self.args.verbose:
                print("Making request: " + self.urlbase + header + "tags=" + tags + \
                    "&page=" + str(pageNum))
            res, content = connection.request(
                url + header + "tags=" + tags + "&page=" + str(pageNum))
            if len(content) >= 0 and res.status == 200:
                if arguments.verbose:
                    print("Response recieved")
                return json.loads(content)
            else:
                return None
        except (httplib2.ServerNotFoundError):
            print("Could not contact server at danbooru.donmai.us")
            print("Retrying in 30 seconds")
            time.sleep(30)
            self.getResultsJSON()
        return None

    def download(self):

        for i in range(1, numPages + 1):
            time.sleep(0.2)

            if self.args.verbose:
                print("Danbooru: current page: " + str(i) + " of ~1000 (" + \
                    str(i * numPerPage) + ")")

            result = self.getResultsJSON()

            # Handle case where there is no result
            if result is None or len(result) <= 0:
                if arguments.verbose:
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
                    if filterResult(result[j], tWidth, tHeight, error):
                        image = {}
                        image["md5"] = child.attrib["md5"]
                        image["image_height"] = int(child.attrib["height"])
                        image["image_width"] = int(child.attrib["width"])
                        image["rating"] = child.attrib["rating"]
                        image["tag_string"] = child.attrib["tags"]
                        image["file_ext"] = result[j]["file_ext"]
                        image["url"] =  self.urlbase + "/data/" + image["md5"] \
                            + "." + image["file_ext"]

                        self.download_manager.enqueue_file(image, self.tags)

                except (IndexError, TypeError):
                    print("Less than 100 images in this result ("\
                        + str(len(result)) + ")")
                    i = numPages + 2
                    j = numPerPage
                    break
                except (KeyError):
                    if not os.path.exists("error.log"):
                        f = open("error.log", "w")
                        f.write('')
                        f.close()
                    f = file("error.log", 'w')
                    f.write(str(result))
                    f.close()

        print("Danbooru: Finished searching")

    def run(self):
        if self.verbose:
            print("Starting Gelbooru Thread")
        self.download()
