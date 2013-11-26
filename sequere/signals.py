from django.dispatch import Signal


followed = Signal(providing_args=['from_instance', 'to_instance'])

unfollowed = Signal(providing_args=['from_instance', 'to_instance'])
