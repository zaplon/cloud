from __future__ import unicode_literals
from django.conf import settings
from django.db import models
import json


class Doctor(models.Model):
    pwz = models.CharField(max_length=7)
    mobile = models.IntegerField(blank=True, null=True)
    user = models.OneToOneField(settings.AUTH_USER_MODEL)
    working_hours = models.CharField(max_length=200, blank=True, null=True)
    visit_duration = models.IntegerField(default=15)

    def get_working_hours(self):
        return json.loads(self.working_hours)


class Patient(models.Model):
    mobile = models.IntegerField(blank=True, null=True)
    user = models.OneToOneField(settings.AUTH_USER_MODEL)


class Recipe(models.Model):
    doctor = models.ForeignKey(Doctor, related_name='recipes')
    nr = models.CharField(max_length=30)
    was_used = models.BooleanField(blank=False, default=False)


class Specialization(models.Model):
    name = models.CharField(max_length=50)
    code = models.CharField(max_length=10)
    code_misal = models.CharField(max_length=100)