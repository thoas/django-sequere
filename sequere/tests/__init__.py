import itertools

from django.test.utils import override_settings
from django.test import TestCase

from exam.decorators import fixture
from exam.cases import Exam

from ..compat import User

from .models import Project

import sequere

from sequere import settings
from sequere.registry import registry

sequere.autodiscover()


class BaseBackendTests(Exam):
    @fixture
    def user(self):
        return User.objects.create_user(username='thoas',
                                        email='florent@ulule.com',
                                        password='$ecret')

    @fixture
    def project(self):
        return Project.objects.create(name='My super project')

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

    def test_is_following(self):
        from ..models import (follow, unfollow, is_following)

        follow(self.user, self.project)

        self.assertTrue(is_following(self.user, self.project))

        unfollow(self.user, self.project)

        self.assertFalse(is_following(self.user, self.project))

    def test_get_followers(self):
        from ..models import follow, get_followers

        follow(self.user, self.project)

        follower_list = list(itertools.chain(*[followers for followers in get_followers(self.project)]))

        self.assertEqual(len(follower_list), 1)

        self.assertIn(self.user, dict(follower_list))

        follower_list = list(itertools.chain(*[followers for followers in get_followers(self.project, identifier=registry.get_identifier(self.user))]))

        self.assertEqual(len(follower_list), 1)

        self.assertIn(self.user, dict(follower_list))

    def test_get_followings(self):
        from ..models import follow, get_followings

        follow(self.user, self.project)

        following_list = list(itertools.chain(*[followers for followers in get_followings(self.user)]))

        self.assertEqual(len(following_list), 1)

        self.assertIn(self.project, dict(following_list))

        following_list = list(itertools.chain(*[followers for followers in get_followings(self.user, identifier=registry.get_identifier(self.project))]))

        self.assertEqual(len(following_list), 1)

        self.assertIn(self.project, dict(following_list))


@override_settings(SEQUERE_BACKEND_CLASS='sequere.backends.database.DatabaseBackend')
class DatabaseBackendTests(BaseBackendTests, TestCase):
    def setUp(self):
        super(DatabaseBackendTests, self).setUp()

        reload(settings)


@override_settings(SEQUERE_BACKEND_CLASS='sequere.backends.redis.RedisBackend')
class RedisBackendTests(BaseBackendTests, TestCase):
    def setUp(self):
        super(RedisBackendTests, self).setUp()

        reload(settings)

        from sequere.backends import get_backend

        get_backend()().client.flushdb()


@override_settings(SEQUERE_BACKEND_CLASS='sequere.backends.redis.RedisFallbackBackend')
class RedisFallbackBackendTests(BaseBackendTests, TestCase):
    def setUp(self):
        super(RedisFallbackBackendTests, self).setUp()

        reload(settings)

        from sequere.backends import get_backend

        get_backend()().client.flushdb()
