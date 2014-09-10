from django.dispatch import Signal

pre_save = Signal(providing_args=['instance', 'action', ])
post_save = Signal(providing_args=['instance', 'action', ])

pre_delete = Signal(providing_args=['instance', 'action', ])
post_delete = Signal(providing_args=['instance', 'action', ])
