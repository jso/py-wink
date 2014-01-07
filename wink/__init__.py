""" 
Library for interfacing with Wink API for devices by Quirky, including:
    - "Eggminder" eggtray
    - "Nimbus" cloud_clock
    - "Pivot Power Genius" powerstrip
    - "Porkfolio" piggy_bank
    - "Spotter" sensor_pod

To get started, you will need:
    - Oauth tokens for the API
    - a Wink account

1) call the "auth" function

2) init the "wink" class with the "auth" results as kwargs

3) call "wink.populate_devices" to read the devices associated with your
    account

"config_file_save" and "config_file_load" are convenience functions for
persisting auth data between sessions. However, since the auth data is just a
simple dictionary, you can easily replace this with whatever method is most
convenient for your application (e.g. convert to JSON).

"""

from auth import auth, reauth

from persist import config_file_save, config_file_load

from api import wink
