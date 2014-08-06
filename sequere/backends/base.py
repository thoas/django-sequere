class BaseBackend(object):
    def follow(self, from_instance, to_instance):
        raise NotImplemented

    def unfollow(self, from_instance, to_instance):
        raise NotImplemented

    def get_followers(self, instance):
        raise NotImplemented

    def get_followings(self, instance):
        raise NotImplemented

    def is_following(self, from_instance, to_instance):
        raise NotImplemented

    def get_followings_count(self, instance):
        raise NotImplemented

    def get_followers_count(self, instance):
        raise NotImplemented

    def clear(self):
        raise NotImplemented
