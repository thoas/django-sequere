# -*- coding: utf-8 -*-
from datetime import datetime

import six
import time

from django.core import exceptions
from django.core.exceptions import ImproperlyConfigured
from django.utils.importlib import import_module
from django.conf import settings
from django.utils import timezone


CLASS_PATH_ERROR = 'django-sequere is unable to interpret settings value for %s. '\
                   '%s should be in the form of a tupple: '\
                   '(\'path.to.models.Class\', \'app_label\').'


def load_class(class_path, setting_name=None):
    """
    Loads a class given a class_path. The setting value may be a string or a
    tuple.

    The setting_name parameter is only there for pretty error output, and
    therefore is optional
    """
    if not isinstance(class_path, six.string_types):
        try:
            class_path, app_label = class_path
        except:
            if setting_name:
                raise exceptions.ImproperlyConfigured(CLASS_PATH_ERROR % (
                    setting_name, setting_name))
            else:
                raise exceptions.ImproperlyConfigured(CLASS_PATH_ERROR % (
                    'this setting', 'It'))

    try:
        class_module, class_name = class_path.rsplit('.', 1)
    except ValueError:
        if setting_name:
            txt = '%s isn\'t a valid module. Check your %s setting' % (
                class_path, setting_name)
        else:
            txt = '%s isn\'t a valid module.' % class_path
        raise exceptions.ImproperlyConfigured(txt)

    try:
        mod = import_module(class_module)
    except ImportError as e:
        if setting_name:
            txt = 'Error importing backend %s: "%s". Check your %s setting' % (
                class_module, e, setting_name)
        else:
            txt = 'Error importing backend %s: "%s".' % (class_module, e)

        raise exceptions.ImproperlyConfigured(txt)

    try:
        clazz = getattr(mod, class_name)
    except AttributeError:
        if setting_name:
            txt = ('Backend module "%s" does not define a "%s" class. Check'
                   ' your %s setting' % (class_module, class_name,
                                         setting_name))
        else:
            txt = 'Backend module "%s" does not define a "%s" class.' % (
                class_module, class_name)
        raise exceptions.ImproperlyConfigured(txt)
    return clazz


def from_timestamp(timestamp):
    if settings.USE_TZ:
        import pytz

        local_tz = timezone.get_default_timezone()

        utc_dt = datetime.utcfromtimestamp(timestamp).replace(tzinfo=pytz.utc)

        return local_tz.normalize(utc_dt.astimezone(local_tz))

    return datetime.fromtimestamp(timestamp)


def to_timestamp(dt):
    return int(time.mktime(dt.timetuple()))


def get_client(connection, connection_class=None):
    if connection_class:
        client = load_class(connection_class)()
    else:
        try:
            import redis
        except ImportError:
            raise ImproperlyConfigured(
                "The Redis backend requires redis-py to be installed.")
        if isinstance(connection, six.string_types):
            client = redis.from_url(connection)
        else:
            # see https://github.com/andymccurdy/redis-py/issues/463#issuecomment-41229918
            connection['decode_responses'] = True

            client = redis.StrictRedis(**connection)

    return client
