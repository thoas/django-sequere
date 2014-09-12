django-sequere
==============

.. image:: https://secure.travis-ci.org/thoas/django-sequere.png?branch=master
    :alt: Build Status
    :target: http://travis-ci.org/thoas/django-sequere

A generic application to follow a resource with multiple backends (db, redis, etc.).

A timeline engine can be also found in ``sequere.contrib.timeline``.

Compatibility
-------------

This library is compatible with:

- python2.6, django1.5
- python2.6, django1.6
- python2.7, django1.4
- python2.7, django1.5
- python2.7, django1.6
- python2.7, django1.7
- python3.3, django1.5
- python3.3, django1.6
- python3.3, django1.7
- python3.4, django1.5
- python3.4, django1.6
- python3.4, django1.7

If I'm a liar, you can ping me.

Installation
------------

1. Either check out the package from GitHub_ or it pull from a release via PyPI ::

       pip install django-sequere


2. Add ``sequere`` to your ``INSTALLED_APPS`` ::

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

You can now use Sequere like any other application, let's play with it: ::

    In [1]: from sequere.models import (follow, unfollow, get_followings_count, is_following,
                                        get_followers_count, get_followers, get_followings)

    In [2]: from myapp.models import User, Project

    In [3]: user = User.objects.create(username='thoas')

    In [4]: project = Project.objects.create(name='La classe americaine')

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


To use this backend you will have to add ``sequere.backends.database`` to your ``INSTALLED_APPS`` ::

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


Timeline
--------

The timeline engine is directly based on ``sequere`` resources system.

Concept
.......

A ``Timeline`` is basically a list of ``Action``.

An ``Action`` is represented by:

- ``actor`` which is the actor of the action
- ``verb`` which is the action name
- ``target`` which is the target of the action (not required)
- ``date`` which is the date when the action has been done

Installation
............

You have to follow installation instructions of ``sequere`` first before installing
``sequere.contrib.timeline``.

Add ``sequere.contrib.timeline`` to your ``INSTALLED_APPS`` ::

       INSTALLED_APPS = (
           'sequere.contrib.timeline',
       )

``sequere.contrib.timeline`` requires `celery`_ to work properly,
so you will have to install it.

Usage
.....

You have to register your actions based on your resources, for example ::

    # sequere_registry.py

    from .models import Project, User

    from sequere.contrib.timeline import Action
    from sequere import register
    from sequere.base import Modelbase


    # actions
    class JoinAction(Action):
        verb = 'join'


    class LikeAction(Action):
        verb = 'like'

    # resources
    class ProjectSequere(ModelBase):
        identifier = 'project'

    class UserSequere(ModelBase):
        identifier = 'user'

        actions = (JoinAction, LikeAction, )

    # register resources
    register(User, UserSequere)
    register(Project, ProjectSequere)


Now we have registered our actions we can play with the timeline API ::

    In [1]: from sequere.models import (follow, unfollow)

    In [2]: from sequere.contrib.timeline import Timeline

    In [3]: from myapp.models import User, Project

    In [4]: from myapp.sequere_registry import JoinAction, LikeAction

    In [5]: thoas = User.objects.create(username='thoas')

    In [6]: project = Project.objects.create(name='La classe americaine')

    In [7]: timeline = Timeline(thoas) # create a timeline

    In [8]: timeline.save(JoinAction(actor=thoas)) # save the action in the timeline

    In [9]: timeline.get_private()
    [<JoinAction: thoas join>]

    In [10]: timeline.get_public()
    [<JoinAction: thoas join>]

When the resource is the actor of its own action then we push the action both
in **private** and **public** timelines.

Now we have to test the system with the follow process ::

    In [11]: newbie = User.objects.create(username='newbie')

    In [12]: follow(newbie, thoas) # newbie is now following thoas

    In [13]: Timeline(newbie).get_private() # thoas actions now appear in the private timeline of newbie
    [<JoinAction: thoas join>]

    In [14]: Timeline(newbie).get_public()
    []

When **A** is following **B** we copy actions of **B** in the private
timeline of **A**, `celery`_ is needed to handle these asynchronous tasks. ::

    In [15]: unfollow(newbie, thoas)

    In [16]: Timeline(newbie).get_private()
    []

When **A** is unfollowing **B** we delete the actions of **B** in the private
timeline of **A**.

As you may have noticed the ``JoinAction`` is an action which does not need a target,
some actions will need target, ``sequere.contrib.timeline`` provides a quick way
to query actions for a specific target. ::

    In [17]: timeline = Timeline(thoas)

    In [18]: timeline.save(LikeAction(actor=thoas, target=project))

    In [19]: timeline.get_private()
    [<JoinAction: thoas join>, <LikeAction: thoas like La classe americaine>]

    In [20]: timeline.get_private(target=Project) # only retrieve actions with Project resource as target
    [<LikeAction: thoas like La classe americaine>]

    In [21]: timeline.get_private(target='project') # only retrieve actions with 'project' identifier as target
    [<LikeAction: thoas like La classe americaine>]

Configuration
-------------

``SEQUERE_BACKEND_CLASS``
.........................

The backend used to store follows

Defaults to ``sequere.backends.database.Databasebackend``.

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

The (optional) prefix to be used for the key when storing in the Redis database. ::

    SEQUERE_REDIS_PREFIX = 'sequere:myproject:'

Defaults to ``sequere:``.

``SEQUERE_TIMELINE_CONNECTION_CLASS``
.....................................

An (optional) dotted import path to a connection to use, e.g.: ::

    SEQUERE_TIMELINE_CONNECTION_CLASS = 'myproject.myapp.mockup.Connection'

``SEQUERE_TIMELINE_REDIS_CONNECTION``
.....................................

A dictionary of parameters to pass to the to Redis client, e.g.: ::

    SEQUERE_TIMELINE_REDIS_CONNECTION = {
        'host': 'localhost',
        'port': 6379,
        'db': 0,
    }

Alternatively you can use a URL to do the same: ::

    SEQUERE_TIMELINE_REDIS_CONNECTION = 'redis://username:password@localhost:6379/0'

``SEQUERE_TIMELINE_REDIS_PREFIX``
.................................

The (optional) prefix to be used for the key when storing in the Redis database. ::

    SEQUERE_TIMELINE_REDIS_PREFIX = 'sequere:myproject:timeline'

Defaults to ``sequere:timeline``.

``SEQUERE_TIMELINE_NYDUS_CONNECTION``
.....................................

`nydus`_ can be used to scale like a pro. ::

    SEQUERE_TIMELINE_NYDUS_CONNECTION = {
        'backend': 'nydus.db.backends.redis.Redis',
        'router': 'nydus.db.routers.keyvalue.PartitionRouter',
        'hosts': {
            0: {'db': 0},
            1: {'db': 1},
            2: {'db': 2},
        }
    }

``sequere.contrib.timeline`` supports both `redis-py`_ and `nydus`_.

If this settings is provided in your Django project then `nydus`_ will be needed
as an additional dependency.


Resources
---------

- `haplocheirus`_: a Redis backed storage engine for timelines written in Scala
- `Case study from Redis documentation`_: write a twitter clone
- `Amico`_: relationships backed by Redis
- `django-constance`_: a multi-backends settings management application


.. _GitHub: https://github.com/thoas/django-sequere
.. _nydus: https://github.com/disqus/nydus
.. _redis-py: https://github.com/andymccurdy/redis-py
.. _celery: http://www.celeryproject.org/
.. _Django Admin: https://docs.djangoproject.com/en/dev/ref/contrib/admin/
.. _Sorted Sets: http://redis.io/commands#sorted_set
.. _haplocheirus: https://github.com/twitter/haplocheirus
.. _Case study from Redis documentation: http://redis.io/topics/twitter-clone
.. _Amico: https://github.com/agoragames/amico
.. _Celery: http://www.celeryproject.org/
.. _django-constance: https://github.com/comoga/django-constance
