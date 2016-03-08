from sequere.query import QuerySetTransformer
from sequere.contrib.timeline.action import Action

from sequere.backends.redis.utils import get_key

from .exceptions import ActionInvalid
from .utils import logger


class TimelineQuerySetTransformer(QuerySetTransformer):
    def __init__(self, client, count, key, prefix=None):
        super(TimelineQuerySetTransformer, self).__init__(client, count)

        self.keys = [key, ]
        self.order_by(False)
        self.prefix = prefix or ''

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

        return self._transform(scores)

    def _transform(self, scores):
        raise NotImplementedError


class RedisTimelineQuerySetTransformer(TimelineQuerySetTransformer):
    def _transform(self, scores):
        with self.qs.pipeline() as pipe:
            for uid, score in scores:
                pipe.hgetall(get_key(self.prefix, 'uid', uid))

            results = pipe.execute()

            actions = []

            for data in results:
                if not data:
                    continue

                try:
                    action = Action.from_data(data)
                except ActionInvalid as e:
                    logger.exception(e)
                else:
                    actions.append(action)

            return actions
