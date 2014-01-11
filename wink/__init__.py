""" Library for interfacing with Wink API for devices by Quirky, including:

    - "Eggminder" eggtray
    - "Nimbus" cloud_clock
    - "Pivot Power Genius" powerstrip
    - "Porkfolio" piggy_bank
    - "Spotter" sensor_pod

To get started, you will need:
    - Oauth tokens for the API
    - a Wink account

1) run 'login' and provide the requested information

2) run 'init' to instantiate the Wink class

"config_file_save" and "config_file_load" are convenience functions for
persisting auth data between sessions. However, since the auth data is just a
simple dictionary, you can easily replace this with whatever method is most
convenient for your application (e.g. convert to JSON).

"login" is a helper function that requests the necessary authentication
information from the user and saves it to a configuration file 'config.cfg'.

"init" is another helper function that reads from a config file, instantiates
the Wink class, and populates the devices from the Wink server.

"""

from auth import auth, reauth, need_to_reauth

import persist

from api import Wink

from util import login, init
