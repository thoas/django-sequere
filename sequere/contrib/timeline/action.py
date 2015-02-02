from __future__ import unicode_literals

from django.utils.functional import memoize, cached_property
from django.utils.encoding import python_2_unicode_compatible
from django.utils import six
from django.utils.encoding import force_str
from django.utils import timezone as datetime

from sequere.utils import to_timestamp, from_timestamp
from sequere.registry import registry
from sequere.backends.redis.connection import manager as backend

from .exceptions import ActionDoesNotExist


def _get_actions():
    return dict((action.verb, action)
                for model_class in registry.values()
                for action in getattr(model_class, 'actions', []))


get_actions = memoize(_get_actions, {}, 0)


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

    @cached_property
    def actor_uid(self):
        return backend.make_uid(self.actor)

    @cached_property
    def target_uid(self):
        if self.target:
            return backend.make_uid(self.target)

        return None

    @property
    def timestamp(self):
        return to_timestamp(self.date)

    def format_data(self):
        result = {
            'actor': self.actor_uid,
            'verb': self.verb,
        }

        result['timestamp'] = self.timestamp

        if self.target:
            result['target'] = self.target_uid

        self.data = result

        return result

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

    @classmethod
    def from_data(cls, data):
        verb = data['verb']

        actions = get_actions()

        action_class = actions.get(verb, None)

        if action_class is None:
            raise ActionDoesNotExist('Action %s does not exist' % verb)

        for attr_name in ('actor', 'target', ):
            if data.get(attr_name, None):
                data[attr_name] = backend.get_from_uid(data[attr_name])
            else:
                data[attr_name] = None

        data['date'] = from_timestamp(float(data.pop('timestamp')))

        return action_class(**data)
