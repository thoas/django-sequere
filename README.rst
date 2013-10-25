django-sequere
==============

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

Last step is to tell Sequere to autodiscover your registered models ::

    # urls.py

    from django.conf.urls.defaults import patterns

    import sequere; sequere.autodiscover()


    urlpatterns = patterns(
        '',
        # Your urls here
    )


You can now use Sequere like any other application, let's play with it ::

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

    In [9]: get_followers(project)
    [(<User: thoas>, datetime.datetime(2013, 10, 25, 4, 41, 31, 612067))]

    In [10]: get_followings(user)
    [(<Project: La classe americaine, datetime.datetime(2013, 10, 25, 4, 41, 31, 612067))]


Backends
--------

sequere.backends.simple.SimpleBackend
.....................................

A simple backend to store your follows in you favorite database using the Django's
ORM.

The follower will be identified by a couple (from_identifier, from_object_id)
and the following will be identified by the couple (to_identifier, to_object_id).

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

coming soon


Configuration
-------------

``SEQUERE_BACKEND_CLASS``
.........................

The backend used to store follows


.. _GitHub: https://github.com/thoas/django-sequere
.. _Django Admin: https://docs.djangoproject.com/en/dev/ref/contrib/admin/
