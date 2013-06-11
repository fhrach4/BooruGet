"""
Frank Hrach
wall.py
Last edit: Thu Jun  6 18:01:49 EDT 2013
"""

import argparse
import httplib2, urllib, hashlib
import json
import xml.etree.ElementTree as ET
import threading, os, random, platform
import time

from subprocess import call

threads= []
numthreads = 0

platform = platform.system()

arguments = []

NSFW_BLACKLIST = ["ass", "assymmetrical_docking", "cameltoe", "cleavage",
    "cum", "cum_on_face", "cum_on_breasts" , "erect_nipples", "futanari",
    "garter_belt", "giantess", "lingere", "nipples", "panties", "penis",
    "pussy", "sex", "symmetrical_docking", "undressing", "underwear", "yuri",
    "wardrobe_malfunction"]

GLOBAL_BLACKLIST = ["gore"]

MD5_NSFW_BLACKLIST = ["780a802e55b88d0f6ce08cf9a14a42d3",
    "3becc66befdbfe9585b4d8d729c56813", "4436aed96caea9df8a58464b5b1a5e04",
    "c7a8dc55f55e5e6c1174f3999292c2a5", "624540f4f15c75bd10cc293fb33bb896g",
    "87cbe547d4f3d4c42054bc44bbad9f4e"]

MD5_GLOBAL_BLACKLIST = []

MD5_NSFW_WHITELISTLIST = [""]

MD5_GLOBAL_WHITELISTLIST = [""]

def getResults( pageNum, numPerPage, tags, login, key ):

    # create connection
    connection = httplib2.Http(".cache")
    header = "?login=" + login + "&api_key=" + key + "&limit=" + str(numPerPage) + "&"

    # make request
    url = "http://danbooru.donmai.us/posts.json"
    res, content = connection.request( url + header + "tags=" + tags +\
    "&page=" + str(pageNum))
    if len(content) >= 0:
        return json.loads(content)
    else:
        return None

def getResultsGel( tags ):
    connection = httplib2.Http(".cache")
    header = "index.php?page=dapi&s=post&q=index"

    url = "http://gelbooru.com/"
    res, content = connection.request( url + header + "&tags=" + tags )
    if len( content ) >= 0:
        return ET.parse( content )
    else:
        return None

def changewallpaper(tags):
    global arguments
    global platform

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
                print "\t" + md5

            # if in the md5 nsfw blacklist remove the file
            if md5 in MD5_NSFW_BLACKLIST and not arguments.nsfw:
                if arguments.verbose:
                    print "\tAttempting to remove file..."
                os.remove(fileName)
                change = False
                if arguments.verbose:
                    print "\tRemoved file because it was in md5 nsfw blacklist"


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

def download(searchString, twidth, theight, error, login, key ):
    global numthreads
    global threads
    global arguments

    urlbase = "http://danbooru.donmai.us"
    numPerPage = 100
    numPages = 1000

    minWidth = twidth - twidth * error
    maxWidth = twidth + twidth * error
    minHeight = theight - theight * error
    maxHeight = theight + theight * error

    for i in range(1,numPages + 1):
        if arguments.verbose:
            print  "current page: " + str(i) + " (" + str(i * numPerPage) + ")"
        result = getResults(i, numPerPage, searchString, login, key)
        if len(result) == 0:
            break
        for j in range( numPerPage ):
            try:
                md5 = result[j]['md5']
                fExtension = result[j]['file_ext']
                height = result[j]['image_height']
                width = result[j]['image_width']
                rating = result[j]['rating']
                tString = result[j]['tag_string']
                tagString = tString.split(" ")

                # if the width is acceptable AND the hight is acceptable,
                #start a download thread
                if width <= maxWidth and width >= minWidth and height <= maxHeight and height >= minHeight:

                    # create the thread and move on
                    fail = False
                    md5_Fail = False
                    md5_Global_Fail = False
                    md5_Pass = False
                    blacklisedTag = "None"
                    globalBlacklistedTag = "None"

                    # if nfsw is not allowed, check the tag blacklist
                    if arguments.nsfw == False:
                        for tag in NSFW_BLACKLIST:
                            if tag in tagString:
                                fail = True
                                blacklisedTag = tag

                    # check if md5 is blacklisted
                    if md5 in MD5_NSFW_BLACKLIST and arguments.nsfw == False:
                        fail = True
                        md5_Fail = True

                    # check if md5 is blacklisted for nsfw
                    if md5 in MD5_GLOBAL_BLACKLIST and arguments.nsfw == True:
                        fail = True
                        md5_Global_Fail = True

                    # if nsfw is allowed  or not allowed check the global blacklist
                    for tag in GLOBAL_BLACKLIST:
                        if tag in tagString:
                            fail = True
                            blacklisedTag = tag

                    # check if md5 is in the md5 whitelist
                    if md5 in MD5_NSFW_WHITELISTLIST:
                        md5_Pass = True

                    if (not(rating != "s" and arguments.nsfw == False) and not fail) or md5_Pass:
                        if arguments.verbose:
                            print "Accepted:"
                            print "\trating: " + rating
                            print "\tmd5: " + md5
                            print "\tincluded in md5 nsfw blacklist: " + str(md5_Fail)
                            print "\tincluded in md5 global blacklist: " + str(md5_Global_Fail)
                            print "\tincluded in md5 whitelist: " + str(md5_Pass)
                            print "\tfile extension: " + fExtension
                            print "\tContained blacklisted tag: " + blacklisedTag
                            print "\tContained global blacklisted tag: " + globalBlacklistedTag
                            print "\twidth: " + str(width)
                            print "\theight: " + str(height)
                            print "\tnsfw: " + str(arguments.nsfw)
                        while numthreads >= 4:
                            print numthreads
                            time.sleep(1000)
                        t = threading.Thread(target=downloadImage, args = [urlbase, searchString, md5, fExtension])
                        #threads.append(t)
                        numthreads += 1
                        t.start()
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
                            print "\tContained blacklisted tag: " + blacklisedTag
                            print "\tContained global blacklisted tag: " + globalBlacklistedTag
                            print "\twidth: " + str(width)
                            print "\theight: " + str(height)
                            print "\tnsfw: " + str(arguments.nsfw)
            except (IndexError, KeyError):
                print "Less than 100 images in this result ("\
                + str(len(result)) + ")"
                i = numPages + 1
                j = numPerPage
                break

    print "Finished searching"

def downloadImage( urlBase, location , md5, fExtension ):
    """
    Uses wget to download an image with the specified md5 from the specified
    url base to the specified location
    """
    global numthreads
    call(["wget", "-q", "-N", "-P" + location, urlBase + "/data/" + md5 + "." + fExtension ])
    numthreads -= 1

def handleArguments():
    global arguments
    parser = argparse.ArgumentParser()
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
        download( search, width, height, error, username, apikey )

    #print getResultsGel("huge_breasts")

main()
