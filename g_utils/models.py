from __future__ import unicode_literals

from django.db import models


class SoftDeleteModel(models.Model):
    class Meta:
        abstract = True
    deleted = models.DateTimeField(null=True, blank=True)
