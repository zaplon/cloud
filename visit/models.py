# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import os

from django.db import models
from django.urls import reverse

from gabinet.settings import VISIT_TABS_DIR
from user_profile.models import Doctor
import json

keys_choices = (('CTRL+F1', 'ctrl+f1'), ('CTRL+F2', 'ctrl+f2'), ('CTRL+F3', 'ctrl+f3'), ('CTRL+F4', 'ctrl+f4'),
                ('CTRL+F5', 'ctrl+f5'), ('CTRL+F6', 'ctrl+f6'), ('CTRL+F7', 'ctrl+f7'), ('CTRL+F8', 'ctrl+f8'),
                ('CTRL+F9', 'ctrl+f9'), ('CTRL+F10', 'ctrl+f10'), ('alt+f1', 'ALT+F1'), ('alt+f2', 'ALT+F2'),
                ('alt+f3', 'ALT+F3'),  ('alt+f4', 'ALT+F4'),  ('alt+f5', 'ALT+F5'),  ('alt+f6', 'ALT+F6'),
                 ('alt+f7', 'ALT+F7'),  ('alt+f8', 'ALT+F8'),  ('alt+f9', 'ALT+F9'),  ('alt+f10', 'ALT+F10'))


class Tab(models.Model):
    title = models.CharField(max_length=100, verbose_name=u'Tytuł')
    template = models.CharField(max_length=100, default='default.html', verbose_name=u'Szablon')
    doctor = models.ForeignKey(Doctor, related_name='tabs')
    order = models.IntegerField(unique=True, null=True, blank=True)
    enabled = models.BooleanField(default=True, verbose_name=u'Włączona')

    class Meta:
        ordering = ['order']

    def get_absolute_url(self):
        return reverse('tabs')

    def __unicode__(self):
        return self.title


class VisitTab(models.Model):
    title = models.CharField(max_length=100)
    body = models.TextField(default='')
    json = models.TextField(default='null')
    order = models.IntegerField(unique=True, null=True, blank=True)

    @property
    def data(self):
        if len(self.json) > 0:
            return json.loads(self.json)
        else:
            return False

    class Meta:
        ordering = ['order']


class Visit(models.Model):
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    visit_pdf = models.FileField(upload_to='visits/', null=True, blank=True)
    tabs = models.ManyToManyField(VisitTab, related_name='tabs')
    in_progress = models.BooleanField(default=False)

    def create_tabs(self):
        tabs = self.term.doctor.tabs.all()
        visit_tabs = []
        for tab in tabs:
            f = open(os.path.join(VISIT_TABS_DIR, tab.template), 'r')
            body = f.read()
            f.close()
            visit_tab = VisitTab.objects.create(title=tab.title, body=body, order=tab.order)
            visit_tabs.append(visit_tab)
        return visit_tabs


class Template(models.Model):
    name = models.CharField(max_length=100, verbose_name=u'Nazwa')
    tab = models.ForeignKey(Tab, related_name='templates', verbose_name=u'Sekcja')
    text = models.CharField(max_length=1000, verbose_name=u'Tekst')
    key = models.CharField(max_length=8, blank=True, null=True, verbose_name=u'Skrót',
                           choices=keys_choices)
    doctor = models.ForeignKey(Doctor, related_name='templates', null=True, blank=True)

    def get_absolute_url(self):
        return reverse('templates')


class Icd10(models.Model):
    code = models.CharField(max_length=5)
    desc = models.CharField(max_length=200)

    class Meta:
        verbose_name = 'Rozpoznanie'
        verbose_name_plural = 'Rozpoznania'