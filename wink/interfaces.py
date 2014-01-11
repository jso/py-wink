import urllib


class Sharable(object):

    read_permissions = [
        "read_data",
        "read_triggers",
    ]

    write_permissions = [
        "write_data",
        "write_triggers",
    ]

    manage_permissions = [
        "manage_triggers",
        "manage_sharing",
    ]

    all_permissions = (
        read_permissions +
        write_permissions +
        manage_permissions
    )

    def _share_path(self, email=None):
        if not email:
            return "%s/users" % self._path()
        return "%s/users/%s" % (self._path(), urllib.quote(email))

    def get_sharing(self):
        return self.wink._get(self._share_path())

    def share_with(self, email, permissions):
        permissions = set(permissions) & set(Sharing.all_permissions)
        data = dict(
            email=email,
            permissions=list(permissions),
        )
        return self.wink._post(self._share_path(), data)

    def unshare_with(self, email):
        return self.wink._delete(self._share_path(email))
