from sequere.utils import load_class, get_setting


backend = load_class(get_setting('TIMELINE_BACKEND'))(**get_setting('TIMELINE_BACKEND_OPTIONS'))
