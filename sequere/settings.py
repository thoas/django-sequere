from django.conf import settings


BACKEND_CLASS = getattr(settings, 'SEQUERE_BACKEND_CLASS', 'sequere.backends.database.DatabaseBackend')

FAIL_SILENTLY = getattr(settings, 'SEQUERE_FAIL_SILENTLY', False)
