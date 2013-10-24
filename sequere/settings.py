from django.conf import settings


BACKEND_CLASS = getattr(settings, 'SEQUERE_BACKEND_CLASS', 'sequere.backends.simple.SimpleBackend')
