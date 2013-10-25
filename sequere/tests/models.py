from django.db import models

from ..mixin import SequereMixin


class Project(SequereMixin, models.Model):
    name = models.CharField(max_length=100)
