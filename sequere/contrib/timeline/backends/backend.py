from sequere import settings
from sequere.utils import load_class


backend = load_class(settings.BACKEND_CLASS)(**settings.BACKEND_OPTIONS)
