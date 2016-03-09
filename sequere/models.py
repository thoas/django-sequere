
def follow(from_instance, to_instance):
    from sequere import app

    return app.backend.follow(from_instance, to_instance)


def is_following(from_instance, to_instance):
    from sequere import app

    return app.backend.is_following(from_instance, to_instance)


def unfollow(from_instance, to_instance):
    from sequere import app

    return app.backend.unfollow(from_instance, to_instance)


def get_followings(instance, *args, **kwargs):
    from sequere import app

    return app.backend.get_followings(instance, *args, **kwargs)


def get_followings_count(instance, *args, **kwargs):
    from sequere import app

    return app.backend.get_followings_count(instance, *args, **kwargs)


def get_followers_count(instance, *args, **kwargs):
    from sequere import app

    return app.backend.get_followers_count(instance, *args, **kwargs)


def get_followers(instance, *args, **kwargs):
    from sequere import app

    return app.backend.get_followers(instance, *args, **kwargs)


def get_friends_count(instance, *args, **kwargs):
    from sequere import app

    return app.backend.get_friends_count(instance, *args, **kwargs)


def get_friends(instance, *args, **kwargs):
    from sequere import app

    return app.backend.get_friends(instance, *args, **kwargs)
