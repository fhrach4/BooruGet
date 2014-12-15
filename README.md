#BooruGet
##About
This project downlads files from danbooru and gelbooru. It can run on all operating systems, but requires httplib2 to be installed. This is generally not installed on a default python3 install

* This program is still very much in devlopment and is not very user friendly yet.

##Installation
BooruGet  will create all required files/folders on first run.

###Dependencies
* python3
* httplib2

##Configuration
All configuration files are stored in .config

###BooruGet.config
Currently there are three settings
`username`, `apikey`, and `out_dir`

* Username is your username
* Apikey is your apikey for Danbooru. If you do not have a danbooru account you can leave this blank and use `--nodan` to exclude danbooru from searches
 * Gelbooru does not require an api key
* out_dir is the directory to output files to. Each search will create a directory with the name of the search as a folder. E.G. searching for test will put results in src/test

###Black and White List Configuration
All files under this category should have each entry on it's own line.
For example:

something<br />
someOtherThing<br />
someDifferentThing

####nsfw_blacklist
Enter tags that should not be downloaded unless nsfw images are allowed

####global_blacklist
Enter tags that never should be downloaded even if nsfw images are allowed

####md5_global_blacklist
Enter the md5 hash of a file that should never be downloaded

####md5_nsfw_blacklist
Enter the md5 hash of a file that should only be downloaded if nsfw images are allowed

####md5_nsfw_whitelist
Enter the md5 hash of a file that should be downloaded if nsfw images are not allowed

###md5_global_whitelist
Enter the md5 hash of a file that should always be downloaded

###_nsfw_md5
A program-created list of files that would register as nsfw

##Running
Currently this program does not have a gui
It can be run from the terminal in OSX and Linux by calling `./BooruGet searchName`
In Windows it can be run from cmd or PowerShell using `python BooruGet searchName`

###Examples
* ```./BooruGet "some search"``` to run
* ```./BooruGet --help``` to get help
* ```./BooruGet -w 1920 -t 1080 "some_tag"``` to get all images that fit 1920x1080 and match some_tag

###Error
Error is how off the aspect ratio can be. This allows more pictures that are 'close enougth' to be downlodaed.
Setting the error lets a picture be greater than or less than the target dimensions by the amount.
For example: an error of .15 for 1920x1080 would allows pictures in the range from 1632x918 to 2208x1242. The default error is .05 or 5%

###Anysize
By default, the program will ignore images that are smaller than the target size even if they are the correct aspect ratio. Using Anysize ignores this and will download all matches no matter what the size. For example, if you specify 1920x1080 the aspect ratio is 16:9, if a picture were only 1600x900 it would normally be ignored, however, with -a, it would be downloaded.

##Planned Features
* GUI client for Windows and GTK
* Better organization
* Better README
