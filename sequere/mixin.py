class SequereMixin(object):
    def follow(self, instance):
        from .models import follow

        return follow(self, instance)

    def is_following(self, instance):
        from .models import is_following

        return is_following(self, instance)

    def unfollow(self, instance):
        from .models import unfollow

        return unfollow(self, instance)

    def get_followings(self, *args, **kwargs):
        from .models import get_followings

        return get_followings(self, *args, **kwargs)

    def get_followings_count(self, *args, **kwargs):
        from .models import get_followings_count

        return get_followings_count(self, *args, **kwargs)

    def get_followers_count(self, *args, **kwargs):
        from .models import get_followers_count

        return get_followers_count(self, *args, **kwargs)

    def get_friends_count(self, *args, **kwargs):
        from .models import get_friends_count

        return get_friends_count(self, *args, **kwargs)

    def get_friends(self, *args, **kwargs):
        from .models import get_friends

        return get_friends(self, *args, **kwargs)

    def get_followers(self, *args, **kwargs):
        from .models import get_followers

        return get_followers(self, *args, **kwargs)
