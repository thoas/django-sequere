from django.dispatch import Signal

pre_save = Signal(providing_args=['instance', 'action', ], use_caching=True)
post_save = Signal(providing_args=['instance', 'action', ], use_caching=True)
