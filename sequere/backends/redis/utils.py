from sequere.utils import get_setting


def get_key(*args, **kwargs):
    separator = kwargs.pop('separator', get_setting('KEY_SEPARATOR'))

    key = separator.join(['%s' % arg for arg in args if arg is not None])

    return key
