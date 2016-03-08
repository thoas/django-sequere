from __future__ import unicode_literals

from django.utils.encoding import python_2_unicode_compatible
from django.utils import six
from django.utils.encoding import force_str
from django.utils import timezone as datetime
from django.utils.lru_cache import lru_cache

from sequere.registry import registry


@lru_cache()
def get_actions():
    return dict((action.verb, action)
                for model_class in registry.values()
                for action in getattr(model_class, 'actions', []))


@python_2_unicode_compatible
class Action(object):
    verb = None

    def __init__(self, actor, target=None, date=None, **kwargs):
        self.actor = actor
        self.target = target
        self.kwargs = kwargs.pop('kwargs', {})
        self.date = date or datetime.now()
        self.uid = None
        self.data = None

        for k, v in kwargs.items():
            setattr(self, k, v)

    def __str__(self):
        if not self.target:
            return '%s %s' % (self.actor, self.verb)

        return '%s %s %s' % (self.actor, self.verb, self.target)

    def __repr__(self):
        try:
            u = six.text_type(self)
        except (UnicodeEncodeError, UnicodeDecodeError):
            u = '[Bad Unicode data]'
        return force_str('<%s: %s>' % (self.__class__.__name__, u))
