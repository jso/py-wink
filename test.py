if __name__ == "__main__":
    import wink

    w = wink.init()

    for device in w.device_list():
        print device.__class__.__name__, device.id
