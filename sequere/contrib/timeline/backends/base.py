class BaseBackend(object):
    def get_action(self):
        raise NotImplementedError

    def delete(self, action):
        raise NotImplementedError

    def save(self, action):
        raise NotImplementedError

    def get_count(self, name, action=None, target=None):
        raise NotImplementedError

    def get_read_at(self):
        raise NotImplementedError

    def get_unread_count(self, read_at, action=None, target=None):
        raise NotImplementedError

    def get_private(self, action=None, target=None, desc=True):
        raise NotImplementedError

    def get_public(self, action=None, target=None, desc=True):
        raise NotImplementedError

    def get_private_count(self, action=None, target=None):
        raise NotImplementedError

    def get_public_count(self, action=None, target=None):
        raise NotImplementedError
