from ConfigParser import ConfigParser
import httplib2
import json

import device_types

class wink(object):

    def __init__(self, config_file):
        self.config_file = config_file
        self.config = ConfigParser()
        self.config.read(self.config_file)
        self.http = httplib2.Http()

        self.username = None
        if self.config.has_option("client", "most_recent_login"):
            self.username = self.config.get("client", "most_recent_login")

        self.devices = []

    def save_config(self):
        with open(self.config_file, "wb") as f:
            self.config.write(f)

    def _url(self, path):
        return "%s%s" % (self.config.get("api", "base_url"), path)

    def _headers(self):
        return dict(
            Authorization="Bearer %s" % self.config.get(
                "access_tokens", 
                self.username),
        )

    def logged_in(self):
        return (
            self.username is not None and
            self.config.has_section("access_tokens") and
            self.config.has_option("access_tokens", self.username)
        )

    def act_as(self, username):
        """
        Change the username that will be assumed for all calls.

        Only necessary if you are managing multiple logins. By
        default, it is the last username you authenticated.
        """

        self.username = username

    def auth(self, username, password=None):
        """
        Do OAuth login.
        
        If no password is provided, assume there is a valid refresh_token.
        Otherwise, do username/password authentication.
        """

        body = dict(
            client_id=self.config.get("client", "id"),
            client_secret=self.config.get("client", "secret"),
        )

        if password is not None:
            body["username"] = username
            body["password"] = password
            body["grant_type"] = "password"
        else:
            body["refresh_token"] = self.config.get("refresh_tokens", username)
            body["grant_type"] = "refresh_token"

        headers = {"Content-Type": "application/json"}
        body = json.dumps(body)

        resp, content = self.http.request(
            self._url("/oauth2/token"),
            "POST",
            headers=headers,
            body=body
        )

        if resp["status"] != "201":
            raise RuntimeError(
                "expected HTTP 201, but got %s for POST /oauth2/token" % resp["status"] 
            )

        data = json.loads(content)

        if not self.config.has_section("access_tokens"):
            self.config.add_section("access_tokens")
        self.config.set("access_tokens", username, data["data"]["access_token"])

        if not self.config.has_section("refresh_tokens"):
            self.config.add_section("refresh_tokens")
        self.config.set("refresh_tokens", username, data["data"]["refresh_token"])
        
        self.config.set("client", "most_recent_login", username)

        self.save_config()

        self.username = username

    def _http(self, path, method, headers={}, body=None, expected="200"):
        # add the auth header
        all_headers = self._headers()
        all_headers.update(headers)

        if body: 
            all_headers["Content-Type"] = "application/json"
            if type(body) is not str:
                body = json.dumps(body)

        resp, content = self.http.request(
            self._url(path),
            method,
            headers=all_headers,
            body=body
        )

        if (type(expected) is str and 
            resp["status"] != expected) or (
                resp["status"] not in expected):
            raise RuntimeError(
                "expected HTTP %s, but got %s for %s %s" % (
                    expected, 
                    resp["status"], 
                    method, 
                    path,
                )
            )

        if content:
            return json.loads(content)
        return {}

    def _get(self, path):
        return self._http(path, "GET").get("data")

    def _put(self, path, data):
        return self._http(path, "PUT", body=data)

    def _post(self, path, data):
        return self._http(path, "POST", body=data, expected=["200", "201", "202"])

    def _delete(self, path):
        return self._http(path, "DELETE", expected="204")

    def get_profile(self):
        return self._get("/users/me")

    def update_profile(self, data):
        return self._put("/users/me", data)

    def get_devices(self):
        return self._get("/users/me/wink_devices")

    def get_services(self):
        return self._get("/users/me/linked_services")

    def create_service(self, data):
        return self._post("/users/me/linked_services", data)

    def get_icons(self):
        return self._get("/icons")

    def get_channels(self):
        return self._get("/channels")

    def populate_devices(self):
        devices_info = self.get_devices()

        self.devices = []

        for device_info in devices_info:
            device_type, device_id = None, None
            for k in device_info:
                if k.endswith("_id"):
                    device_type = k[:-3]
                    device_id = device_info[k]
                    break

            if device_type is None: continue

            device_cls = getattr(device_types, device_type)
            device_obj = device_cls(self, device_id, device_info)
            self.devices.append(device_obj)

