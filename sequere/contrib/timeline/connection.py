from sequere.utils import get_client
from sequere.backends.redis.managers import Manager

from . import settings
from .wrappers import RedisWrapper

client = RedisWrapper(get_client(settings.TIMELINE_CONNECTION, connection_class=settings.TIMELINE_CONNECTION_CLASS))

storage = Manager(client, prefix=settings.TIMELINE_PREFIX)
