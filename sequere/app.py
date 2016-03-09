from sequere.utils import load_class, get_setting


def get_backend():
    return load_class(get_setting('BACKEND'))(**get_setting('BACKEND_OPTIONS'))


backend = get_backend()
