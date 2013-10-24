from .models import Project

from ..compat import User

import sequere


sequere.register(User)
sequere.register(Project)
