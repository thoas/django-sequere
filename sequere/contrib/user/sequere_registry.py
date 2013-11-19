from sequere.compat import User
from sequere.base import ModelBase


class UserSequere(ModelBase):
    model = User
    identifier = 'user'
