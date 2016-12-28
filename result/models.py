from __future__ import unicode_literals
from visit.models import Visit
from user_profile.models import Patient
from django.db import models


class Result(models.Model):
    name = models.CharField(max_length=200)
    file = models.FileField(upload_to='results/')
    uploaded = models.DateTimeField(auto_created=True)
    description = models.CharField(max_length=1000, blank=True, null=True)
    visit = models.ForeignKey(Visit, related_name='results')
    patient = models.ForeignKey(Patient, related_name='results')
