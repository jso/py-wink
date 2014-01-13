from interfaces import *

import time


class CreatableResourceBase(object):
    """Base class for 'creatable' objects, e.g.:
        - triggers
        - alarms
        - scheduled_outlet_states

    """

    # TODO add automatic getters/setters for these fields
    mutable_fields = []

    def __init__(self, parent, data):
        self.parent = parent
        self.data = data

        self.id = data["%s_id" % self.resource_type()]

    def _path(self):
        return "/%ss/%s" % (self.resource_type(), self.id)

    def resource_type(self):
        return self.__class__.__name__

    def get(self):
        return self.parent.wink._get(self._path())

    def update(self, data):
        return self.parent.wink._put(self._path(), data)

    def delete(self):
        return self.parent.wink._delete(self._path())


class CreatableSubResourceBase(CreatableResourceBase):

    def _path(self):
        return "%s%s" % (
            self.parent._path(),
            CreatableResourceBase._path(self)
        )


class DeviceBase(object):
    """Implements functionality shared by all devices:
        - get
        - update

    """

    # list of fields from the device 'get'
    # that should be removed so we only capture
    # the 'state' and 'configuration' of the device
    non_config_fields = []

    # TODO add automatic getters/setters for these fields
    mutable_fields = []

    subdevice_types = []

    def __init__(self, wink, data):
        self.wink = wink
        self.data = data

        self.id = data["%s_id" % self.device_type()]

        self._subdevices = []

        for subdevice_type in self.subdevice_types:
            subdevice_plural = "%ss" % subdevice_type.__name__
            setattr(self, "_%s" % subdevice_plural, [])
            setattr(self,
                    subdevice_plural,
                    self._subdevices_by_type_closure(subdevice_plural))
            subdevice_list = getattr(self, "_%s" % subdevice_plural)

            for subdevice_info in self.data[subdevice_plural]:
                this_obj = subdevice_type(
                    self.wink,
                    subdevice_info)
                self._subdevices.append(this_obj)
                subdevice_list.append(this_obj)

    def _subdevices_by_type_closure(self, subdevice_type):
        return lambda: self.subdevices_by_type(subdevice_type)

    def subdevices_by_type(self, typ):
        return list(getattr(self, "_%s" % typ, []))

    def subdevices(self):
        return list(self._subdevices)

    def _path(self):
        return "/%ss/%s" % (self.device_type(), self.id)

    def device_type(self):
        return self.__class__.__name__

    def get(self):
        return self.wink._get(self._path())

    def update(self, data):
        return self.wink._put(self._path(), data)

    def get_config(self, status=None):
        if not status:
            status = self.get()

        for field in self.non_config_fields:
            if field in status:
                del status[field]

        return status

    def revert(self):
        """
        If you break anything, run this to revert the device
        configuration to the original value from when the object
        was instantiated.
        """

        old_config = self.get_config(self.data)
        self.update(old_config)

        for subdevice in self.subdevices():
            subdevice.revert()

    class trigger(CreatableResourceBase):

        mutable_fields = [
            ("name", str),
            ("enabled", bool),
            ("trigger_configuration", dict),
            ("channel_configuration", dict),
        ]

    def _trigger_path(self):
        return "%s/triggers" % self._path()

    def triggers(self):
        return [
            DeviceBase.trigger(self, x)
            for x
            in self.get().get("triggers", [])
        ]

    def create_trigger(self, data):
        res = self.wink._post(self._trigger_path(), data)

        return DeviceBase.trigger(self, res)


class powerstrip(DeviceBase, Sharable):

    non_config_fields = [
        "powerstrip_id",

        # TODO revisit this decision -- can/should we
        # count them as revertible state?
        "powerstrip_triggers",
        "outlets",
        "last_reading",
        "mac_address",
        "serial",
        "subscription",
        "triggers",
        "user_ids",
    ]

    class outlet(DeviceBase):

        non_config_fields = [
            "outlet_id",
            "outlet_index",
        ]

        mutable_fields = [
            ("name", str),
            ("icon_id", str),
            ("powered", bool),
        ]

        class scheduled_outlet_state(CreatableSubResourceBase):

            mutable_fields = [
                ("name", str),
                ("powered", bool),
                ("enabled", bool),
                ("recurrence", str),
            ]

        def _schedule_path(self):
            return "%s/scheduled_outlet_states" % self._path()

        def create_schedule(self, data):
            res = self.wink._post(self._schedule_path(), data)

            return powerstrip.outlet.scheduled_outlet_state(self, res)

    subdevice_types = [
        outlet
    ]


class eggtray(DeviceBase, Sharable):
    pass


class cloud_clock(DeviceBase, Sharable):

    non_config_fields = [
        "cloud_clock_id",

        # TODO revisit this decision -- can/should we
        # count them as revertible state?
        "cloud_clock_triggers",
        "dials",  # will be done explicitly, later
        "last_reading",
        "mac_address",
        "serial",
        "subscription",
        "triggers",
        "user_ids",
    ]

    mutable_fields = [
        ("name", str),
    ]

    # while dial clearly belongs to a cloud_clock, the API puts
    # the dial interface at the root level, so I am representing
    # it as a DeviceBase
    class dial(DeviceBase):

        non_config_fields = [
            "dial_id",
            "dial_index",
            "labels",
            "position",
        ]

        mutable_fields = [
            ("name", str),
            ("label", str),
            ("channel_configuration", dict),
            ("dial_configuration", dict),
            ("brightness", int),
        ]

        def templates(self):
            return self.wink._get("/dial_templates")

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

    subdevice_types = [
        dial,
    ]

    def rotate(self, direction="left"):
        statuses = [d.get_config() for d in self.dials()]

        if direction == "left":
            statuses.append(statuses.pop(0))
        else:
            statuses.insert(0, statuses.pop(-1))

        for d, new_status in zip(self.dials(), statuses):
            d.update(new_status)

    class alarm(CreatableResourceBase):

        mutable_fields = [
            ("name", str),
            ("recurrence", str),
            ("enabled", bool),
        ]

    def _alarm_path(self):
        return "%s/alarms" % self._path()

    def alarms(self):
        return [
            cloud_clock.alarm(self, x)
            for x
            in self.get().get("alarms", [])
        ]

    def create_alarm(self, name, recurrence, enabled=True):
        data = dict(
            name=name,
            recurrence=recurrence,
            enabled=enabled)

        res = self.wink._post(self._alarm_path(), data)

        return cloud_clock.alarm(self, res)


class piggy_bank(DeviceBase, Sharable):
    pass
    # TODO: deposits


class sensor_pod(DeviceBase, Sharable):
    pass
