from .models import Project

from ..compat import User
from ..base import ModelBase

import sequere


class ProjectSequere(ModelBase):
    identifier = 'projet'


sequere.register(User)
sequere.register(Project, ProjectSequere)
