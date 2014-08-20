from .base import ModelBase


class SequereRegistry(dict):
    def __init__(self):
        self._models = {}

    def for_model(self, model):
        try:
            return self._models[model]
        except KeyError:
            return

    def get_identifier(self, instance):
        from django.db import models

        klass = instance

        if isinstance(instance, models.Model):
            klass = instance.__class__

        return dict((v, k) for k, v in self.identifiers.items()).get(klass)

    @property
    def identifiers(self):
        return dict((v().get_identifier(), k)
                    for k, v in self._models.items())

    def unregister(self, name):
        del self[name]

    def register(self, *args, **kwargs):
        from django.db import models

        sequere = None
        model = None

        assert len(args) <= 2, 'register takes at most 2 args'
        assert len(args) > 0, 'register takes at least 1 arg'

        for arg in args:
            if issubclass(arg, models.Model):
                model = arg
            else:
                sequere = arg

        if model:
            self._register_model(model, sequere, **kwargs)
        else:
            name = kwargs.get('name', sequere.__name__)
            sequere = type(name, (sequere,), kwargs)
            self._register(sequere)

    def _register_model(self, model, sequere=None,
                        name=None, **kwargs):

        if name is not None:
            pass
        elif sequere is not None:
            if sequere.__name__.find(model.__name__) == 0:
                name = sequere.__name__
            else:
                name = '%s%s' % (model.__name__, sequere.__name__)
        else:
            name = '%sSequere' % model.__name__

        if sequere is None:
            base = ModelBase
        else:
            base = sequere

        kwargs['model'] = model

        sequere = type(name, (base,), kwargs)

        self._register(sequere)
        self._models[model] = sequere

    def _register(self, sequere):
        self[sequere.__name__] = sequere


def _autodiscover(registry):
    import copy
    from django.conf import settings
    from django.utils.importlib import import_module
    from django.utils.module_loading import module_has_submodule

    for app in settings.INSTALLED_APPS:
        mod = import_module(app)
        # Attempt to import the app's admin module.
        try:
            before_import_registry = copy.copy(registry)
            import_module('%s.sequere_registry' % app)
        except:
            # Reset the model registry to the state before the last import as
            # this import will have to reoccur on the next request and this
            # could raise NotRegistered and AlreadyRegistered exceptions
            # (see #8245).
            registry = before_import_registry

            # Decide whether to bubble up this error. If the app just
            # doesn't have an admin module, we can ignore the error
            # attempting to import it, otherwise we want it to bubble up.
            if module_has_submodule(mod, 'sequere_registry'):
                raise

registry = SequereRegistry()


def autodiscover():
    _autodiscover(registry)


def register(*args, **kwargs):
    return registry.register(*args, **kwargs)
