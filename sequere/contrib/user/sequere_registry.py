from sequere.compat import User
from sequere.registry import registry
from sequere.base import ModelBase


class UserSequere(ModelBase):
    model = User
    identifier = 'user'


registry.register(User, UserSequere)
