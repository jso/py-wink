if __name__ == "__main__":
    from wink.api import wink

    w = wink("config.cfg")

    username = raw_input("username? ")
    password = raw_input("password? ")

    # do password auth
    w.auth(username, password)
