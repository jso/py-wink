if __name__ == "__main__":
    import wink

    auth_info = wink.config_file_load("config.cfg")

    w = wink.wink(**auth_info)

    w.populate_devices()

    for device in w.devices:
        print device.__class__.__name__, device.id
