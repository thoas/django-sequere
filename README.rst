django-sequere
==============

.. image:: https://secure.travis-ci.org/thoas/django-sequere.png?branch=master
    :alt: Build Status
    :target: http://travis-ci.org/thoas/django-sequere

A Django application to implement a follow system and a timeline using multiple backends (db, redis, etc.).

The timeline engine can be found in ``sequere.contrib.timeline``.

Installation
------------

1. Either check out the package from GitHub_ or it pull from a release via PyPI ::

       pip install django-sequere


2. Add ``sequere`` to your ``INSTALLED_APPS``

.. code-block:: python

       INSTALLED_APPS = (
           'sequere',
       )

Usage
-----

In Sequere any resources can follow any resources and vice versa.

Let's say you have two models:

.. code-block:: python

    # models.py

    from django.db import models

    class User(models.Model):
        username = models.CharField(max_length=150)


    class Project(models.Model):
        name = models.CharField(max_length=150)


Now you to register them in sequere to identify them when a resource is following
another one.

.. code-block:: python

    # sequere_registry.py

    from .models import Project, User

    import sequere

    sequere.register(User)
    sequere.register(Project)


Sequere uses the same concepts as `Django Admin`_, so if you have already used it,
you will not be lost.

You can now use Sequere like any other application, let's play with it:

.. code-block:: python

    >>> from sequere.models import (follow, unfollow, get_followings_count, is_following,
                                        get_followers_count, get_followers, get_followings)

    >>> from myapp.models import User, Project

    >>> user = User.objects.create(username='thoas')

    >>> project = Project.objects.create(name='La classe americaine')

    >>> follow(user, project)  # thoas will now follow "La classe americaine"

    >>> is_following(user, project)
    True

    >>> get_followers_count(project)
    1

    >>> get_followings_count(user)
    1

    >>> get_followers(user)
    []

    >>> get_followers(project)
    [(<User: thoas>, datetime.datetime(2013, 10, 25, 4, 41, 31, 612067))]

    >>> get_followings(user)
    [(<Project: La classe americaine, datetime.datetime(2013, 10, 25, 4, 41, 31, 612067))]


If you are as lazy as me to provide the original instance in each sequere calls, use ``SequereMixin``

.. code-block:: python

    # models.py

    from django.db import models

    from sequere.mixin import SequereMixin

    class User(SequereMixin, models.Model):
        username = models.Charfield(max_length=150)

    class Project(SequereMixin, models.Model):
        name = models.Charfield(max_length=150)

Now you can use calls directly from the instance:

.. code-block:: python

    >>> from myapp.models import User, Project

    >>> user = User.objects.create(username='thoas')

    >>> project = Project.objects.create(name'La classe americaine')

    >>> user.follow(project)  # thoas will now follow "La classe americaine"

    >>> user.is_following(project)
    True

    >>> project.get_followers_count()
    1

    >>> user.get_followings_count()
    1

    >>> user.get_followers()
    []

    >>> project.get_followers()
    [(<User: thoas>, datetime.datetime(2013, 10, 25, 4, 41, 31, 612067))]

    >>> user.get_followings()
    [(<Project: La classe americaine, datetime.datetime(2013, 10, 25, 4, 41, 31, 612067))]


So much fun!


Backends
--------

sequere.backends.database.DatabaseBackend
.........................................

A database backend to store your follows in you favorite database using the Django's
ORM.


To use this backend you will have to add ``sequere.backends.database`` to your ``INSTALLED_APPS``

.. code-block:: python

    INSTALLED_APPS = (
        'sequere',
        'sequere.backends.database',
    )

The follower will be identified by the couple (from_identifier, from_object_id)
and the following by (to_identifier, to_object_id).

Each identifiers are taken from the registry. For example, if you want to create
a custom identifier key from a model you can customized it like so:

.. code-block:: python

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

Add ``sequere.contrib.timeline`` to your ``INSTALLED_APPS``

.. code-block:: python

       INSTALLED_APPS = (
           'sequere.contrib.timeline',
       )

``sequere.contrib.timeline`` requires `celery`_ to work properly,
so you will have to install it.

Usage
.....

You have to register your actions based on your resources, for example

.. code-block:: python

    # sequere_registry.py

    from .models import Project, User

    from sequere.contrib.timeline import Action
    from sequere import register
    from sequere.base import ModelBase


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


Now we have registered our actions we can play with the timeline API

.. code-block:: python

    >>> from sequere.models import (follow, unfollow)

    >>> from sequere.contrib.timeline import Timeline

    >>> from myapp.models import User, Project

    >>> from myapp.sequere_registry import JoinAction, LikeAction

    >>> thoas = User.objects.create(username='thoas')

    >>> project = Project.objects.create(name='La classe americaine')

    >>> timeline = Timeline(thoas) # create a timeline

    >>> timeline.save(JoinAction(actor=thoas)) # save the action in the timeline

    >>> timeline.get_private()
    [<JoinAction: thoas join>]

    >>>: timeline.get_public()
    [<JoinAction: thoas join>]

When the resource is the actor of its own action then we push the action both
in **private** and **public** timelines.

Now we have to test the system with the follow process

.. code-block:: python

    >>> newbie = User.objects.create(username='newbie')

    >>> follow(newbie, thoas) # newbie is now following thoas

    >>> Timeline(newbie).get_private() # thoas actions now appear in the private timeline of newbie
    [<JoinAction: thoas join>]

    >>> Timeline(newbie).get_public()
    []

When **A** is following **B** we copy actions of **B** in the private
timeline of **A**, `celery`_ is needed to handle these asynchronous tasks.

.. code-block:: python

    >>> unfollow(newbie, thoas)

    >>> Timeline(newbie).get_private()
    []

When **A** is unfollowing **B** we delete the actions of **B** in the private
timeline of **A**.

As you may have noticed the ``JoinAction`` is an action which does not need a target,
some actions will need target, ``sequere.contrib.timeline`` provides a quick way
to query actions for a specific target.

.. code-block:: python

    >>> timeline = Timeline(thoas)

    >>> timeline.save(LikeAction(actor=thoas, target=project))

    >>> timeline.get_private()
    [<JoinAction: thoas join>, <LikeAction: thoas like La classe americaine>]

    >>> timeline.get_private(target=Project) # only retrieve actions with Project resource as target
    [<LikeAction: thoas like La classe americaine>]

    >>> timeline.get_private(target='project') # only retrieve actions with 'project' identifier as target
    [<LikeAction: thoas like La classe americaine>]

Configuration
-------------

``SEQUERE_BACKEND_CLASS``
.........................

The backend used to store follows

Defaults to ``sequere.backends.database.DatabaseBackend``.

``SEQUERE_REDIS_CONNECTION``
............................

A dictionary of parameters to pass to the to Redis client, e.g.:

.. code-block:: python

    SEQUERE_REDIS_CONNECTION = {
        'host': 'localhost',
        'port': 6379,
        'db': 0,
    }

Alternatively you can use a URL to do the same:

.. code-block:: python

    SEQUERE_REDIS_CONNECTION = 'redis://username:password@localhost:6379/0'


``SEQUERE_REDIS_CONNECTION_CLASS``
..................................

An (optional) dotted import path to a connection to use, e.g.:

.. code-block:: python

    SEQUERE_REDIS_CONNECTION_CLASS = 'myproject.myapp.mockup.Connection'

``SEQUERE_REDIS_PREFIX``
........................

The (optional) prefix to be used for the key when storing in the Redis database.

.. code-block:: python

    SEQUERE_REDIS_PREFIX = 'sequere:myproject:'

Defaults to ``sequere:``.

``SEQUERE_TIMELINE_CONNECTION_CLASS``
.....................................

An (optional) dotted import path to a connection to use, e.g.:

.. code-block:: python

    SEQUERE_TIMELINE_CONNECTION_CLASS = 'myproject.myapp.mockup.Connection'

``SEQUERE_TIMELINE_REDIS_CONNECTION``
.....................................

A dictionary of parameters to pass to the to Redis client, e.g.:

.. code-block:: python

    SEQUERE_TIMELINE_REDIS_CONNECTION = {
        'host': 'localhost',
        'port': 6379,
        'db': 0,
    }

Alternatively you can use a URL to do the same:

.. code-block:: python

    SEQUERE_TIMELINE_REDIS_CONNECTION = 'redis://username:password@localhost:6379/0'

``SEQUERE_TIMELINE_REDIS_PREFIX``
.................................

The (optional) prefix to be used for the key when storing in the Redis database.

.. code-block:: python

    SEQUERE_TIMELINE_REDIS_PREFIX = 'sequere:myproject:timeline'

Defaults to ``sequere:timeline``.


Resources
---------

- `haplocheirus`_: a Redis backed storage engine for timelines written in Scala
- `Case study from Redis documentation`_: write a twitter clone
- `Amico`_: relationships backed by Redis
- `django-constance`_: a multi-backends settings management application


.. _GitHub: https://github.com/thoas/django-sequere
.. _redis-py: https://github.com/andymccurdy/redis-py
.. _celery: http://www.celeryproject.org/
.. _Django Admin: https://docs.djangoproject.com/en/dev/ref/contrib/admin/
.. _Sorted Sets: http://redis.io/commands#sorted_set
.. _haplocheirus: https://github.com/twitter/haplocheirus
.. _Case study from Redis documentation: http://redis.io/topics/twitter-clone
.. _Amico: https://github.com/agoragames/amico
.. _Celery: http://www.celeryproject.org/
.. _django-constance: https://github.com/comoga/django-constance
