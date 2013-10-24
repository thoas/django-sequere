from ..registry import registry


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

    def get_identifier(self, instance):
        klass = registry.sequere_for_model(instance.__class__)

        return klass().get_identifier()
