# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models
from django.urls import reverse
from user_profile.models import Doctor


class Tab(models.Model):
    title = models.CharField(max_length=100)
    body = models.TextField(default='')
    template = models.CharField(max_length=100, default='visit/tabs/default.html')
    doctor = models.ForeignKey(Doctor, related_name='tabs')

    def get_absolute_url(self):
        return reverse('tabs')

    def __unicode__(self):
        return self.title


class Visit(models.Model):
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    visit_pdf = models.FileField(upload_to='visits/', null=True, blank=True)
    tabs = models.ManyToManyField(Tab, related_name='tabs')


class Template(models.Model):
    name = models.CharField(max_length=100, verbose_name=u'Nazwa')
    tab = models.ForeignKey(Tab, related_name='templates', verbose_name=u'Sekcja')
    text = models.CharField(max_length=1000, verbose_name=u'Tekst')
    key = models.CharField(max_length=8, blank=True, null=True, verbose_name=u'Skrót',
                           choices=(('CTRL+F1', 'ctrl+f1'), ('CTRL+F2', 'ctrl+f2')))
    doctor = models.ForeignKey(Doctor, related_name='templates', null=True, blank=True)

    def get_absolute_url(self):
        return reverse('templates')


class Icd10(models.Model):
    code = models.CharField(max_length=5)
    desc = models.CharField(max_length=200)

    class Meta:
        verbose_name = 'Rozpoznanie'
        verbose_name_plural = 'Rozpoznania'