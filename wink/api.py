import httplib2
import json

import devices

class Wink(object):

    required_kwargs = set([
        "base_url",
        "username",
        "access_token",
    ])

    content_headers = {
        "Content-Type": "application/json",
    }

    def __init__(self, **kwargs):
        for k in Wink.required_kwargs:
            if k not in kwargs:
                raise RuntimeError("kwarg %s not provided" % k)
            setattr(self, k, kwargs[k])

        self.http = httplib2.Http()
        self.devices = []

    def _url(self, path):
        return "%s%s" % (self.base_url, path)

    def _headers(self):
        return dict(
            Authorization="Bearer %s" % self.access_token,
        )

    def _http(self, path, method, headers={}, body=None, expected="200"):
        # add the auth header
        all_headers = self._headers()
        all_headers.update(headers)

        if body: 
            all_headers.update(Wink.content_headers)
            if type(body) is not str:
                body = json.dumps(body)

        resp, content = self.http.request(
            self._url(path),
            method,
            headers=all_headers,
            body=body
        )

        if type(expected) is str: expected = set([expected])

        if resp["status"] not in expected:
            raise RuntimeError(
                "expected code %s, but got %s for %s %s" % (
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

        del self.devices[:]

        for device_info in devices_info:
            device_type, device_id = None, None
            for k in device_info:
                if k.endswith("_id") and hasattr(devices, k[:-3]):
                    device_type = k[:-3]
                    device_id = device_info[k]
                    break

            if device_type is None: continue

            device_cls = getattr(devices, device_type)
            device_obj = device_cls(self, device_id, device_info)
            self.devices.append(device_obj)

