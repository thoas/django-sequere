class ModelBase(object):
    model = None
    identifier = None

    def get_identifier(self):
        return self.identifier or self.model.__name__.lower()
