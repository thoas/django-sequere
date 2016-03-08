from sequere import settings
from sequere.utils import load_class


backend = load_class(settings.BACKEND)(**settings.BACKEND_OPTIONS)
