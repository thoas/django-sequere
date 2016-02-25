from sequere.exceptions import SequereException


class ActionDoesNotExist(SequereException):
    pass


class ActionInvalid(SequereException):
    def __init__(self, *args, **kwargs):
        self.data = kwargs.pop('data', None)

        super(ActionInvalid, self).__init__(*args, **kwargs)
