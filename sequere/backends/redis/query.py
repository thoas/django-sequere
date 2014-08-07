from operator import itemgetter
from collections import defaultdict

from sequere.query import QuerySetTransformer
from sequere.registry import registry
from sequere import utils


class RedisQuerySetTransformer(QuerySetTransformer):
    def __init__(self, client, count, key, prefix):
        super(RedisQuerySetTransformer, self).__init__(client, count)

        self.key = key
        self.keys = [key, ]
        self.order_by(False)
        self.prefix = prefix

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
                pipe.hgetall('%suid:%s' % (self.prefix, uid))

            identifier_ids = defaultdict(list)

            orders = {}

            for i, value in enumerate(pipe.execute()):
                identifier_ids[value['identifier']].append(value['object_id'])
                orders[int(value['object_id'])] = utils.from_timestamp(scores[i][1])

            for identifier, ids in identifier_ids.iteritems():
                klass = registry.identifiers.get(identifier)

                results = klass.objects.filter(pk__in=ids)

                for result in results:
                    created = orders[result.pk]

                    del orders[result.pk]

                    orders[result] = created

            return sorted(orders.items(),
                          key=itemgetter(1),
                          reverse=self.desc)
