import time

from django.utils.functional import memoize

from sequere.utils import to_timestamp, from_timestamp
from sequere.registry import registry

from .exceptions import ActionDoesNotExist


def _get_actions():
    return dict((action.verb, action)
                for model_class in registry.values()
                for action in getattr(model_class, 'actions', []))


get_actions = memoize(_get_actions, {}, 0)


class Action(object):
    verb = None

    def __init__(self, actor, target=None, date=None, **kwargs):
        self.actor = actor
        self.target = target
        self.kwargs = kwargs.pop('kwargs', {})
        self.date = date
        self.uid = None
        self.actor_uid = None
        self.target_uid = None

        for k, v in kwargs.items():
            setattr(self, k, v)

    def format_data(self, backend):
        self.actor_uid = backend.make_uid(self.actor)

        result = {
            'actor': self.actor_uid,
            'verb': self.verb,
        }

        if self.date:
            timestamp = to_timestamp(self.date)
        else:
            timestamp = int(time.time())

        result['timestamp'] = timestamp

        if self.target:
            self.target_uid = backend.make_uid(self.target)

            result['target'] = self.target_uid

        return result

    @classmethod
    def from_data(cls, data, backend):
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

        data['date'] = from_timestamp(float(data['timestamp']))

        return action_class(**data)
