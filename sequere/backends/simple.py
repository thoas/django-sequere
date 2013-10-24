from .base import BaseBackend

from ..models import Follow
from ..helpers import chunks


class SimpleBackend(BaseBackend):
    model = Follow
    chunks_length = 20

    def _params(self, from_instance=None, to_instance=None):
        params = {}

        if from_instance:
            from_identifier = self.get_identifier(from_instance)

            params.update({
                'from_identifier': from_identifier,
                'from_object_id': from_instance.pk,
            })

        if to_instance:
            to_identifier = self.get_identifier(to_instance)

            params.update({
                'to_identifier': to_identifier,
                'to_object_id': to_instance.pk
            })

        return params

    def follow(self, from_instance, to_instance):
        new, created = self.model.objects.get_or_create(**self._params(from_instance=from_instance,
                                                                       to_instance=to_instance))

        return new

    def unfollow(self, from_instance, to_instance):
        return self.model.objects.filter(**self._params(from_instance=from_instance,
                                                        to_instance=to_instance)).delete()

    def get_followers(self, instance):
        count = self.get_followers_count(instance)

        return chunks(self.model.objects.filter(**self._params(to_instance=instance)),
                      self.chunks_length,
                      count)

    def get_followings(self, instance):
        count = self.get_followings_count(instance)

        return chunks(self.model.objects.filter(**self._params(from_instance=instance)),
                      self.chunks_length,
                      count)

    def is_following(self, from_instance, to_instance):
        return self.model.objects.filter(**self._params(from_instance=from_instance,
                                                        to_instance=to_instance)).exists()

    def get_followings_count(self, instance):
        return self.model.objects.filter(from_identifier=self.get_identifier(instance),
                                         from_object_id=instance.pk).count()

    def get_followers_count(self, instance):
        return self.model.objects.filter(to_identifier=self.get_identifier(instance),
                                         to_object_id=instance.pk).count()
