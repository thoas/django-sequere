from collections import OrderedDict

from sequere.query import QuerySetTransformer
from sequere import utils


class RedisQuerySetTransformer(QuerySetTransformer):
    def __init__(self, manager, count, key):
        super(RedisQuerySetTransformer, self).__init__(manager.client, count)

        self.manager = manager
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
        start = self.start or 0
        stop = self.stop or -1

        scores = self.method(*self.pieces,
                             start=start,
                             num=stop - start,
                             withscores=True)

        scores = OrderedDict(scores)

        objects = self.manager.get_from_uid_list(scores.keys())

        return [(objects[i], utils.from_timestamp(value[1]))
                for i, value in enumerate(scores.items())]
