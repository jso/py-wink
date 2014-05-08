"""Functions for authenticating, and several alternatives
for persisting credentials.

Both auth and reauth functions require the following kwargs:
    client_id
    client_secret
    base_url
"""

import datetime
import httplib2
import json

default_expires_in = 900

_datetime_format = "%Y-%m-%d %H:%M:%S"  # assume UTC


def _datetime_serialize(dt):
    return dt.strftime(_datetime_format)


def _datetime_deserialize(s):
    return datetime.datetime.strptime(s, _datetime_format)


def need_to_reauth(tolerance=10, **kwargs):
    """Determine whether reauthentication is necessary."""

    if "expires" not in kwargs:
        return True

    expires = _datetime_deserialize(kwargs["expires"])

    now = (
        datetime.datetime.utcnow() +
        datetime.timedelta(0, tolerance)
    )

    return now >= expires


def auth(**kwargs):
    """Do password authentication.

    Also requires kwargs "username" and "password".
    """

    data = dict(
        grant_type="password",
        username=kwargs["username"],
        password=kwargs["password"],
    )

    result = _auth(data, **kwargs)
    del result["password"]

    return result


def reauth(**kwargs):
    """Use the refresh token to update the access token.

    Also requires kwarg "refresh_token".
    """
    data = dict(
        grant_type="refresh_token",
        refresh_token=kwargs["refresh_token"],
    )

    return _auth(data, **kwargs)


def _auth(data, auth_path="/oauth2/token", **kwargs):
    body = dict(
        client_id=kwargs["client_id"],
        client_secret=kwargs["client_secret"],
        **data
    )

    http = httplib2.Http()
    resp, content = http.request(
        "".join([kwargs["base_url"], auth_path]),
        "POST",
        headers={"Content-Type": "application/json"},
        body=json.dumps(body),
    )

    # TODO handle case of bad auth information

    if resp["status"] != "201" and resp["status"] != "200":
        raise RuntimeError(
            "expected HTTP 200 or 201, but got %s for auth" % resp["status"]
        )

    data = json.loads(content)["data"]

    # make up an expiration time for the access token,
    # if one is not provided
    if "expires_in" not in data:
        data["expires_in"] = str(default_expires_in)

    # compute the expiration time in UTC and format in
    # seconds since the epoch
    expires = (
        datetime.datetime.utcnow() +
        datetime.timedelta(0, int(data["expires_in"]))
    )

    new_auth_data = dict(kwargs)

    # do this second to be sure we overwrite any old tokens
    new_auth_data.update(dict(
        access_token=data["access_token"],
        refresh_token=data["refresh_token"],
        expires=_datetime_serialize(expires),
    ))

    return new_auth_data
