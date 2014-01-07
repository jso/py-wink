if __name__ == "__main__":
    from wink.api import wink

    w = wink("config.cfg")

    w.populate_devices()

    for device in w.devices:
        print device.__class__.__name__, device.id
