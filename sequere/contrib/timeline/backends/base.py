class BaseBackend(object):
    def get_action(self):
        raise NotImplementedError

    def delete(self, action):
        raise NotImplementedError

    def save(self, action):
        raise NotImplementedError

    def get_count(self, instance, name, action=None, target=None):
        raise NotImplementedError

    def get_read_at(self):
        raise NotImplementedError

    def get_unread_count(self, instance, read_at, action=None, target=None):
        raise NotImplementedError

    def get_private(self, instance, action=None, target=None, desc=True):
        raise NotImplementedError

    def get_public(self, instance, action=None, target=None, desc=True):
        raise NotImplementedError

    def get_private_count(self, instance, action=None, target=None):
        raise NotImplementedError

    def get_public_count(self, instance, action=None, target=None):
        raise NotImplementedError
