from .models import Project

from ..compat import User
from ..base import ModelBase

from sequere.contrib.timeline import Action
from sequere import register


class ProjectSequere(ModelBase):
    identifier = 'projet'


class JoinAction(Action):
    verb = 'join'


class LikeAction(Action):
    verb = 'like'


class UserSequere(ModelBase):
    identifier = 'user'

    actions = [JoinAction, LikeAction, ]


register(User, UserSequere)
register(Project, ProjectSequere)
