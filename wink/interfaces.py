import urllib

class Sharing(object):
    
    all_permissions = [
        "read_data",
        "write_data",
        "read_triggers",
        "write_triggers",
        "manage_triggers",
        "manage_sharing",
    ]

    def _share_path(self, email=None):
        if not email:
            return "%s/users" % self._path()
        return "%s/users/%s" % (self._path(), urllib.quote(email))

    def get_sharing(self):
        return self.wink._get(self._share_path())

    def share_with(self, email, permissions):
        permissions = set(permissions) & set(Sharing.all_permissions)
        data = dict(
            email=email,
            permissions=list(permissions),
        )
        return self.wink._post(self._share_path(), data)

    def unshare_with(self, email):
        return self.wink._delete(self._share_path(email))

class Triggers(object):
    
    def _device_trigger_path(self):
        return "%s/triggers" % self._path()

    def create_trigger(self, data):
        return self.wink._post(self._device_trigger_path(), data)

    def _trigger_path(self, id):
        return "/triggers/%s" % id

    def get_trigger(self, id):
        return self.wink._get(self._trigger_path(id))

    def update_trigger(self, id, data):
        return self.wink._put(self._trigger_path(id), data)

class Alarms(object):

    def _device_alarm_path(self):
        return "%s/alarms" % self._path()

    def get_alarms(self):
        return self.wink._get(self._device_alarm_path())

    def create_alarm(self, data):
        return self.wink._post(self._device_alarm_path(), data)

    def _alarm_path(self, id):
        return "/alarms/%s" % id

    def update_alarm(self, id, data):
        return self.wink._put(self._alarm_path(id), data)

    def delete_alarm(self, id):
        return self.wink._delete(self._alarm_path(id))

class Schedulable(object):

    def _schedule_path(self, id=None):
        if not id:
            return "%s/scheduled_outlet_states" % self._path()
        return "%s/scheduled_outlet_states/%s" % (self._path(), id)

    def create_schedule(self, data):
        return self.wink._post(self._schedule_path(), data)

    def update_schedule(self, id, data):
        return self.wink._put(self._schedule_path(id), data)

    def delete_schedule(self, id):
        return self.wink._delete(self._schedule_path(id))
