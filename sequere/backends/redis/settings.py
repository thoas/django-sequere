from django.conf import settings

CONNECTION_CLASS = getattr(settings, 'SEQUERE_REDIS_CONNECTION_CLASS',
                           getattr(settings, 'SEQUERE_CONNECTION_CLASS', None))

REDIS_CONNECTION = getattr(settings, 'SEQUERE_REDIS_CONNECTION',
                           getattr(settings, 'SEQUERE_CONNECTION', {}))

REDIS_PREFIX = getattr(settings, 'SEQUERE_REDIS_PREFIX',
                       getattr(settings, 'SEQUERE_PREFIX', 'sequere:'))

REDIS_FALLBACK_BACKEND_CLASS = getattr(settings, 'SEQUERE_REDIS_FALLBACK_BACKEND_CLASS',
                                       'sequere.backends.database.DatabaseBackend')
