from sequere.utils import load_class, get_setting


backend = load_class(get_setting('BACKEND'))(**get_setting('BACKEND_OPTIONS'))
