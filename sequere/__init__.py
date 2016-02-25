version = (0, 2, 7)

__version__ = '.'.join(map(str, version))

from .registry import register, autodiscover


__all__ = ['register', 'autodiscover']

default_app_config = 'sequere.apps.SequereConfig'
