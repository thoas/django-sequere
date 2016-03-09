from sequere.utils import load_class, get_setting


def get_backend():
    return load_class(get_setting('TIMELINE_BACKEND'))(**get_setting('TIMELINE_BACKEND_OPTIONS'))


backend = get_backend()
