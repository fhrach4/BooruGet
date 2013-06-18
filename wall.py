"""
Frank Hrach
wall.py
Last edit: Thu Jun  6 18:01:49 EDT 2013
"""

import argparse
import httplib2, urllib, hashlib
import json
import xml.etree.ElementTree as ET
import threading, os, random, platform, sys
import time
import math

from subprocess import call

threads= []
numthreads = 0
writeLock = False

platform = platform.system()

arguments = [""]
NSFW_BLACKLIST = [""]
GLOBAL_BLACKLIST = [""]
MD5_NSFW_BLACKLIST = [""]
MD5_GLOBAL_BLACKLIST = [""]
MD5_NSFW_WHITELISTLIST = [""]
MD5_GLOBAL_WHITELISTLIST = [""]
NSFW_MD5 = [""]

def getResultsJSON(url, pageNum, numPerPage, tags, login, key ):

    # create connection
    connection = httplib2.Http(".cache")
    header = "posts.json?login=" + login + "&api_key=" + key + "&limit=" + str(numPerPage) + "&"

    # make request
    res, content = connection.request( url + header + "tags=" + tags +\
    "&page=" + str(pageNum))
    if len(content) >= 0:
        return json.loads(content)
    else:
        return None

def getResultsXML( url, pageNum, numPerPage, tags ):

    connection = httplib2.Http(".cache")
    res, content = connection.request( url + "&tags=" + tags
        + "&pid=" + str(pageNum) + "&limit=" +str( numPerPage))
    if len( content ) >= 0:
        return ET.fromstring( content )
    else:
        return None

def changewallpaper(tags):
    global arguments
    global platform

    updateMD5BlackAndWhiteLists()

    change = True
    dirname = "/home/frank4/.test/" + tags
    if arguments.verbose:
        print "Starting wallpaper switch..."
    try:
        if arguments.verbose:
            print "\tGetting directory listng at: " + dirname

        files = os.listdir( dirname )

        if arguments.verbose:
            print "\t" + str(len(files)) + " in directory"

        # as long as there is at least one file in the directory
        if len(files) > 0:

            # get a random index, and create the path and md5
            randomIndex = random.randint(0, len(files) -1)
            fileName =  dirname + "/" + files[randomIndex]
            md5 = files[randomIndex].split(".")[0]

            if arguments.verbose:
                print "\tNext filename: " + fileName
                print "\tmd5: " + md5

            # if in the md5 nsfw blacklist remove the file
            if md5 in MD5_GLOBAL_BLACKLIST or ( md5 in MD5_NSFW_WHITELISTLIST and arguments.nsfw ):
                if arguments.verbose:
                    print "\tAttempting to remove file..."
                os.remove(fileName)
                change = False
                if arguments.verbose:
                    print "\tRemoved file because it was blacklisted"

            # if nsfw is off and image is marked as nsfw, try again
            if (not arguments.nsfw) and md5 in NSFW_MD5:
                if arguments.verbose:
                    print "\tNSFW is on, trying again"
                change = False

            # if the file was not removed from the directory change it
            # TODO handle different os and window managers
            if change and platform == "Linux":
                call(["xfconf-query", "-c","xfce4-desktop", "-p", \
                "/backdrop/screen0/monitor0/image-path", "-s", fileName])
                if arguments.verbose:
                    print "\tcommand run"
            if arguments.verbose:
                print "Wallpaper switch ... Done"
    except:
        # Do nothing, this is not a problem
        pass

    # if the wallpaper was not changed, try again, othwerwise wait 30 seconds
    if not change:
        threading.Thread(target=changewallpaper, args=[tags]).start()
    else:
        threading.Timer(30, changewallpaper, args=[tags]).start()

def downloadGel(searchString, tWidth, tHeight, error ):
    global arguments
    global numthreads

    url  = "http://gelbooru.com/index.php?page=dapi&s=post&q=index"

    numPerPage = 100
    numPages = 1000

    root = getResultsXML(url, 1, numPerPage, searchString)
    numPages = int(math.ceil( int(root.attrib["count"]) / float(len(root) )))

    for i in range(1, numPages + 1):
        #TODO add try catch around this and other error handling
        #root = getResultsXML( url, searchString ).getRoot()
        root = getResultsXML(url, i, numPerPage, searchString)

        if arguments.verbose:
            print  "Gelbooru: current page: " + str(i) + " (" + str(i * numPerPage) + ") out of " + str(numPages) + " pages("+ root.attrib["count"] + ")"

        try:
            for child in root:
                #TODO check to make sure result has data
                image = {}
                image["md5"] = child.attrib["md5"]
                image["image_height"] = int(child.attrib["height"])
                image["image_width"] = int(child.attrib["width"])
                image["rating"] = child.attrib["rating"]
                image["tag_string"] = child.attrib["tags"]
                image["file_ext"] = child.attrib["file_url"].split(".")[3]

                if filterResult( image, tWidth, tHeight, error ):
                    while numthreads >= 4:
                        time.sleep(1000)
                    t = threading.Thread(target=downloadImage, args = [child.attrib["file_url"], searchString])
                    numthreads += 1
                    t.start()
        except(IndexError):
            print "End of results"
    print "Gelbooru: Finished searching"


def downloadDan(searchString, tWidth, tHeight, error, login, key ):
    global numthreads
    global threads
    global arguments

    urlbase = "http://danbooru.donmai.us/"
    numPerPage = 100
    numPages = 1000

    for i in range(1,numPages + 1):
        if arguments.verbose:
            print  "Danbooru: current page: " + str(i) + " of ~1000 (" + str(i * numPerPage) + ")"
        result = getResultsJSON(urlbase, i, numPerPage, searchString, login, key)
        if len(result) == 0:
            break
        for j in range( numPerPage ):
            try:
                if filterResult( result[j], tWidth, tHeight, error ):
                    while numthreads >= 4:
                        time.sleep(1000)
                    md5 = result[j]["md5"]
                    fExtension = result[j]["file_ext"]
                    url = urlbase + "/data/" + md5 + "." + fExtension
                    t = threading.Thread(target=downloadImage, args = [url, searchString])
                    #threads.append(t)
                    numthreads += 1
                    t.start()
            except (IndexError, KeyError, TypeError):
                print "Less than 100 images in this result ("\
                + str(len(result)) + ")"
                i = numPages + 1
                j = numPerPage
                break

    print "Danbooru: Finished searching"

def filterResult( result, tWidth, tHeight, error ):
    """
    result  ->  A dictionary containing the following keys: md5, file_ext,
                image_height, image_width, rating, tag_string
                md5:        the md5 hash of the image
                fExtension: the file extension of the image
                height:     the height in pixles of the image
                width:      the width in pixels of the image
                rating:     the rating of the image (see danbooru for more)
                tString:    a string containing all of the tags

    returns ->  Boolean: True if the image should be downoaded otherwise false
    """
    global arguments
    global writeLock

    # extract all relevant information from the dictionary
    md5 = result['md5']
    fExtension = result['file_ext']
    height = result['image_height']
    width = result['image_width']
    rating = result['rating']
    tString = result['tag_string']
    tagString = tString.split(" ")

    minWidth = tWidth - tWidth * error
    maxWidth = tWidth + tWidth * error
    minHeight = tHeight - tHeight * error
    maxHeight = tHeight + tHeight * error

    fail = False
    nsfw = False
    md5_Fail = False
    md5_Global_Fail = False
    md5_Pass = False
    blacklistedTag = ""
    globalBlacklistedTag = ""

    # calculate the ratio
    ratio = width / float(height)
    tratio = tWidth/ float(tHeight)

    maxRatio = tratio + tratio * error
    minRatio = tratio - tratio * error

    # check if the width and height are acceptable
    #if width <= maxWidth and width >= minWidth and height <= maxHeight and height >= minHeight:
    if ratio >= minRatio and ratio <= maxRatio:
        if (width <= minWidth and  height <= minHeight) or arguments.anysize:
            fail = True
            # TODO maybe add verbose message for failed size check

        # if nfsw is not allowed, check the tag blacklist
        for tag in NSFW_BLACKLIST:
            if tag in tagString:
                if not arguments.nsfw:
                    fail = True
                nsfw = True
                blacklistedTag = blacklistedTag + tag +", "

        # check if md5 is blacklisted
        if md5 in MD5_NSFW_BLACKLIST and arguments.nsfw == False:
            fail = True
            md5_Fail = True

        # check if md5 is blacklisted for nsfw
        if md5 in MD5_GLOBAL_BLACKLIST and arguments.nsfw == True:
            fail = True
            md5_Global_Fail = True

        # if nsfw is allowed or not allowed check the global blacklist
        for tag in GLOBAL_BLACKLIST:
            if tag in tagString:
                fail = True
                globalBlacklistedTag = globalBlacklistedTag + tag + ", "

        # check if md5 is in the md5 whitelist
        if md5 in MD5_NSFW_WHITELISTLIST:
            md5_Pass = True

        # if nsfw and rating is safe or if md5 was in the whitelist return true
        if (not(rating != "s" and arguments.nsfw == False) and not fail) or md5_Pass:
            if arguments.verbose:
                print "Accepted:"
                print "\trating: " + rating
                print "\tmd5: " + md5
                print "\tincluded in md5 nsfw blacklist: " + str(md5_Fail)
                print "\tincluded in md5 global blacklist: " + str(md5_Global_Fail)
                print "\tincluded in md5 whitelist: " + str(md5_Pass)
                print "\tfile extension: " + fExtension
                print "\tContained blacklisted tag: " + blacklistedTag
                print "\tContained global blacklisted tag: " + globalBlacklistedTag
                print "\tWidth: " + str(width)
                print "\tHeight: " + str(height)
                print "\tRatio: " + str(ratio)
                print "\tnsfw allowed: " + str(arguments.nsfw)
                print "\tTag String: " + str(tString)

            # if the rating is not s and it is not already marked as nsfw,
            # mark as nsfw
            if ( not rating == "s") and (not str(md5) in NSFW_MD5):
                if arguments.verbose:
                    print "\t\tmarking as nsfw"
                NSFW_MD5.append(str(md5))
                while writeLock:
                    time.sleep(500)
                writeLock = True
                f = open("._nsfw_md5", "a+")
                f.write( md5 + '\n' )
                f.close()
                writeLock = False
                if arguments.verbose:
                    print "\t\tdone"
            # otherwise go through each tag. If the tag is recognized as nsfw
            # mark the image as nsfw
            elif nsfw and (not str(md5) in NSFW_MD5):
                if arguments.verbose:
                    print "\t\tmarking as nsfw"
                NSFW_MD5.append(str(md5))
                while writeLock:
                    time.sleep(500)
                writeLock = True
                f = open("._nsfw_md5", "a+")
                f.write( md5 + '\n' )
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
                print "\tincluded in md5 global blacklist: " + str(md5_Global_Fail)
                print "\tincluded in md5 whitelist: " + str(md5_Pass)
                print "\tincluded in md5 whitelist: " + str(md5_Pass)
                print "\tfile extension: " + fExtension
                print "\tContained blacklisted tag: " + blacklistedTag
                print "\tContained global blacklisted tag: " + globalBlacklistedTag
                print "\tWidth: " + str(width)
                print "\tHeight: " + str(height)
                print "\tRatio: " + str(ratio)
                print "\tnsfw allowed: " + str(arguments.nsfw)
                print "\tTag String: " + str(tString)
                return False
    else:
        if arguments.verbose:
            #print "failed size test"
            #print "Skipped:"
            #print "\trating: " + rating
            #print "\tmd5: " + md5
            #print "\tincluded in md5 blacklist: " + str(md5_Fail)
            #print "\tincluded in md5 global blacklist: " + str(md5_Global_Fail)
            #print "\tincluded in md5 whitelist: " + str(md5_Pass)
            #print "\tincluded in md5 whitelist: " + str(md5_Pass)
            #print "\tfile extension: " + fExtension
            #print "\tContained blacklisted tag: " + blacklistedTag
            #print "\tContained global blacklisted tag: " + globalBlacklistedTag
            #print "\tWidth: " + str(width)
            #print "\tHeight: " + str(height)
            #print "\tnsfw: " + str(arguments.nsfw)
            pass

    return False

def downloadImage( url, location ):
    global numthreads
    call(["wget","-q", "-N", "-P" + location, url ])
    numthreads -= 1

def updateMD5BlackAndWhiteLists():
    # list of al the blacklist/whitelist files. Each one corrisponds with
    # it's data structure equivalent
    files = [ ".md5_nsfw_blacklist", ".md5_global_blacklist", ".md5_nsfw_whitelist",
        ".md5_global_whitelist" ]
    structs = [ MD5_NSFW_BLACKLIST, MD5_GLOBAL_BLACKLIST, MD5_NSFW_WHITELISTLIST,
        MD5_GLOBAL_WHITELISTLIST ]

    for i in range( len(files) ):

        # try and load the contents of the file
        try:
            f = open( files[i])
            for line in f:
                structs[i].append( str(line) )
            f.close()
        except Exception, e:
            print "Error opening " + files[i]
            print e
            sys.exit()

def loadBlackAndWhiteLists():
    global arguments
    global NSFW_BLACKLIST
    global GLOBAL_BLACKLIST
    global MD5_NSFW_BLACKLIST
    global MD5_GLOBAL_BLACKLIST
    global MD5_NSFW_WHITELISTLIST
    global MD5_GLOBAL_WHITELISTLIST
    global NSFW_MD5

    # list of al the blacklist/whitelist files. Each one corrisponds with
    # it's data structure equivalent
    files = [ ".nsfw_blacklist", ".global_blacklist", ".md5_nsfw_blacklist",
        ".md5_global_blacklist", ".md5_nsfw_whitelist", ".md5_global_whitelist",
        "._nsfw_md5"]
    structs = [ NSFW_BLACKLIST, GLOBAL_BLACKLIST, MD5_NSFW_BLACKLIST,
        MD5_GLOBAL_BLACKLIST, MD5_NSFW_WHITELISTLIST, MD5_GLOBAL_WHITELISTLIST,
        NSFW_MD5]

    for i in range( len(files) ):

        # if the file does not exist, create it
        if not os.path.exists(files[i]):
            f = open(files[i], "w" )
            f.write('')
            f.close()

        # then try and load the contents of the file
        try:
            f = open( files[i])
            for line in f:
                structs[i].append( str(line.strip()) )
            f.close()
        except Exception, e:
            print "Error opening " + files[i]
            print e
            sys.exit()

def handleArguments():
    global arguments
    parser = argparse.ArgumentParser()
    parser.add_argument("-a", "--anysize", help = "Allow any sized image (default is to only allow images equal to or larger than the specified screen size", action="store_true" )
    parser.add_argument("-u", "--username", help = "The username you use to log into danbooru")
    parser.add_argument("-k", "--apikey", help = "Your api key (can be found on your user page")
    parser.add_argument("-w", "--width", help = "the width of your screen in pixels", type=int)
    parser.add_argument("-t", "--height", help = "the height of your screen in pixels", type=int)
    parser.add_argument("-e", "--error", help="the percentage error allowed for the image (default is 5%)", default=0.05, type=float)
    parser.add_argument("-v", "--verbose", help="prints debug output", action="store_true")
    parser.add_argument("--nsfw", help = "Allow nsfw results, default is disallow", action="store_true")
    parser.add_argument("-d", "--downloadonly", help = "Download only, do not start changing wallpaper", action="store_true")
    parser.add_argument("-l", "--localonly", help="Do not download, use local files only", action="store_true")
    parser.add_argument("search", help = "the string to search for formatted correctly")
    arguments = parser.parse_args()

def main():
    global arguments
    handleArguments()
    loadBlackAndWhiteLists()
    if arguments.verbose:
        print arguments
    search = arguments.search
    width = arguments.width
    height = arguments.height
    error = arguments.error
    username = arguments.username
    apikey = arguments.apikey
    if not arguments.downloadonly:
        threading.Thread(target=changewallpaper, args=[search]).start()
    if not arguments.localonly:
        print "Starting downloads"
        threading.Thread(target=downloadGel, args=[search, width, height, error] ).start()
        threading.Thread(target=downloadDan, args = [search, width, height, error, username, apikey]).start()

main()
