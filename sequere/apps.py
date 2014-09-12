from django.apps import AppConfig


class SequereConfig(AppConfig):
    name = 'sequere'
    verbose_name = 'Sequere'

    def ready(self):
        super(SequereConfig, self).ready()
        self.module.autodiscover()
