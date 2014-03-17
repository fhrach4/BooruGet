import sys
import os


class Filter:

    NSFW_BLACKLIST = []
    GLOBAL_BLACKLIST = []
    MD5_NSFW_BLACKLIST = []
    MD5_GLOBAL_BLACKLIST = []
    MD5_NSFW_WHITELISTLIST = []
    MD5_GLOBAL_WHITELISTLIST = []
    NSFW_MD5 = []

    FILES = [
        os.path.join(".config", "nsfw_blacklist"), os.path.join(
            ".config", "global_blacklist"),
        os.path.join(".config", "md5_nsfw_blacklist"), os.path.join(
            ".config", "md5_global_blacklist"),
        os.path.join(".config", "md5_nsfw_whitelist"), os.path.join(
            ".config", "md5_global_whitelist"),
        os.path.join(".config", "_nsfw_md5")]

    structs = [
        NSFW_BLACKLIST, GLOBAL_BLACKLIST, MD5_NSFW_BLACKLIST,
        MD5_GLOBAL_BLACKLIST, MD5_NSFW_WHITELISTLIST, MD5_GLOBAL_WHITELISTLIST,
        NSFW_MD5]

    def __init__(self):
        pass

    def loadBlackAndWhiteLists():
        global arguments

        # list of al the blacklist/whitelist files. Each one corrisponds with
        # it's data structure equivalent

        for i in range(len(self.FILES)):

            # if the file does not exist, create it
            if not os.path.exists(self.FILES[i]):
                f = open(self.FILES[i], "w")
                f.write('')
                f.close()

            # then try and load the contents of the file
            try:
                f = open(self.FILES[i])
                for line in f:
                    structs[i].append(str(line.strip()))
                f.close()
            except Exception, e:
                print "Error opening " + FILES[i]
                print e
                sys.exit()

    def filterResult(self, result):
        md5 = result['md5']
        fExtension = result['file_ext']
        height = result['image_height']
        width = result['image_width']
        rating = result['rating']
        tString = result['tag_string']
        tagString = tString.split(" ")

        minWidth = self.targetWidth - self.targetWidth * self.error
        minHeight = self.targetHeight - self.targetHeight * self.error

        # maxHeight may not be used...
        maxHeight = self.targetHeight + self.targetHeight * self.error

        fail = False
        mark_nsfw = False
        md5_Fail = False
        md5_Global_Fail = False
        md5_Pass = False
        blacklistedTag = []
        globalBlacklistedTag = []

        # calculate the ratio
        ratio = width / float(height)
        tratio = self.targetWidth / float(self.targetHeight)

        maxRatio = tratio + tratio * self.error
        minRatio = tratio - tratio * self.error

        # check if the width and height are acceptable
        # if width <= maxWidth and width >= minWidth and height <= maxHeight and
        # height >= minHeight:
        if (ratio >= minRatio and ratio <= maxRatio) or self.anySize:
            if (width <= minWidth and height <= minHeight):
                fail = True
                # TODO maybe add verbose message for failed size check
            # if the anysize argument is used, auto-pass this check
            if self.anySize:
                fail = False

            # if nfsw is not allowed, check the tag blacklist
            for tag in NSFW_BLACKLIST:
                if tag in tagString:
                    if not arguments.nsfw:
                        fail = True
                    mark_nsfw = True
                    blacklistedTag.append(tag)

            # check if md5 is blacklisted
            if md5 in MD5_NSFW_BLACKLIST and not arguments.nsfw:
                fail = True
                md5_Fail = True

            # check if md5 is blacklisted for nsfw
            if md5 in MD5_GLOBAL_BLACKLIST:
                fail = True
                md5_Global_Fail = True

            # if nsfw is allowed or not allowed check the global blacklist
            for tag in GLOBAL_BLACKLIST:
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
                    print "\self.targetWidth: " + str(width) + " (minimim: " + \
                        str(minWidth) + ")"
                    print "\self.targetHeight: " + str(height) + " (minumum: " + \
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
                    print "\self.targetWidth: " + str(width) + " (minimim: " + \
                        str(minWidth) + ")"
                    print "\self.targetHeight: " + str(height) + " (minumum: " + \
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
                print "\self.targetWidth: " + str(width) + " (minimim: " + str(minWidth) + \
                    ")"
                print "\self.targetHeight: " + str(height) + " (minumum: " + \
                    str(maxHeight) + ")"
                print "\tRatio: " + str(ratio) + " (target: " + str(tratio) + \
                    " minimum: " + str(minRatio) + \
                    " maximum: " + str(maxRatio) + ")"
                print "\tnsfw allowed: " + str(arguments.nsfw)
                print "\tTag String: " + str(tString)

        return False
