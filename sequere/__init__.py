version = (0, 2)

__version__ = '.'.join(map(str, version))

from .registry import autodiscover


__all__ = ['autodiscover']
