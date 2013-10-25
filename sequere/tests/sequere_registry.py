from .models import Project

from ..compat import User
from ..base import ModelBase

from sequere import registry


class ProjectSequere(ModelBase):
    identifier = 'projet'


registry.register(User)
registry.register(Project, ProjectSequere)
