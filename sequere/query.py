import six

REPR_OUTPUT_SIZE = 20


class QuerySetTransformer(object):
    def __init__(self, qs, count):
        self.qs = qs
        self._count = count

    def set_limits(self, start, stop):
        self.start = start
        self.stop = stop

    def __len__(self):
        return self._count

    def __getitem__(self, k):
        if not isinstance(k, (slice,) + six.integer_types):
            raise TypeError

        assert ((not isinstance(k, slice) and (k >= 0))
                or (isinstance(k, slice) and (k.start is None or k.start >= 0)
                    and (k.stop is None or k.stop >= 0))), "Negative indexing is not supported."

        if isinstance(k, slice):
            if k.start is not None:
                start = int(k.start)
            else:
                start = None
            if k.stop is not None:
                stop = int(k.stop)
            else:
                stop = None

            self.set_limits(start, stop)

            return k.step and list(self.transform(self.qs))[::k.step] or self.transform(self.qs)

    def transform(self, qs):
        raise NotImplementedError

    def count(self):
        return self._count

    def all(self):
        self.set_limits(0, self.count())
        return self.transform(self.qs)

    def __repr__(self):
        data = list(self[:REPR_OUTPUT_SIZE + 1])
        if len(data) > REPR_OUTPUT_SIZE:
            data[-1] = "...(remaining elements truncated)..."
        return repr(data)
