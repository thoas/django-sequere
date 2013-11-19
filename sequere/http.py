# -*- coding: utf-8 -*-
from django.http import HttpResponse

try:
    import simplejson as json
except ImportError:
    import json  # NOQA


class JSONResponse(HttpResponse):
    """Represent a HTTP response with a Content-Type of 'application/json'.

    This subclass of `django.http.HttpResponse` will remove most of the
    necessary boilerplate in returning JSON responses from views. The object
    to be serialized is passed in as the only positional argument, and the
    other keyword arguments are as usual for `HttpResponse`, with one
    exception: an optional 'callback' argument may be given which will wrap
    the response with a JavaScript function call to the given function name.
    """

    def __init__(self, obj, indent=0, cls=None, **kwargs):
        params = {
            'indent': indent
        }

        if cls:
            params['cls'] = cls

        kwargs['content'] = json.dumps(obj, **params)

        if 'callback' in kwargs:
            callback = kwargs.pop('callback')
            if callback:
                kwargs['content'] = u'%s(%s);' % (callback, kwargs['content'])
                kwargs.setdefault('content_type', 'application/javascript')

        kwargs.setdefault('content_type', 'application/json')
        super(JSONResponse, self).__init__(**kwargs)
