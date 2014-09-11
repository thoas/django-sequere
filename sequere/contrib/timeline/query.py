from sequere.query import QuerySetTransformer
from sequere.contrib.timeline.action import Action

from sequere.backends.redis.utils import get_key

from .connection import storage


class TimelineQuerySetTransformer(QuerySetTransformer):
    def __init__(self, client, count, key):
        super(TimelineQuerySetTransformer, self).__init__(client, count)

        self.keys = [key, ]
        self.order_by(False)

    def order_by(self, desc):
        self.desc = desc

        if desc:
            self.method = getattr(self.qs, 'zrevrangebyscore')

            self.pieces = self.keys + ['+inf', '-inf']
        else:
            self.method = getattr(self.qs, 'zrangebyscore')

            self.pieces = self.keys + ['-inf', '+inf']

        return self

    def transform(self, qs):
        scores = self.method(*self.pieces,
                             start=self.start,
                             num=self.stop - self.start,
                             withscores=True)

        results = []

        with self.qs.map() as pipe:
            for uid, score in scores:
                results.append(pipe.hgetall(get_key(storage.prefix, 'uid', uid)))

        return [Action.from_data(data)
                for data in results if data]
