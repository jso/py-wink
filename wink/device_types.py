from interfaces import *

class BaseDevice(object):
    
    def __init__(self, wink, id, data):
        self.wink = wink
        self.id = id
        self.data = data

    def _path(self):
        return "/%ss/%s" % (self.__class__.__name__, self.id)

    def get(self):
        return self.wink._get(self._path())

    def update(self, data):
        return self.wink._put(self._path(), data)

class powerstrip(BaseDevice, Sharing, Triggers):

    class outlet(BaseDevice, Schedulable): pass

class eggtray(BaseDevice, Sharing, Triggers): pass

class cloud_clock(BaseDevice, Sharing, Triggers, Alarms):

    # while dial clearly belongs to a cloud_clock, the API puts
    # the dial interface at the root level, so I am representing
    # it as a BaseDevice
    class dial(BaseDevice):

        def templates(self):
            # TODO API doc is wrong; given as /dial_template, actually is /dial_templates
            return self.wink._get("/dial_templates")

    def __init__(self, wink, id, data):
        BaseDevice.__init__(self, wink, id, data)

        self.dials = []
        for dial_info in self.data["dials"]:
            this_dial = cloud_clock.dial(self.wink, dial_info["dial_id"], dial_info)
            self.dials.append(this_dial)

class piggy_bank(BaseDevice, Sharing, Triggers): pass
# TODO: deposits

class sensor_pod(BaseDevice, Sharing, Triggers): pass
