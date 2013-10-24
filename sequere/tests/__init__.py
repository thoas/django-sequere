from django.test import TestCase
from django.core.urlresolvers import reverse
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
        from ..models import follow

        follow(self.user, self.project)
