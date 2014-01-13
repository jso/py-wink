if __name__ == "__main__":
    import time
    try:
        import wink
    except ImportError as e:
        import sys
        sys.path.insert(0, "..")
        import wink

    w = wink.init("../config.cfg")

    if "cloud_clock" not in w.device_types():
        raise RuntimeError(
            "you do not have a cloud_clock associated with your account!"
        )

    c = w.cloud_clock()

    print "found cloud_clock %s called %s!" % (c.id, c.data.get("name"))

    print "'demoing' each of the dials:"

    for i, dial in enumerate(c.dials()):
        print "dial #%d '%s'..." % (i+1, dial.data.get("name"))
        dial.demo()

    print "let's switch things up... rotate left!"
    c.rotate()
    time.sleep(5)

    print "reverting to original state."
    c.revert()
