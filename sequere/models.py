from django.db import models
from django.utils.encoding import python_2_unicode_compatible
from django.db.models.query import QuerySet


class FollowQuerySet(QuerySet):
    pass


class FollowManager(models.Manager):
    def get_query_set(self):
        return FollowQuerySet(self.model)


@python_2_unicode_compatible
class Follow(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)

    from_object_id = models.PositiveIntegerField()
    from_identifier = models.CharField(max_length=50, db_index=True)

    to_object_id = models.PositiveIntegerField()
    to_identifier = models.CharField(max_length=50, db_index=True)

    objects = FollowManager()

    def __str__(self):
        return '<%s: %d>' % (self.identifier,
                             self.object_id)


def follow(from_instance, to_instance):
    pass


def is_following(from_instance, to_instance):
    pass


def unfollow(from_instance, to_instance):
    pass


def get_followings(instance):
    pass


def get_followers(instance):
    pass
