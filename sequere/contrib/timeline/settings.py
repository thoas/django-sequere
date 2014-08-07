from django.conf import settings

CONNECTION_CLASS = getattr(settings, 'SEQUERE_TIMELINE_CONNECTION_CLASS', None)

CONNECTION = getattr(settings, 'SEQUERE_TIMELINE_REDIS_CONNECTION', {})

PREFIX = getattr(settings,
                 'SEQUERE_TIMELINE_REDIS_PREFIX',
                 '%stimeline:' % getattr(settings, 'SEQUERE_REDIS_PREFIX', 'sequere:'))


NYDUS_CONNECTION = getattr(settings, 'SEQUERE_TIMELINE_NYDUS_CONNECTION', None)
