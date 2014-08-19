from sequere.compat import User
from sequere.registry import registry
from sequere.base import ModelBase


class UserSequere(ModelBase):
    model = User
    identifier = 'user'


if registry.for_model(User) is None:
    registry.register(User, UserSequere)
