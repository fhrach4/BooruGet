"""
A module for filtering out various images downloaded from a Booru based offf of
tagging, rating, and size

When declaring a new instance, the following args from program launch must
be provided in an argument:
    target_width:       The width of the desired picture size
    target_height:      The height of the desired picture size
    error:              How much, as a percentage, an image can deviate from
                        the target_width and target_height
"""
import sys
import os


class Filter(object):
    """
    Runs a filter based off of several criteria
    """


    files = [
        os.path.join(".config", "nsfw_blacklist"), os.path.join(
            ".config", "global_blacklist"),
        os.path.join(".config", "md5_nsfw_blacklist"), os.path.join(
            ".config", "md5_global_blacklist"),
        os.path.join(".config", "md5_nsfw_whitelist"), os.path.join(
            ".config", "md5_global_whitelist"),
        os.path.join(".config", "_nsfw_md5")]


    def __init__(self, args):
        """
        Arguments -> a dict of the args passed to the program
        """
        # TODO more detaild documentation
        self.nsfw_blacklist = []
        self.global_blacklist = []
        self.md5_nsfw_blacklist = []
        self.md5_global_blacklist = []
        self.md5_nsfw_whitelist = []
        self.md5_global_whitelist = []
        self.nsfw_md5 = []

        self.structs = [
            self.nsfw_blacklist, self.global_blacklist, self.md5_nsfw_blacklist,
            self.md5_global_blacklist, self.md5_nsfw_whitelist,
            self.md5_global_whitelist, self.nsfw_md5]

        self.args = args

        self.load_black_and_white_lists()

    def load_black_and_white_lists(self):
        """
        Loads the various black and white lists located in .config
        """

        # list of all the blacklist/whitelist files. Each one corrisponds with
        # it's data structure equivalent
        for i in range(len(self.files)):
            # if the file does not exist, create it
            if not os.path.exists(self.files[i]):
                f = open(self.files[i], "w")
                f.write('')
                f.close()

            # then try and load the contents of the file
            try:
                f = open(self.files[i])
                for line in f:
                    self.structs[i].append(str(line.strip()))
                f.close()
            except(Exception, e):
                #TODO add more specific error handling
                print("Error opening " + self.files[i])
                print(e)
                sys.exit()

    def filter_result(self, result):
        """
        The method that actually does the filtering

        result -> a result from a booru api
        """

        md5 = result['md5']
        file_extension = result['file_ext']
        height = result['image_height']
        width = result['image_width']
        rating = result['rating']
        #search_string = result['tag_string'].split(" ")

        min_width = self.args.target_width - \
           self.args.target_width * self.args.error
        min_height = self.args.target_height - \
            self.args.target_height * self.args.error

        # maxHeight may not be used...
        max_height = self.args.target_height + \
            self.args.target_height * self.args.error

        fail = False
        mark_nsfw = False
        md5_fail = False
        md5_global_fail = False
        md5_pass = False
        blacklisted_tag = []
        global_blacklisted_tag = []

        # calculate the ratio
        ratio = width / float(height)
        tratio = self.args.target_width / float(self.args.target_height)

        max_ratio = tratio + tratio * self.args.error
        min_ratio = tratio - tratio * self.args.error

        # check if the width and height are acceptable, or automatically pass
        # if the anysize argument is passed
        if (ratio >= min_ratio and ratio <= max_ratio) or \
            self.args.any_size:

            # if the picture is larger than the target size, or any size is
            # allowed, the image passes
            fail = True
            if width >= min_width and height >= min_height or \
                self.args.any_size:
                fail = False

            # if nfsw is not allowed, check the tag blacklist
            for tag in self.nsfw_blacklist:
                if tag in result['tag_string']:
                    if not self.args.nsfw:
                        fail = True
                    mark_nsfw = True
                    blacklisted_tag.append(tag)

            # check if md5 is blacklisted
            if md5 in self.md5_nsfw_blacklist and not self.args.nsfw:
                fail = True
                md5_fail = True

            # check if md5 is blacklisted for nsfw
            if md5 in self.md5_global_blacklist:
                fail = True
                md5_global_fail = True

            # if nsfw is allowed or not allowed check the global blacklist
            for tag in self.global_blacklist:
                if tag in self.args.search_string:
                    fail = True
                    global_blacklisted_tag.append(tag)

            # check if md5 is in the md5 whitelist
            if md5 in self.md5_nsfw_whitelist:
                md5_pass = True

            # if nsfw and rating is safe or if md5 was in the whitelist
            #return true
            if(not(rating != "s" and not self.args.nsfw) and not fail) \
                or md5_pass:
                if self.args.verbose:
                    values = [True, rating, md5, md5_fail, md5_global_fail,
                              md5_pass, file_extension, blacklisted_tag,
                              global_blacklisted_tag, width, min_width, height,
                              max_height, ratio, min_ratio, max_ratio]
                    self.print_debug_message(values)

                # if the rating is not s and it is not already marked as nsfw,
                # mark as nsfw
                if (not rating == "s") and (not str(md5) in self.nsfw_md5):
                    if self.args.verbose:
                        print("\t\tmarking as nsfw")
                    self.nsfw_md5.append(str(md5))
                    self.update_md5_black_and_white_lists()

                    if self.args.verbose:
                        print("\t\tdone")

                # otherwise go through each tag. If the tag is recognized as nsfw
                elif mark_nsfw and (not str(md5) in self.nsfw_md5):
                    if self.args.verbose:
                        print("\t\tmarking as nsfw")
                    self.nsfw_md5.append(str(md5))
                    self.update_md5_black_and_white_lists()

                    if self.args.verbose:
                        print("\t\tdone")
                return True
            else:
                if self.args.verbose:
                    values = [False, rating, md5, md5_fail, md5_global_fail,
                              md5_pass, file_extension, blacklisted_tag,
                              global_blacklisted_tag, width, min_width, height,
                              max_height, ratio, min_ratio, max_ratio]
                    self.print_debug_message(values)
        else:
            if self.args.verbose:
                values = [False, rating, md5, md5_fail, md5_global_fail,
                          md5_pass, file_extension, blacklisted_tag,
                          global_blacklisted_tag, width, min_width, height,
                          max_height, ratio, min_ratio, max_ratio]
                self.print_debug_message(values)

        return False

    def print_debug_message(self, values):
        """
        Prints a debug message to stdout

        values -> list  a list which contains the following values
                        in the following order

                        accepted, raiting, md5, md5_fail, md5_global_fail,
                        md5_pass, file_extension, blacklisted_tag,
                        global_blacklisted_tag, width, min_width, height,
                        max_height, ratio, min_ratio, max_ratio
        """

        accepted = values[0]
        rating = values[1]
        md5 = values[2]
        md5_fail = values[3]
        md5_global_fail = values[4]
        md5_pass = values[5]
        file_extension = values[6]
        blacklisted_tag = values[7]
        global_blacklisted_tag = values[8]
        width = values[9]
        min_width = values[10]
        height = values[11]
        max_height = values[12]
        ratio = values[13]
        min_ratio = values[14]
        max_ratio = values[15]

        if accepted:
            print("Accepted:")
        else:
            print("Skipped")
        print("\trating: " + rating)
        print("\tmd5: " + md5)
        print("\tincluded in md5 nsfw blacklist: " + str(md5_fail))
        print("\tincluded in md5 global blacklist: " + \
            str(md5_global_fail))
        print("\tincluded in md5 whitelist: " + str(md5_pass))
        print("\tfile extension: " + file_extension)
        print("\tContained blacklisted tag: " + str(blacklisted_tag))
        print("\tContained global blacklisted tag: " + \
            str(global_blacklisted_tag))
        print("\self.target_width: " + str(width) + " (minimim: " + \
            str(min_width) + ")")
        print("\self.target_height: " + str(height) + \
            " (minumum: " + str(max_height) + ")")
        print("\tRatio: " + str(ratio) + "(minimum: " + str(min_ratio)\
            + " maximum: " + str(max_ratio) + ")")
        print("\tnsfw allowed: " + str(self.args.nsfw))
        try:
            print("\tTag String: " + str(self.args.search_string))
        except UnicodeEncodeError:
            # TODO handle unicode Error
            pass

    def update_md5_black_and_white_lists(self):
        """
        add new information to the black and white list files
        """

        for i in range(len(self.files)):

            # try and load the contents of the file
            try:
                f = open(self.files[i])
                for line in f:
                    self.structs[i].append(str(line))
                f.close()
            except(Exception):
                print("Error opening " + self.files[i])
                sys.exit()
