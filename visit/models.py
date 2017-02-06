# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import os

from django.db import models
from django.urls import reverse

from gabinet.settings import VISIT_TABS_DIR
from user_profile.models import Doctor


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