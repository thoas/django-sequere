django-sequere
==============

.. image:: https://secure.travis-ci.org/thoas/django-sequere.png?branch=master
    :alt: Build Status
    :target: http://travis-ci.org/thoas/django-sequere

A generic application to follow a resource with multiple backends (db, redis, etc.)

Compatibility
-------------

This library is compatible with:

- python2.6, django1.4
- python2.6, django1.5
- python2.7, django1.4
- python2.7, django1.5
- python3.3, django1.5

If I'm a liar, you can ping me.

Installation
------------

1. Either check out the package from GitHub_ or it pull from a release via PyPI ::

       pip install django-sequere


2. Add 'sequere' to your ``INSTALLED_APPS`` ::

       INSTALLED_APPS = (
           'sequere',
       )

Usage
-----

In Sequere any resources can follow any resources and vice versa.

Let's say you have two models: ::

    # models.py

    from django.db import models

    class User(models.Model):
        username = models.Charfield(max_length=150)


    class Project(models.Model):
        name = models.Charfield(max_length=150)


Now you to register them in sequere to identify them when a resource is following
another one. ::

    # sequere_registry.py

    from .models import Project, User

    import sequere

    sequere.register(User)
    sequere.register(Project)


Sequere uses the same concepts as `Django Admin`_, so if you have already used it,
you will not be lost.

Last step is to tell Sequere to autodiscover your registered models: ::

    # urls.py

    from django.conf.urls.defaults import patterns

    import sequere; sequere.autodiscover()


    urlpatterns = patterns(
        '',
        # Your urls here
    )


You can now use Sequere like any other application, let's play with it: ::

    In [1]: from sequere.models import (follow, unfollow, get_followings_count, is_following,
                                        get_followers_count, get_followers, get_followings)

    In [2]: from myapp.models import User, Project

    In [3]: user = User.objects.create(username='thoas')

    In [4]: project = Project.objects.create(name'La classe americaine')

    In [5]: follow(user, project)  # thoas will now follow "La classe americaine"

    In [6]: is_following(user, project)
    True

    In [7]: get_followers_count(project)
    1

    In [8]: get_followings_count(user)
    1

    In [9]: get_followers(user)
    []

    In [10]: get_followers(project)
    [(<User: thoas>, datetime.datetime(2013, 10, 25, 4, 41, 31, 612067))]

    In [11]: get_followings(user)
    [(<Project: La classe americaine, datetime.datetime(2013, 10, 25, 4, 41, 31, 612067))]


If you are as lazy as me to provide the original instance in each sequere calls, use ``SequereMixin``::

    # models.py

    from django.db import models

    from sequere.mixin import SequereMixin

    class User(SequereMixin, models.Model):
        username = models.Charfield(max_length=150)

    class Project(SequereMixin, models.Model):
        name = models.Charfield(max_length=150)

Now you can use calls directly from the instance: ::

    In [1]: from myapp.models import User, Project

    In [2]: user = User.objects.create(username='thoas')

    In [3]: project = Project.objects.create(name'La classe americaine')

    In [4]: user.follow(project)  # thoas will now follow "La classe americaine"

    In [5]: user.is_following(project)
    True

    In [6]: project.get_followers_count()
    1

    In [7]: user.get_followings_count()
    1

    In [8]: user.get_followers()
    []

    In [9]: project.get_followers()
    [(<User: thoas>, datetime.datetime(2013, 10, 25, 4, 41, 31, 612067))]

    In [10]: user.get_followings()
    [(<Project: La classe americaine, datetime.datetime(2013, 10, 25, 4, 41, 31, 612067))]


So much fun!


Backends
--------

sequere.backends.database.DatabaseBackend
.........................................

A database backend to store your follows in you favorite database using the Django's
ORM.


To use this backend you will have to add 'sequere.backends.database' to your ``INSTALLED_APPS`` ::

    INSTALLED_APPS = (
        'sequere',
        'sequere.backends.database',
    )

The follower will be identified by the couple (from_identifier, from_object_id)
and the following by (to_identifier, to_object_id).

Each identifiers are taken from the registry. For example, if you want to create
a custom identifier key from a model you can customized it like so: ::

    # sequere_registry.py

    from myapp.models import Project

    from sequere.base import ModelBase

    import sequere


    class ProjectSequere(ModelBase):
        identifier = 'projet' # the french way ;)

    sequere.registry(Project, ProjectSequere)


sequere.backends.redis.RedisBackend
...................................

We are using exclusively `Sorted Sets`_ in this Redis implementation.

Create a uid for a new resource ::

    INCR sequere:global:uid    =>  1
    SET sequere:uid:{identifier}:{id} 1
    HMSET sequere:uid::{id} identifier {identifier} object_id {id}

Store followers count ::

    INCR sequere:uid:{to_uid}:followers:count => 1
    INCR sequere:uid:{to_uid}:followers:{from_identifier}:count => 1

Store followings count ::

    INCR sequere:uid:{from_uid}:followings:count => 1
    INCR sequere:uid:{from_uid}:followings:{to_identifier}:count => 1


Add a new follower ::

    ZADD sequere:uid:{to_uid}:followers {from_uid} {timestamp}
    ZADD sequere:uid:{to_uid}:followers:{from_identifier} {from_uid} {timestamp}

Add a new following ::

    ZADD sequere:uid:{from_uid}:followings {to_uid} {timestamp}
    ZADD sequere:uid:{from_uid}:followings{to_identifier} {to_uid} {timestamp}


Retrieve the followers uids ::

    ZRANGEBYSCORE sequere:uid:{uid}:followers -inf +inf

Retrieve the followings uids ::

    ZRANGEBYSCORE sequere:uid:{uid}:followings =inf +inf

With this implementation you can retrieve your followers ordered ::

    ZREVRANGEBYSCORE sequere:uid:{uid}:followers +inf -inf

sequere.backends.redis.RedisFallbackBackend
...........................................

If you want to store follows in Redis and in your database with asynchronous tasks,
this backend is for you.

To run asynchronous tasks, we are using `Celery`_ tasks.

To use this backend you will have to install both 'sequere.backends.database' and 'sequere.backends.redis' to your ``INSTALLED_APPS`` ::

    INSTALLED_APPS = (
        'sequere',
        'sequere.backends.database',
        'sequere.backends.redis',
    )


Configuration
-------------

``SEQUERE_BACKEND_CLASS``
.........................

The backend used to store follows

``SEQUERE_REDIS_CONNECTION``
............................

A dictionary of parameters to pass to the to Redis client, e.g.: ::

    SEQUERE_REDIS_CONNECTION = {
        'host': 'localhost',
        'port': 6379,
        'db': 0,
    }

Alternatively you can use a URL to do the same: ::

    SEQUERE_REDIS_CONNECTION = 'redis://username:password@localhost:6379/0'


``SEQUERE_REDIS_CONNECTION_CLASS``
..................................

An (optional) dotted import path to a connection to use, e.g.: ::

    SEQUERE_REDIS_CONNECTION_CLASS = 'myproject.myapp.mockup.Connection'

``SEQUERE_REDIS_PREFIX``
........................

The (optional) prefix to be used for the key when storing in the Redis database. Defaults to 'sequere:'. E.g.: ::

    SEQUERE_REDIS_PREFIX = 'sequere:myproject:'


Resources
---------

- `haplocheirus`_: a Redis backed storage engine for timelines written in Scala
- `Case study from Redis documentation`_: write a twitter clone
- `Amico`_: relationships backed by Redis


.. _GitHub: https://github.com/thoas/django-sequere
.. _Django Admin: https://docs.djangoproject.com/en/dev/ref/contrib/admin/
.. _Sorted Sets: http://redis.io/commands#sorted_set
.. _haplocheirus: https://github.com/twitter/haplocheirus
.. _Case study from Redis documentation: http://redis.io/topics/twitter-clone
.. _Amico: https://github.com/agoragames/amico
.. _Celery: http://www.celeryproject.org/
