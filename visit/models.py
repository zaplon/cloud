# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from enum import Enum

from django.db import models
from django.db.models.signals import pre_save
from django.urls import reverse
from django.utils.text import slugify
import json

keys_choices = (('CTRL+F1', 'ctrl+f1'), ('CTRL+F2', 'ctrl+f2'), ('CTRL+F3', 'ctrl+f3'), ('CTRL+F4', 'ctrl+f4'),
                ('CTRL+F5', 'ctrl+f5'), ('CTRL+F6', 'ctrl+f6'), ('CTRL+F7', 'ctrl+f7'), ('CTRL+F8', 'ctrl+f8'),
                ('CTRL+F9', 'ctrl+f9'), ('CTRL+F10', 'ctrl+f10'), ('alt+f1', 'ALT+F1'), ('alt+f2', 'ALT+F2'),
                ('alt+f3', 'ALT+F3'),  ('alt+f4', 'ALT+F4'),  ('alt+f5', 'ALT+F5'),  ('alt+f6', 'ALT+F6'),
                 ('alt+f7', 'ALT+F7'),  ('alt+f8', 'ALT+F8'),  ('alt+f9', 'ALT+F9'),  ('alt+f10', 'ALT+F10'))


class TabTypes(Enum):
    DEFAULT = 'Pole tekstowe'
    ICD10 = 'Rozpoznanie'
    MEDICINES = 'Leki'
    NOTES = 'Notatki'
    SERVICES = 'Skierowania'
    VIDEO = 'Nagranie wideo'
    OCULIST = 'Okulista'


class Tab(models.Model):

    class Meta:
        ordering = ['order', 'title']

    title = models.CharField(max_length=100, verbose_name=u'Tytuł')
    doctor = models.ForeignKey('user_profile.Doctor', related_name='tabs')
    order = models.IntegerField(null=True, blank=True, verbose_name=u'Kolejność')
    enabled = models.BooleanField(default=True, verbose_name=u'Włączona')
    type = models.CharField(max_length=16, choices=[(tag.name, tag.value) for tag in TabTypes],
                            default=TabTypes.DEFAULT.name, verbose_name=u'Typ')

    @property
    def name(self):
        return slugify(self.title)

    @property
    def type_name(self):
        print(self.type)
        try:
            return TabTypes[self.type.split('.')[1]].value
        except:
            return TabTypes[self.type].value

    class Meta:
        ordering = ['order']
        unique_together = ('doctor', 'order',)

    def get_absolute_url(self):
        return reverse('tabs')

    def __str__(self):
        return self.title


#@receiver(pre_save, sender=Tab)
#def slugify_name(sender, instance, **kwargs):
#    instance.name = slugify(instance.title)


class VisitTab(models.Model):
    title = models.CharField(max_length=100)
    json = models.TextField(default='null')
    order = models.IntegerField(null=True, blank=True)
    type = models.CharField(max_length=12)
    visit = models.ForeignKey('Visit', related_name='tabs')

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
    in_progress = models.BooleanField(default=False)

    def create_tabs(self):
        tabs = self.term.doctor.tabs.all()
        visit_tabs = []
        for tab in tabs:
            visit_tab = VisitTab.objects.create(title=tab.title, order=tab.order, type=tab.type, visit=self)
            visit_tabs.append(visit_tab)
        return visit_tabs

    @property
    def printable_tabs(self):
        return self.tabs.all().exclude(type='OCULIST')


class Template(models.Model):
    name = models.CharField(max_length=100, verbose_name=u'Nazwa')
    tab = models.ForeignKey(Tab, related_name='templates', verbose_name=u'Sekcja')
    text = models.CharField(max_length=1000, verbose_name=u'Tekst')
    key = models.CharField(max_length=8, blank=True, null=True, verbose_name=u'Skrót',
                           choices=keys_choices)
    doctor = models.ForeignKey('user_profile.Doctor', related_name='templates', null=True, blank=True)

    def get_absolute_url(self):
        return reverse('templates')


class Icd10(models.Model):
    code = models.CharField(max_length=5)
    desc = models.CharField(max_length=200)
    visits = models.ManyToManyField(Visit, related_name='icd_codes')

    class Meta:
        verbose_name = 'Rozpoznanie'
        verbose_name_plural = 'Rozpoznania'

