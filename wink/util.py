"""
Utility functions that are best kept inside the package, as opposed to external
scripts.
"""

from api import Wink
from auth import auth
from persist import config_file_load, config_file_save

def login(base_url="https://winkapi.quirky.com", config_file="config.cfg"):
    """
    Request authentication information from the user,
    make the authentication request, and
    write the credentials to the specified configuration file.
    """

    auth_info = dict(
        base_url=base_url,
    )

    # request information from the user
    for k in [
        "client_id",
        "client_secret",
        "username",
        "password",
    ]:
        auth_info[k] = raw_input("%s? " % k)

    try:
        auth_result = auth(**auth_info)
    except RuntimeError as e:
        print "Authentication failed. :("
        print e
    else:
        print "Authentication success! ;-)"
        config_file_save(config_file, auth_result)

def init(config_file="config.cfg"):
    """
    Load authentication information from the specified configuration file,
    init the Wink object, and
    populate the device data structures from the Wink servers.
    """

    auth_info = config_file_load(config_file)
    w = Wink(**auth_info)
    w.populate_devices()
    return w
