# -*- coding: utf-8 -*-
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
    terms_generated_till = models.DateField(null=True, blank=True)
    terms_start = models.TimeField(default='09:00')
    terms_end = models.TimeField(default='17:00')

    def get_working_hours(self):
        return json.loads(self.working_hours)

    def get_name(self):
        return self.__unicode__()

    def __unicode__(self):
        return '%s %s' % (self.user.first_name, self.user.last_name)


class Patient(models.Model):
    mobile = models.IntegerField(blank=True, null=True, verbose_name=u'Telefon')
    user = models.OneToOneField(settings.AUTH_USER_MODEL, blank=True, null=True)
    first_name = models.CharField(max_length=100, default='', verbose_name=u'Imię')
    last_name = models.CharField(max_length=100, default='', verbose_name=u'Nazwisko')
    pesel = models.CharField(max_length=11, blank=True, null=True, verbose_name=u'Pesel')
    email = models.EmailField(blank=True, null=True, verbose_name=u'Email')

    def __unicode__(self):
        return '%s %s' % (self.first_name, self.last_name)


class Note(models.Model):
    text = models.CharField(max_length=1024)
    patient = models.ForeignKey(Patient, related_name='notes')
    doctor = models.ForeignKey(Doctor, related_name='notes')

    def get_author(self):
        return self.doctor.__unicode__()


class Recipe(models.Model):
    doctor = models.ForeignKey(Doctor, related_name='recipes')
    nr = models.CharField(max_length=30)
    was_used = models.BooleanField(blank=False, default=False)


class Specialization(models.Model):
    name = models.CharField(max_length=50)
    code = models.CharField(max_length=10)
    code_misal = models.CharField(max_length=100)