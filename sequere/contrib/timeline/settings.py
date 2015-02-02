from django.conf import settings

from sequere.backends.redis.settings import *  # noqa


TIMELINE_CONNECTION_CLASS = getattr(settings, 'SEQUERE_TIMELINE_CONNECTION_CLASS', None)

TIMELINE_CONNECTION = getattr(settings, 'SEQUERE_TIMELINE_REDIS_CONNECTION', {})

TIMELINE_IMPORT_ACTIONS_ON_FOLLOW = getattr(settings, 'SEQUERE_IMPORT_ACTIONS_ON_FOLLOW', True)

TIMELINE_REMOVE_ACTIONS_ON_UNFOLLOW = getattr(settings, 'SEQUERE_IMPORT_ACTIONS_ON_UNFOLLOW', True)

TIMELINE_PREFIX = getattr(settings,
                          'SEQUERE_TIMELINE_REDIS_PREFIX',
                          '%stimeline:' % getattr(settings, 'SEQUERE_REDIS_PREFIX', 'sequere:'))

TIMELINE_NYDUS_CONNECTION = getattr(settings, 'SEQUERE_TIMELINE_NYDUS_CONNECTION', None)
