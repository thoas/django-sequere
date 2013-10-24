from .base import BaseBackend

from ..models import Follow


class SimpleBackend(BaseBackend):
    model = Follow

    def follow(self, from_instance, to_instance):
        from_identifier = self.get_identifier(from_instance)

        to_identifier = self.get_identifier(to_instance)

        params = {
            'from_identifier': from_identifier,
            'from_object_id': from_instance.pk,
            'to_identifier': to_identifier,
            'to_object_id': to_instance.pk
        }

        new, created = self.model.objects.get_or_create(**params)

        return new

    def unfollow(self, from_instance, to_instance):
        raise NotImplemented

    def get_followers(self, instance):
        raise NotImplemented

    def get_followings(self, instance):
        raise NotImplemented

    def is_following(self, from_instance, to_instance):
        raise NotImplemented
