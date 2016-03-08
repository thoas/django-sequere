from django.conf import settings

BACKEND = getattr(settings, 'SEQUERE_BACKEND', 'sequere.backends.database.DatabaseBackend')

BACKEND_OPTIONS = getattr(settings, 'SEQUERE_BACKEND_OPTIONS', {})

FAIL_SILENTLY = getattr(settings, 'SEQUERE_FAIL_SILENTLY', False)
