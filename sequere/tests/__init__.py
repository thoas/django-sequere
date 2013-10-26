import itertools

from django.test.utils import override_settings
from django.test import TestCase

from exam.decorators import fixture
from exam.cases import Exam

from ..compat import User

from .models import Project

import sequere

from sequere import settings

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

        self.assertEqual(get_followers_count(self.project), 1)

    def test_unfollow(self):
        from ..models import (follow, get_followings_count,
                              get_followers_count, unfollow)

        follow(self.user, self.project)

        unfollow(self.user, self.project)

        self.assertEqual(get_followings_count(self.user), 0)

        self.assertEqual(get_followers_count(self.project), 0)

    def test_is_following(self):
        from ..models import (follow, unfollow, is_following)

        follow(self.user, self.project)

        self.assertTrue(is_following(self.user, self.project))

        unfollow(self.user, self.project)

        self.assertFalse(is_following(self.user, self.project))

    def test_get_followers(self):
        from ..models import follow, get_followers

        follow(self.user, self.project)

        followers = list(itertools.chain(*[followers for followers in get_followers(self.project)]))

        self.assertEqual(len(followers), 1)

        self.assertIn(self.user, dict(followers))

    def test_get_followings(self):
        from ..models import follow, get_followings

        follow(self.user, self.project)

        followings = list(itertools.chain(*[followers for followers in get_followings(self.user)]))

        self.assertEqual(len(followings), 1)

        self.assertIn(self.project, dict(followings))


@override_settings(SEQUERE_BACKEND_CLASS='sequere.backends.simple.SimpleBackend')
class FollowSimpleTests(BaseBackendTests, TestCase):
    def setUp(self):
        super(FollowSimpleTests, self).setUp()

        reload(settings)


@override_settings(SEQUERE_BACKEND_CLASS='sequere.backends.redis.RedisBackend')
class FollowRedisTests(BaseBackendTests, TestCase):
    def setUp(self):
        super(FollowRedisTests, self).setUp()

        reload(settings)

        from sequere.backends import get_backend

        get_backend()().client.flushdb()
