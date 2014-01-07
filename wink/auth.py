"""
Functions for authenticating, and several alternatives
for persisting credentials.

Both auth and reauth functions require the following kwargs:
    username
    client_id
    client_secret
    base_url
"""

import httplib2
import json

def auth(**kwargs):
    """ Do password authentication.
    
    Also requires kwarg "password".
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
    """ Use the refresh token to update the access token.

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

    if resp["status"] != "201":
        raise RuntimeError(
            "expected HTTP 201, but got %s for auth" % resp["status"] 
        )

    data = json.loads(content)["data"]

    new_auth_data = dict(kwargs)

    # do this second to be sure we overwrite any old tokens
    new_auth_data.update(dict(
        access_token=data["access_token"],
        refresh_token=data["refresh_token"],
    ))

    return new_auth_data

