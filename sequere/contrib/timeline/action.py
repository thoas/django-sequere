import time

from sequere.utils import to_timestamp, from_timestamp


class Action(object):
    depth = 1
    verb = None

    def __init__(self, actor, target=None, date=None, **kwargs):
        self.actor = actor
        self.target = target
        self.kwargs = kwargs.pop('kwargs', {})
        self.date = date
        self.uid = None
        self.actor_uid = None
        self.target_uid = None

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
        pass
