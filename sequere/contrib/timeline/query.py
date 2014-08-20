from sequere.query import QuerySetTransformer
from sequere.contrib.timeline.action import Action

from sequere.backends.redis.utils import get_key


class TimelineQuerySetTransformer(QuerySetTransformer):
    def __init__(self, client, count, key, prefix, manager=None):
        super(TimelineQuerySetTransformer, self).__init__(client, count)

        self.keys = [key, ]
        self.order_by(False)
        self.prefix = prefix

        self.manager = manager or client

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

        with self.qs.pipeline() as pipe:
            for uid, score in scores:
                pipe.hgetall(get_key(self.prefix, 'uid', uid))

            return [Action.from_data(data, self.manager)
                    for data in pipe.execute()]
