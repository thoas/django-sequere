from sequere.exceptions import SequereException


class DoesNotExist(SequereException):
    pass


class ActionDoesNotExist(DoesNotExist):
    pass
