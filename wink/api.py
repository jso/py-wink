import httplib2
import json

import devices

class Wink(object):
    """
    Main object for making API calls to the Wink cloud servers.

    Constructor requires the API base URL and an access token.

    "populate_devices" reads the device list from the Wink servers
    and instantiates the appropriate class for each device.

    There are several ways to access the device objects:
    "device_list" gives the full list of top-level devices
    "devices_by_type" gives all devices of a given type
    "device_types" gives all device types that are instantiated
    "[device_type]" returns the device object for the first seen
        for the given type
    "[device_type]s" returns a list of all devices of that type
    """

    required_kwargs = set([
        "base_url",
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
        self._device_list = []
        self._devices_by_type = {}

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

        # clean up data structures, just in case this is called
        # multiple times in the same instance.
        del self._device_list[:]
        for device_type in self._devices_by_type:
            delattr(self, device_type)
            delattr(self, "%ss" % device_type)
        self._devices_by_type.clear()

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

            # update some data structures to provide access to the devices
            self._device_list.append(device_obj)

            if not hasattr(self, device_type):
                setattr(self, device_type, self._get_device_func(device_obj))
                self._devices_by_type[device_type] = []
                setattr(self, "%ss" % device_type, self._get_device_list_func(device_type))

            self._devices_by_type[device_type].append(device_obj)
    
    def _get_device_func(self, device_object):
        return lambda: device_object

    def _get_device_list_func(self, device_type):
        return lambda: list(self._devices_by_type[device_type])

    def device_list(self):
        return list(self._device_list)

    def device_types(self):
        return list(self._devices_by_type)

    def devices_by_type(self, typ):
        return list(self._devices_by_type.get(typ, []))
