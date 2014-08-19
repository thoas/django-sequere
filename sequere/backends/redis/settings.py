from django.conf import settings

CONNECTION_CLASS = getattr(settings, 'SEQUERE_REDIS_CONNECTION_CLASS', None)

CONNECTION = getattr(settings, 'SEQUERE_REDIS_CONNECTION', {})

PREFIX = getattr(settings, 'SEQUERE_REDIS_PREFIX', 'sequere')

KEY_SEPARATOR = getattr(settings, 'SEQUERE_KEY_SEPARATOR', ':')
