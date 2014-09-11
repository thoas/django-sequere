from django.conf import settings

from sequere.backends.redis.settings import *


TIMELINE_PREFIX = getattr(settings,
                          'SEQUERE_TIMELINE_REDIS_PREFIX',
                          '%stimeline:' % getattr(settings, 'SEQUERE_REDIS_PREFIX', 'sequere:'))

TIMELINE_NYDUS_CONNECTION = getattr(settings, 'SEQUERE_TIMELINE_NYDUS_CONNECTION', None)
