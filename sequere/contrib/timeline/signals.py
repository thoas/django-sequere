from django.dispatch import Signal

pre_save = Signal(providing_args=['instance', 'action', ])
post_save = Signal(providing_args=['instance', 'action', ])
