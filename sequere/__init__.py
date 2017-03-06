version = (0, 4, 1)

__version__ = '.'.join(map(str, version))

from .registry import register, autodiscover  # noqa


__all__ = ['register', 'autodiscover']

default_app_config = 'sequere.apps.SequereConfig'
