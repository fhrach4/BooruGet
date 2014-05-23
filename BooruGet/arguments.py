"""
Represents the arguments passed into the program
"""

class Arguments(object):
    """
    """
    #TODO write documentation
    def __init__(self, any_size, target_height, target_width, error, verbose, \
        nsfw, search_string):
        self.any_size = any_size
        self.target_height = target_height
        self.target_width = target_width
        self.error = error
        self.verbose = verbose
        self.nsfw = nsfw
        self.search_string = search_string
