from django.core.exceptions import ImproperlyConfigured

from sequere.backends.redis.managers import Manager

from . import settings

nydus_connection = settings.TIMELINE_NYDUS_CONNECTION

try:
    from nydus.db import create_cluster
except ImportError:
    raise ImproperlyConfigured(
        "The nydus backend requires nydus to be installed.")
else:
    client = create_cluster(nydus_connection)

storage = Manager(client, prefix=settings.TIMELINE_PREFIX)
