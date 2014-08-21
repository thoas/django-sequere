from sequere.utils import get_client

from . import settings
from .managers import InstanceManager


client = get_client(settings.CONNECTION, connection_class=settings.CONNECTION_CLASS)

manager = InstanceManager(client, prefix=settings.PREFIX)
