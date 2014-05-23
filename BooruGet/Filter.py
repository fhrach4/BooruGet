"""
A module for filtering out various images downloaded from a Booru based offf of
tagging, rating, and size

When declaring a new instance, the following arguments from program launch must
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


    def __init__(self, arguments):
        """
        Arguments -> a dict of the arguments passed to the program
        """
        # TODO more detaild documentation
        self.nsfw_blacklist = []
        self.global_blacklist = []
        self.md5_nsfw_blacklist = []
        self.md5_global_blacklist = []
        self.md5_nsfw_whitelistlist = []
        self.md5_global_whitelistlist = []
        self.nsfw_md5 = []

        self.structs = [
            self.nsfw_blacklist, self.global_blacklist, self.md5_nsfw_blacklist,
            self.md5_global_blacklist, self.md5_nsfw_whitelistlist,
            self.md5_global_whitelistlist, self.nsfw_md5]

        self.arguments = arguments;

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
            except Exception, e:
                #TODO add more specific error handling
                print "Error opening " + self.files[i]
                print e
                sys.exit()

    def filterResult(self, result):
        """
        The method that actually does the filtering

        result -> a result from a booru api
        """

        md5 = result['md5']
        file_extension = result['file_ext']
        height = result['image_height']
        width = result['image_width']
        rating = result['rating']
        tag_string = result['tag_string'].split(" ")

        min_width = self.arguments.target_width - \
           self.arguments.target_width * self.arguments.error
        min_height = self.arguments.target_height - \
            self.arguments.target_height * self.arguments.error

        # maxHeight may not be used...
        max_height = self.arguments.target_height + \
            self.arguments.target_height * self.arguments.error

        fail = False
        mark_nsfw = False
        md5_fail = False
        md5_global_fail = False
        md5_pass = False
        blacklisted_tag = []
        global_blacklisted_tag = []

        # calculate the ratio
        ratio = width / float(height)
        tratio = self.arguments.target_width / float(self.arguments.target_height)

        max_ratio = tratio + tratio * self.error
        min_ratio = tratio - tratio * self.error

        # check if the width and height are acceptable
        # if width <= maxWidth and width >= minWidth and height <= maxHeight and
        # height >= minHeight:
        if (ratio >= min_ratio and ratio <= max_ratio) or self.any_size:
            if (width <= min_width and height <= min_height):
                fail = True
                # TODO maybe add verbose message for failed size check
            # if the anysize argument is used, auto-pass this check
            if self.any_size:
                fail = False

            # if nfsw is not allowed, check the tag blacklist
            for tag in self.nsfw_blacklist:
                if tag in tag_String:
                    if not arguments.nsfw:
                        fail = True
                    mark_nsfw = True
                    blacklistedTag.append(tag)

            # check if md5 is blacklisted
            if md5 in MD5_nsfw_blacklist and not arguments.nsfw:
                fail = True
                md5_Fail = True

            # check if md5 is blacklisted for nsfw
            if md5 in MD5_global_blacklist:
                fail = True
                md5_Global_Fail = True

            # if nsfw is allowed or not allowed check the global blacklist
            for tag in global_blacklist:
                if tag in tagString:
                    fail = True
                    globalBlacklistedTag.append(tag)

            # check if md5 is in the md5 whitelist
            if md5 in MD5_NSFW_WHITELISTLIST:
                md5_Pass = True

            # if nsfw and rating is safe or if md5 was in the whitelist return true
            if(not(rating != "s" and not arguments.nsfw) and not fail) or md5_Pass:
                if arguments.verbose:
                    print "Accepted:"
                    print "\trating: " + rating
                    print "\tmd5: " + md5
                    print "\tincluded in md5 nsfw blacklist: " + str(md5_Fail)
                    print "\tincluded in md5 global blacklist: " + \
                        str(md5_Global_Fail)
                    print "\tincluded in md5 whitelist: " + str(md5_Pass)
                    print "\tfile extension: " + fExtension
                    print "\tContained blacklisted tag: " + str(blacklistedTag)
                    print "\tContained global blacklisted tag: " + \
                        str(globalBlacklistedTag)
                    print "\self.target_width: " + str(width) + " (minimim: " + \
                        str(minWidth) + ")"
                    print "\self.target_height: " + str(height) + " (minumum: " + \
                        str(maxHeight) + ")"
                    print "\tRatio: " + str(ratio) + "(minimum: " + str(minRatio)\
                        + " maximum: " + str(maxRatio) + ")"
                    print "\tnsfw allowed: " + str(arguments.nsfw)
                    try:
                        print "\tTag String: " + str(tString)
                    except(UnicodeEncodeError):
                        pass

                # if the rating is not s and it is not already marked as nsfw,
                # mark as nsfw
                if (not rating == "s") and (not str(md5) in NSFW_MD5):
                    if arguments.verbose:
                        print "\t\tmarking as nsfw"
                    NSFW_MD5.append(str(md5))
                    while writeLock:
                        time.sleep(500)
                    writeLock = True
                    f = open("._nsfw_md5", "a+")
                    f.write(md5 + '\n')
                    f.close()
                    writeLock = False
                    if arguments.verbose:
                        print "\t\tdone"
                # otherwise go through each tag. If the tag is recognized as nsfw
                # mark the image as nsfw
                elif mark_nsfw and (not str(md5) in NSFW_MD5):
                    if arguments.verbose:
                        print "\t\tmarking as nsfw"
                    NSFW_MD5.append(str(md5))
                    while writeLock:
                        time.sleep(500)
                    writeLock = True
                    f = open("._nsfw_md5", "a+")
                    f.write(md5 + '\n')
                    f.close()
                    writeLock = False
                    if arguments.verbose:
                        print "\t\tdone"
                return True
            else:
                if arguments.verbose:
                    print "Skipped:"
                    print "\trating: " + rating
                    print "\tmd5: " + md5
                    print "\tincluded in md5 blacklist: " + str(md5_Fail)
                    print "\tincluded in md5 global blacklist: " + \
                        str(md5_Global_Fail)
                    print "\tincluded in md5 whitelist: " + str(md5_Pass)
                    print "\tincluded in md5 whitelist: " + str(md5_Pass)
                    print "\tfile extension: " + fExtension
                    print "\tContained blacklisted tag: " + str(blacklistedTag)
                    print "\tContained global blacklisted tag: " + \
                        str(globalBlacklistedTag)
                    print "\self.target_width: " + str(width) + " (minimim: " + \
                        str(minWidth) + ")"
                    print "\self.target_height: " + str(height) + " (minumum: " + \
                        str(maxHeight) + ")"
                    print "\tRatio: " + str(ratio) + " (target: " + str(tratio) + \
                        " minimum: " + str(minRatio) + " maximum: " + \
                        str(maxRatio) + ")"
                    print "\tnsfw allowed: " + str(arguments.nsfw)
                    try:
                        print "\tTag String: " + str(tString)
                    except(UnicodeEncodeError):
                        pass
                    return False
        else:
            if arguments.verbose:
                print "failed size test"
                print "Skipped:"
                print "\trating: " + rating
                print "\tmd5: " + md5
                print "\tincluded in md5 blacklist: " + str(md5_Fail)
                print "\tincluded in md5 global blacklist: " + str(md5_Global_Fail)
                print "\tincluded in md5 whitelist: " + str(md5_Pass)
                print "\tincluded in md5 whitelist: " + str(md5_Pass)
                print "\tfile extension: " + fExtension
                print "\tContained blacklisted tag: " + str(blacklistedTag)
                print "\tContained global blacklisted tag: " + \
                    str(globalBlacklistedTag)
                print "\self.target_width: " + str(width) + " (minimim: " + str(minWidth) + \
                    ")"
                print "\self.target_height: " + str(height) + " (minumum: " + \
                    str(maxHeight) + ")"
                print "\tRatio: " + str(ratio) + " (target: " + str(tratio) + \
                    " minimum: " + str(minRatio) + \
                    " maximum: " + str(maxRatio) + ")"
                print "\tnsfw allowed: " + str(arguments.nsfw)
                print "\tTag String: " + str(tString)

        return False
