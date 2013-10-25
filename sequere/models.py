from django.db import models
from django.utils.encoding import python_2_unicode_compatible
from django.db.models.query import QuerySet

from .backends import get_backend

from .registry import registry


class FollowQuerySet(QuerySet):
    def from_instance(self, instance):
        from_identifier = registry.get_identifier(instance)

        return self.filter(from_identifier=from_identifier,
                           from_object_id=instance.pk)

    def to_instance(self, instance):
        to_identifier = registry.get_identifier(instance)

        return self.filter(to_identifier=to_identifier,
                           to_object_id=instance.pk)


class FollowManager(models.Manager):
    def get_query_set(self):
        return FollowQuerySet(self.model)

    def from_instance(self, instance):
        return self.get_query_set().from_instance(instance)

    def to_instance(self, instance):
        return self.get_query_set().to_instance(instance)


@python_2_unicode_compatible
class Follow(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)

    from_object_id = models.PositiveIntegerField()
    from_identifier = models.CharField(max_length=50, db_index=True)

    to_object_id = models.PositiveIntegerField()
    to_identifier = models.CharField(max_length=50, db_index=True)

    objects = FollowManager()

    class Meta:
        ordering = ['-created_at', ]

    def __str__(self):
        return '[%s: %d] -> [%s: %d]' % (self.from_identifier,
                                         self.from_object_id,
                                         self.to_identifier,
                                         self.to_object_id)


def follow(from_instance, to_instance):
    return get_backend()().follow(from_instance, to_instance)


def is_following(from_instance, to_instance):
    return get_backend()().is_following(from_instance, to_instance)


def unfollow(from_instance, to_instance):
    return get_backend()().unfollow(from_instance, to_instance)


def get_followings(instance):
    return get_backend()().get_followings(instance)


def get_followings_count(instance):
    return get_backend()().get_followings_count(instance)


def get_followers_count(instance):
    return get_backend()().get_followers_count(instance)


def get_followers(instance):
    return get_backend()().get_followers(instance)
