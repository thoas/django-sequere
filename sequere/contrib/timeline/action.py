import time

from sequere.utils import to_timestamp, from_timestamp


class Action(object):
    identifier = None
    depth = 1

    def __init__(self, actor, verb, target=None, date=None, **kwargs):
        self.actor = actor
        self.verb = verb
        self.target = target
        self.kwargs = kwargs.pop('kwargs', {})
        self.date = date

    def format_data(self, backend):
        result = {
            'actor': backend.make_uid(self.actor),
            'verb': self.verb,
        }

        if self.date:
            timestamp = to_timestamp(self.date)
        else:
            timestamp = int(time.time())

        result['timestamp'] = timestamp

        if self.target:
            result['target'] = backend.make_uid(self.target)

        return result

    @classmethod
    def from_data(cls, data, backend):
        pass
