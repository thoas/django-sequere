from django.dispatch import Signal

follow = Signal(providing_args=['from_instance', 'to_instance', ], use_caching=True)

unfollow = Signal(providing_args=['from_instance', 'to_instance', ], use_caching=True)
