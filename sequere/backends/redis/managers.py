import six

from collections import defaultdict

from sequere.registry import registry

from .utils import get_key


class Manager(object):
    def __init__(self, client, prefix=None):
        self.client = client
        self.prefix = prefix or ''

    def add_prefix(self, key):
        return get_key(self.prefix, key)

    def make_uid(self, data):
        uid = self.client.incr(self.add_prefix(get_key('global', 'uid')))

        data['uid'] = uid

        key = self.add_prefix(get_key('uid', uid))

        self.client.hmset(key, data)

        return uid

    def get_data_from_uid(self, uid):
        key = self.add_prefix(get_key('uid', uid))

        return self.client.hgetall(key)

    def clear(self):
        self.client.flushdb()


class InstanceManager(Manager):
    def make_uid(self, instance):
        uid = self.get_uid(instance)

        if not uid:
            identifier = registry.get_identifier(instance)

            uid = super(InstanceManager, self).make_uid({
                'identifier': identifier,
                'object_id': instance.pk
            })

            self.client.set(self.make_uid_key(instance), uid)

        return uid

    def make_uid_key(self, instance):
        identifier = registry.get_identifier(instance)

        object_id = instance.pk

        return self.add_prefix(get_key('uid', identifier, object_id))

    def get_from_uid_list(self, uid_list):
        with self.client.pipeline() as pipe:
            for uid in uid_list:
                pipe.hgetall(self.add_prefix(get_key('uid', uid)))

            identifier_ids = defaultdict(dict)

            results = pipe.execute()

            for i, value in enumerate(results):
                identifier_ids[value['identifier']][int(value['object_id'])] = None

            for identifier, objects in six.iteritems(identifier_ids):
                klass = registry.identifiers.get(identifier)

                for result in klass.objects.filter(pk__in=objects.keys()):
                    identifier_ids[identifier][result.pk] = result

            results = [identifier_ids[value['identifier']][int(value['object_id'])]
                       for i, value in enumerate(results)]

            return results

    def get_from_uid(self, uid):
        data = self.get_data_from_uid(int(uid))

        klass = registry.identifiers.get(data['identifier'])

        try:
            return klass.objects.get(pk=data['object_id'])
        except klass.DoesNotExist:
            return None

    def get_uid(self, instance):
        return self.client.get(self.make_uid_key(instance))
