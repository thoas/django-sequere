django-sequere
==============

.. image:: https://secure.travis-ci.org/thoas/django-sequere.png?branch=master
    :alt: Build Status
    :target: http://travis-ci.org/thoas/django-sequere

A generic application to follow a resource with multiple backends (db, redis, etc.)

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

sequere.backends.simple.SimpleBackend
.....................................

A simple backend to store your follows in you favorite database using the Django's
ORM.

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

Store followers count ::

    INCR sequere:uid:{uid}:followers:count => 1

Store followings count ::

    INCR sequere:uid:{uid}:followings:count => 1


Add a new follower ::

    ZADD sequere:uid:{uid}:followers {uid} {timestamp}

Add a new following ::

    ZADD sequere:uid:{uid}:followings {uid} {timestamp}


Retrieve the followers uids ::

    ZRANGE sequere:uid:{uid}:followers 0 -1

Retrieve the followings uids ::

    ZRANGE sequere:uid:{uid}:followings 0 -1

With this implementation you can retrieve your followers ordered ::

    ZREVRANGE sequere:uid:{uid}:followers 0 -1


Configuration
-------------

``SEQUERE_BACKEND_CLASS``
.........................

The backend used to store follows


Resources
---------

`haplocheirus`_: a Redis backed storage engine for timelines written in Scala
`Case study from Redis documentation`_: write a twitter clone
`Amico`_: relationships backed by Redis


.. _GitHub: https://github.com/thoas/django-sequere
.. _Django Admin: https://docs.djangoproject.com/en/dev/ref/contrib/admin/
.. _Sorted Sets: http://redis.io/commands#sorted_set
.. _haplocheirus: https://github.com/twitter/haplocheirus
.. _Case study from Redis documentation: http://redis.io/topics/twitter-clone
.. _Amico: https://github.com/agoragames/amico
