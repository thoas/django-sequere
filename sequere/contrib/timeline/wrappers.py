from .query import RedisTimelineQuerySetTransformer, NydusTimelineQuerySetTransformer


class CallProxy(object):
    """
    Handles routing function calls to the proper connection.
    """
    def __init__(self, cluster, path):
        self.__cluster = cluster
        self.__path = path

    def __call__(self, *args, **kwargs):
        return getattr(self.__cluster, self.__path)(*args, **kwargs)

    def __getattr__(self, name):
        return CallProxy(self.__cluster, self.__path + '.' + name)


class Wrapper(object):
    def __init__(self, client):
        self.client = client

    def __getattr__(self, name):
        return CallProxy(self.client, name)


class PipelineContextManager(object):
    def __init__(self, pipeline, *args, **kwargs):
        self.pipeline = pipeline

    def __enter__(self):
        return self.pipeline

    def __exit__(self, exc_type, exc_value, tb):
        self.pipeline.execute()


class RedisWrapper(Wrapper):
    queryset_class = RedisTimelineQuerySetTransformer

    def map(self, *args, **kwargs):
        return PipelineContextManager(self.client.pipeline(), *args, **kwargs)


class NydusWrapper(Wrapper):
    queryset_class = NydusTimelineQuerySetTransformer
