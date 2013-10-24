from django.template.defaultfilters import slugify


class ModelBase(object):
    model = None
    identifier = None

    def get_identifier(self):
        return self.identifier or slugify(self.model.__name__)
