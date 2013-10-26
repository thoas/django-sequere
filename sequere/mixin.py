from . import models as sequere


class SequereMixin(object):
    def follow(self, instance):
        return sequere.follow(self, instance)

    def is_following(self, instance):
        return sequere.is_following(self, instance)

    def unfollow(self, instance):
        return sequere.unfollow(self, instance)

    def get_followings(self, desc=True, chunks_length=None):
        return sequere.get_followings(self, desc=desc, chunks_length=chunks_length)

    def get_followings_count(self):
        return sequere.get_followings_count(self)

    def get_followers_count(self):
        return sequere.get_followers_count(self)

    def get_followers(self, desc=True, chunks_length=None):
        return sequere.get_followers(self, desc=desc, chunks_length=chunks_length)
