# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import datetime
from django.urls import reverse

from visit.models import Visit
from user_profile.models import Patient, Doctor
from django.db import models
from django.conf import settings
from .search import *

RESULT_TYPES = (('IMAGE', u'Zdjęcie'), ('DOCUMENT', u'Dokument'), ('VIDEO', u'Film'), ('ENDOSCOPE_VIDEO', u'Film'),
                ('ENDOSCOPE_IMAGE', u'Zdjęcie'))


class Result(models.Model):
    name = models.CharField(max_length=200, verbose_name='Nazwa')
    file = models.FileField(upload_to='results/', verbose_name='Plik')
    uploaded = models.DateTimeField()
    description = models.CharField(max_length=1000, blank=True, null=True, verbose_name='Opis')
    visit = models.ForeignKey(Visit, related_name='results', null=True, blank=True)
    patient = models.ForeignKey(Patient, related_name='results', verbose_name='Pacjent')
    type = models.CharField(max_length=20, choices=RESULT_TYPES, default='DOCUMENT')
    doctor = models.ForeignKey(Doctor, blank=True, null=True, related_name='results', verbose_name='Doktor')

    def get_absolute_url(self):
        return reverse('archive')

    def save(self, force_insert=False, force_update=False, using=None,
             update_fields=None):
        ext = self.name.split('.')[-1]
        if ext in settings.EXTENSIONS['img']:
            self.type = 'IMAGE'
        if ext in settings.EXTENSIONS['video']:
            self.type = 'VIDEO'
        if not self.uploaded:
            self.uploaded = datetime.datetime.now()
        super(Result, self).save(force_insert=False, force_update=False, using=None, update_fields=None)
        # TODO lepsza obsługa wyjątku
        try:
            self.indexing()
        except:
            pass

    def indexing(self):
        obj = ResultIndex(
            meta={'id': self.id},
            name=self.name,
            description=self.description,
            uploaded=self.uploaded,
            # visit=None,
            url=self.file.url,
            doctor={'pwz': self.doctor.pwz, 'name': self.doctor.name} if self.doctor else None,
            type=self.type,
            patient={'first_name': self.patient.first_name, 'last_name': self.patient.last_name,
                     'pesel': self.patient.pesel,
                     'name': '%s %s' % (self.patient.first_name, self.patient.last_name)}
        )
        obj.save()
        return obj.to_dict(include_meta=True)
