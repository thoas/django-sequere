from . import settings


def get_key(*args, **kwargs):
    separator = kwargs.pop('separator', settings.KEY_SEPARATOR)

    key = separator.join(['%s' % arg for arg in args if arg is not None])

    return key
