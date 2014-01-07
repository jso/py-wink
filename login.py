if __name__ == "__main__":
    import wink

    auth_info = dict(
        base_url="https://winkapi.quirky.com"
    )

    # request information from the user
    for k in [
        "client_id",
        "client_secret",
        "username",
        "password",
    ]:
        auth_info[k] = raw_input("%s? " % k)

    try:
        auth_result = wink.auth(**auth_info)
    except RuntimeError as e:
        print "Authentication failed. :("
        print e
    else:
        print "Authentication success! ;-)"
        wink.config_file_save("config.cfg", auth_result)

