from .celery import app as celery_app  # noqa

from django.test.utils import override_settings
from django.test import TestCase
from django.core.urlresolvers import reverse

from datetime import datetime, timedelta

from exam.decorators import fixture
from exam.cases import Exam

from .models import Project

from sequere import settings
from sequere.registry import registry
from sequere.http import json
from sequere.backends.database.models import Follow

import mock


class FixturesMixin(Exam):
    @fixture
    def user(self):
        from ..compat import User

        return User.objects.create_user(username='thoas',
                                        email='florent@ulule.com',
                                        password='$ecret')

    @fixture
    def newbie(self):
        from ..compat import User

        return User.objects.create_user(username='newbie',
                                        email='newbie@ulule.com',
                                        password='$ecret')

    @fixture
    def project(self):
        return Project.objects.create(name='My super project')


class BaseBackendTests(FixturesMixin):
    def test_follow(self):
        from ..models import follow, get_followings_count, get_followers_count

        follow(self.user, self.project)

        self.assertEqual(get_followings_count(self.user), 1)

        self.assertEqual(get_followings_count(self.user, registry.get_identifier(self.project)), 1)

        self.assertEqual(get_followers_count(self.project), 1)

        self.assertEqual(get_followers_count(self.project, registry.get_identifier(self.user)), 1)

    def test_unfollow(self):
        from ..models import (follow, get_followings_count,
                              get_followers_count, unfollow)

        follow(self.user, self.project)

        unfollow(self.user, self.project)

        self.assertEqual(get_followings_count(self.user), 0)

        self.assertEqual(get_followings_count(self.user, registry.get_identifier(self.project)), 0)

        self.assertEqual(get_followers_count(self.project), 0)

        self.assertEqual(get_followers_count(self.project, registry.get_identifier(self.user)), 0)

    def test_friends(self):
        from ..models import (follow, get_friends_count,
                              unfollow)

        follow(self.user, self.project)

        self.assertEqual(get_friends_count(self.user), 0)

        follow(self.project, self.user)

        from_identifier = registry.get_identifier(self.user)
        to_identifier = registry.get_identifier(self.project)

        self.assertEqual(get_friends_count(self.user), 1)
        self.assertEqual(get_friends_count(self.user, to_identifier), 1)
        self.assertEqual(get_friends_count(self.user, from_identifier), 0)
        self.assertEqual(get_friends_count(self.project), 1)
        self.assertEqual(get_friends_count(self.project, from_identifier), 1)
        self.assertEqual(get_friends_count(self.project, to_identifier), 0)

        unfollow(self.user, self.project)

        self.assertEqual(get_friends_count(self.project), 0)
        self.assertEqual(get_friends_count(self.user), 0)

    def test_get_friends(self):
        pass

    def test_is_following(self):
        from ..models import (follow, unfollow, is_following)

        follow(self.user, self.project)

        self.assertTrue(is_following(self.user, self.project))

        unfollow(self.user, self.project)

        self.assertFalse(is_following(self.user, self.project))

    def test_get_followers(self):
        from ..models import follow, get_followers

        follow(self.user, self.project)

        qs = get_followers(self.project)

        self.assertEqual(qs.count(), 1)

        self.assertIn(self.user, dict(qs.all()))

    def test_get_followings(self):
        from ..models import follow, get_followings

        follow(self.user, self.project)

        qs = get_followings(self.user)

        self.assertEqual(qs.count(), 1)

        self.assertIn(self.project, dict(qs.all()))

    def test_follow_view(self):
        user = self.user

        self.client.login(username=user.username, password='$ecret')

        response = self.client.post(reverse('sequere_follow'))

        self.assertEqual(response.status_code, 400)

        response = self.client.post(reverse('sequere_follow'), data={
            'identifier': 'not-an-identifier',
            'object_id': 1
        })

        self.assertEqual(response.status_code, 400)

        project = self.project

        identifier = registry.get_identifier(project)

        response = self.client.post(reverse('sequere_follow'), data={
            'identifier': identifier,
            'object_id': project.pk
        })

        self.assertEqual(response.status_code, 200)

        content = json.loads(response.content.decode())

        self.assertEqual(content['followings_count'], 1)
        self.assertEqual(content['%s_followings_count' % identifier], 1)

    def test_unfollow_view(self):
        from ..models import follow

        user = self.user

        self.client.login(username=user.username, password='$ecret')

        response = self.client.post(reverse('sequere_follow'))

        project = self.project

        follow(self.user, project)

        identifier = registry.get_identifier(project)

        response = self.client.post(reverse('sequere_unfollow'), data={
            'identifier': identifier,
            'object_id': project.pk
        })

        self.assertEqual(response.status_code, 200)

        content = json.loads(response.content.decode())

        self.assertEqual(content['followings_count'], 0)
        self.assertEqual(content['%s_followings_count' % identifier], 0)


@mock.patch.object(settings, 'BACKEND_CLASS', 'sequere.backends.database.DatabaseBackend')
class DatabaseBackendTests(BaseBackendTests, TestCase):
    def test_from_instance_and_to_instance(self):
        from ..models import follow

        follow(self.user, self.project)

        instance = Follow.objects.all()[0]

        self.assertEqual(instance.to_instance, self.project)
        self.assertEqual(instance.from_instance, self.user)


@mock.patch.object(settings, 'BACKEND_CLASS', 'sequere.backends.redis.RedisBackend')
class RedisBackendTests(BaseBackendTests, TestCase):
    def setUp(self):
        super(RedisBackendTests, self).setUp()

        from sequere.backends.redis.connection import client

        client.flushdb()


@mock.patch.object(settings, 'BACKEND_CLASS', 'sequere.backends.redis.RedisBackend')
class TimelineTests(FixturesMixin, TestCase):
    def setUp(self):
        super(TimelineTests, self).setUp()

        from sequere.backends.redis.connection import client

        client.flushall()

    def test_simple_timeline(self):
        from .sequere_registry import JoinAction, User
        from sequere.contrib.timeline import Timeline

        timeline = Timeline(self.user)

        timeline.save(JoinAction(self.user))

        self.assertEqual(timeline.get_private_count(), 1)
        self.assertEqual(timeline.get_public_count(), 1)

        self.assertEqual(timeline.get_public_count(action='join'), 1)
        self.assertEqual(timeline.get_private_count(action='join'), 1)

        self.assertEqual(timeline.get_private_count(action=JoinAction), 1)
        self.assertEqual(timeline.get_public_count(action=JoinAction), 1)

        self.assertEqual(timeline.get_private_count(target=self.user), 1)
        self.assertEqual(timeline.get_private_count(target=User), 1)

        self.assertEqual(timeline.get_public_count(target=self.user), 1)
        self.assertEqual(timeline.get_public_count(target=User), 1)

        qs = timeline.get_private()

        self.assertEqual(qs.count(), 1)

        results = qs.all()

        self.assertEqual(len(results), 1)

        qs = timeline.get_public()

        self.assertEqual(qs.count(), 1)

        results = qs.all()

        self.assertEqual(len(results), 1)

    def test_read_at(self):
        from sequere.contrib.timeline import Timeline

        timeline = Timeline(self.user)
        timeline.mark_as_read()

        self.assertTrue(timeline.read_at is not None)

    def test_dispatch_action(self):
        from ..models import (follow, unfollow)
        from .sequere_registry import JoinAction, LikeAction, Project
        from sequere.contrib.timeline import Timeline

        follow(self.newbie, self.user)

        timeline = Timeline(self.user)

        action = JoinAction(self.user)

        timeline.save(action)

        timeline = Timeline(self.newbie)

        self.assertEqual(timeline.get_private_count(), 1)
        self.assertEqual(timeline.get_public_count(), 0)

        unfollow(self.newbie, self.user)

        action = LikeAction(actor=self.user, target=self.project)
        timeline = Timeline(self.user)

        timeline.save(action)

        self.assertEqual(timeline.get_private_count(), 2)
        self.assertEqual(timeline.get_public_count(), 2)

        self.assertEqual(timeline.get_private_count(target=Project), 1)
        self.assertEqual(timeline.get_public_count(target=Project), 1)

        timeline = Timeline(self.newbie)

        self.assertEqual(timeline.get_private_count(), 0)
        self.assertEqual(timeline.get_unread_count(), 0)

        timeline.mark_as_read(timestamp=datetime.now() + timedelta(days=1))

        self.assertEqual(timeline.get_unread_count(), 0)

        self.assertEqual(timeline.get_public_count(), 0)

    def test_get_actions(self):
        from .sequere_registry import JoinAction, LikeAction
        from sequere.contrib.timeline import get_actions

        actions = get_actions()

        self.assertEqual(dict(actions), {
            'join': JoinAction,
            'like': LikeAction
        })

    def test_signals_actions(self):
        from ..models import follow, unfollow
        from .sequere_registry import JoinAction
        from sequere.contrib.timeline import Timeline

        timeline = Timeline(self.user)

        action = JoinAction(self.user)

        timeline.save(action)

        follow(self.newbie, self.user)

        timeline = Timeline(self.newbie)

        self.assertEqual(timeline.get_private_count(), 1)
        self.assertEqual(timeline.get_unread_count(), 1)

        unfollow(self.newbie, self.user)

        self.assertEqual(timeline.get_private_count(), 0)
        self.assertEqual(timeline.get_unread_count(), 0)


@override_settings(SEQUERE_BACKEND_CLASS='sequere.backends.redis.RedisBackend', SEQUERE_TIMELINE_NYDUS_CONNECTION={
    'backend': 'nydus.db.backends.redis.Redis',
    'router': 'nydus.db.routers.keyvalue.PartitionRouter',
    'hosts': {
        0: {'db': 0},
        1: {'db': 1},
        2: {'db': 2},
    }
})
class NydusTimelineTests(TimelineTests):
    pass
