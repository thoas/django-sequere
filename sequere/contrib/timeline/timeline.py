from django.core.exceptions import ImproperlyConfigured

from sequere.backends import get_backend
from sequere.utils import get_client

from . import settings


class Timeline(object):
    def __init__(self, instance, *args, **kwargs):
        self.instance = instance
        self.backend = get_backend()
        self.prefix = kwargs.pop('prefix', settings.PREFIX)
        self.kwargs = kwargs.pop('kwargs', {})

        connection_class = kwargs.pop('connection_class', settings.CONNECTION_CLASS)

        nydus_connection = settings.NYDUS_CONNECTION

        if nydus_connection:
            try:
                from nydus.db import create_cluster
            except ImportError:
                raise ImproperlyConfigured(
                    "The nydus backend requires nydus to be installed.")
            else:
                self.client = create_cluster(nydus_connection)
        else:
            self.client = get_client(settings.CONNECTION, connection_class=connection_class)

    def add(self, action):
        pass

    def remove(self, action):
        pass
