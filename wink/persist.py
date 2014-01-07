from ConfigParser import ConfigParser

def config_file_save(filename, data):
    cp = ConfigParser()
    cp.add_section("auth")
    for k, v in data.iteritems():
        cp.set("auth", k, v)
    with open(filename, "wb") as f:
        cp.write(f)

def config_file_load(filename):
    cp = ConfigParser()
    cp.read(filename)
    return dict(cp.items("auth"))
