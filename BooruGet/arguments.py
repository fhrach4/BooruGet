"""
Represents the arguments passed into the program
"""

class Arguments(object):
    """
    Class to hold the arguments specified in the config file and from the
    command line
    """


    def __init__(self, any_size, target_height, target_width, error, verbose, \
                nsfw, search_string, username, password):
        """
        any_size        ->  Boolean ->  True if the program should download
                                        any sized image, otherwise, the
                                        program will only download matches
                                        for the resolution and aspect ration

        target_height   ->  Int     ->  The height to search for

        target_width    ->  Int     ->  The width to search for

        error           ->  Float   ->  the 'error' when choosing a picture
                                        A picture is deemed acceptatable if
                                        it's size is within the percentage
                                        over or under the target for.

        verbose         ->  Boolean ->  The verbosity level to output
                                        (For debugging purposes)

        nsfw            ->  Boolean ->  True if images taged as 'nsfw' should
                                        be downloaded, otherwise false

        search_string   ->  String  ->  the tags to search for seperated by a
                                        space

        username        ->  String  ->  the username to be used for any
                                        connections

        password        ->  String  ->  the password HASH to be used for any
                                        connections. *DO NOT STORE A PLAIN TEXT
                                        PASSWORD IN HERE FOR THE LOVE OF GOD*
        """
        self.any_size = any_size
        self.target_height = target_height
        self.target_width = target_width
        self.error = error
        self.verbose = verbose
        self.nsfw = nsfw
        self.search_string = search_string
        self.username = username
        self.password = password
