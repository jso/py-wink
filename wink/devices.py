from interfaces import *

import time

class BaseDevice(object):
    
    def __init__(self, wink, id, data):
        self.wink = wink
        self.id = id
        self.data = data

    def _path(self):
        return "/%ss/%s" % (self.device_type(), self.id)

    def device_type(self):
        return self.__class__.__name__

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
            return self.wink._get("/dial_templates")

        def get_config(self, status=None):
            if not status:
                status = self.get()
            
            # drop "id" keys, so we're just
            # left with the keys that are settable
            del status["dial_id"]
            del status["dial_index"]

            del status["position"]
            # TODO: reevaluate whether "position" needs to be
            # removed after Quirky replies to my bug report. There
            # is some odd behavior here. Currently, when calling 
            # "update" on a dial, if both position and value are 
            # given, the dial doesn't move at all. If only value
            # is given, then the raw 'value' value is copied to the
            # position field (I think position should be recomputed
            # based on the new dial_configuration)

            return status

        def revert(self):
            """
            If you break anything, run this to revert the dial
            configuration to the original value from when the object
            was instantiated.

            TODO: it would be great to have "revert" functionality on
            all devices, but the trick is figuring out how to get the
            device-specific "settable" config (i.e. get_config for
            each device).
            """

            old_config = self.get_config(self.data)
            self.update(old_config)

        def demo(self, delay=5):
            """
            Generates a sequence of updates to run the dial through 
            the range of values and positions.
            """
            
            original = self.get_config()

            # do some stuff
            values = [
                ("min", original["dial_configuration"]["min_value"]),
                ("max", original["dial_configuration"]["max_value"]),
            ]

            # set the dial to manual control
            self.update(dict(
                channel_configuration=dict(channel_id="10"),
                dial_configuration=original["dial_configuration"],
                label="demo!", 
            ))
            time.sleep(delay)

            for text, value in values:
                self.update(dict(value=value, label="%s: %s" % (text, value)))
                time.sleep(delay)

            # revert to the original configuration
            self.update(original)

        def flash_value(self, duration=5):
            """
            Temporarily replace the existing label with the current value
            for the specified duration.
            """

            original = self.get_config()

            # set the dial to manual control
            self.update(dict(
                channel_configuration=dict(channel_id="10"),
                dial_configuration=original["dial_configuration"],
                label="%s" % original["value"],
            ))
            time.sleep(duration)

            self.update(dict(
                channel_configuration=original["channel_configuration"],
                dial_configuration=original["dial_configuration"],
                label=original["label"],
                labels=original["labels"],
            ))

    def __init__(self, wink, id, data):
        BaseDevice.__init__(self, wink, id, data)

        self.dials = []
        for dial_info in self.data["dials"]:
            this_dial = cloud_clock.dial(self.wink, dial_info["dial_id"], dial_info)
            self.dials.append(this_dial)

    def rotate(self, direction="left"):
        statuses = [d.get_config() for d in self.dials]

        if direction == "left":
            statuses.append(statuses.pop(0))
        else:
            statuses.insert(0, statuses.pop(-1))

        for d, new_status in zip(self.dials, statuses):
            d.update(new_status)

class piggy_bank(BaseDevice, Sharing, Triggers): pass
# TODO: deposits

class sensor_pod(BaseDevice, Sharing, Triggers): pass
