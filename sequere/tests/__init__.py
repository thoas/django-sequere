import itertools

from django.test import TestCase
from django.test.utils import override_settings

from exam.decorators import fixture
from exam.cases import Exam

from ..compat import User

from .models import Project

import sequere

sequere.autodiscover()


class FollowTests(Exam, TestCase):
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

    def test_followers(self):
        from ..models import follow, get_followers

        follow(self.user, self.project)

        followers = list(itertools.chain(*[followers for followers in get_followers(self.project)]))

        self.assertEqual(len(followers), 1)

    def test_followings(self):
        from ..models import follow, get_followings

        follow(self.user, self.project)

        followings = list(itertools.chain(*[followers for followers in get_followings(self.user)]))

        self.assertEqual(len(followings), 1)
