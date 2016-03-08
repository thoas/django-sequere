from django.conf import settings

BACKEND = getattr(settings, 'SEQUERE_TIMELINE_BACKEND', 'sequere.contrib.timeline.backends.redis.RedisBackend')

BACKEND_OPTIONS = getattr(settings, 'SEQUERE_TIMELINE_BACKEND_OPTIONS', {})

TIMELINE_IMPORT_ACTIONS_ON_FOLLOW = getattr(settings, 'SEQUERE_IMPORT_ACTIONS_ON_FOLLOW', True)

TIMELINE_REMOVE_ACTIONS_ON_UNFOLLOW = getattr(settings, 'SEQUERE_IMPORT_ACTIONS_ON_UNFOLLOW', True)
