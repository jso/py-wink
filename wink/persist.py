from ConfigParser import ConfigParser


class PersistInterface(object):
    """
    Persistence classes should implement this interface.
    """

    def load(self):
        return {}

    def save(self, data):
        pass


class ConfigFile(PersistInterface):
    """Use a config file to persist authentication information.
    """

    def __init__(self, filename="config.cfg"):
        self.filename = filename

    def load(self):
        cp = ConfigParser()
        cp.read(self.filename)
        return dict(cp.items("auth"))

    def save(self, data):
        cp = ConfigParser()
        cp.add_section("auth")
        for k, v in data.iteritems():
            cp.set("auth", k, v)
        with open(self.filename, "wb") as f:
            cp.write(f)
