from django.core.exceptions import ImproperlyConfigured

from sequere.utils import get_client
from sequere.backends.redis.managers import Manager

from . import settings
from .wrappers import RedisWrapper, NydusWrapper

nydus_connection = settings.TIMELINE_NYDUS_CONNECTION

if nydus_connection:
    try:
        from nydus.db import create_cluster
    except ImportError:
        raise ImproperlyConfigured(
            "The nydus backend requires nydus to be installed.")
    else:
        client = NydusWrapper(create_cluster(nydus_connection))
else:
    client = RedisWrapper(get_client(settings.TIMELINE_CONNECTION, connection_class=settings.TIMELINE_CONNECTION_CLASS))

storage = Manager(client, prefix=settings.TIMELINE_PREFIX)
