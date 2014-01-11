"""Utility functions that are best kept inside the package,
as opposed to external scripts.

"""

from api import Wink
from auth import auth
from persist import ConfigFile


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

        cf = ConfigFile(config_file)
        cf.save(auth_result)


def init(config_file="config.cfg", debug=False):
    """
    Load authentication information from the specified configuration file,
    and init the Wink object.
    """

    cf = ConfigFile(config_file)

    return Wink(cf, debug=debug)
