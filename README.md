#BooruGet
##About
This project downlads files from danbooru and gelbooru. It can run on all operating systems, but requires wget to be in your path.

This program is still very much in devlopment and is not very user friendly yet.

##Installation
Run BooruGet which will create all required files/folders.
Requires python2.7 with httplib2 and wget.

##Configuration
All configuration files are stored in .config

###BooruGet.config
Currently there are only two settings.
```
username  
apikey 
```
username is your username
apikey is your apikey for danbooru. Gelbooryu does not require an apikey

###Black and White List Configuration
All files under this category should have each entry on it's own line
For example:
```
something
someOtherThing
someDifferentThing
```
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
...It can be run from the terminal in OSX and Linux by calling ./BooruGet searchName
...In windows it can be run from cmd or PowerShell using python BooruGet searchName

'./BooruGet "some search"' to run
'./BooruGet --help' to get help

##Planned Features
...GUI client for Windows and GTK
...Better organization
...Better README
