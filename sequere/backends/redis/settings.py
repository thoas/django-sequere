from django.conf import settings

KEY_SEPARATOR = getattr(settings, 'SEQUERE_KEY_SEPARATOR', ':')
