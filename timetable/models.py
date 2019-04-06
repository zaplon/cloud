# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models
from user_profile.models import Doctor, Patient
from visit.models import Visit
import datetime
from django.utils import timezone


class ServiceToDoctor(models.Model):
    doctor = models.ForeignKey(Doctor, verbose_name=u'Lekarz', on_delete=models.CASCADE)
    service = models.ForeignKey('Service', verbose_name=u'Usługa', on_delete=models.CASCADE)
    price = models.FloatField(blank=True, null=True, verbose_name=u'Cena')
    localization = models.ForeignKey('Localization', null=True, blank=True, on_delete=models.CASCADE)


class Service(models.Model):
    name = models.CharField(max_length=255, verbose_name=u'Nazwa')
    price = models.FloatField(default=0, verbose_name=u'Cena')
    code = models.CharField(unique=True, verbose_name='Kod', max_length=10)
    doctors = models.ManyToManyField(Doctor, verbose_name=u'Lekarze', blank=True)

    class Meta:
        verbose_name = u'Usługa'
        verbose_name_plural = u'Usługi'

    def __str__(self):
        return self.name


class Localization(models.Model):
    name = models.CharField(max_length=255, verbose_name=u'Nazwa')
    address = models.CharField(max_length=255, blank=True, null=True, verbose_name=u'Adres')
    code = models.CharField(unique=True, verbose_name='Kod', max_length=10)

    class Meta:
        verbose_name = 'Lokalizacja'
        verbose_name_plural = 'Lokalizacje'

    def __str__(self):
        return self.name


class Term(models.Model):
    patient = models.ForeignKey(Patient, related_name='patient', blank=True, null=True, verbose_name=u'Pacjent',
                                on_delete=models.CASCADE)
    visit = models.OneToOneField(Visit, related_name='term', blank=True, null=True, on_delete=models.CASCADE)
    datetime = models.DateTimeField(verbose_name=u'Data')
    status = models.CharField(max_length=10, choices=(('CANCELLED', u'Anulowany'), ('PENDING', u'Oczekujący'),
                                                      ('FREE', u'Wolny'),
                                                      ('FINISHED', u'Zakończony')), default='PENDING')
    doctor = models.ForeignKey(Doctor, related_name='terms', verbose_name=u'Lekarz', on_delete=models.CASCADE)
    duration = models.IntegerField(default=15, verbose_name=u'Czas trwania (min)')
    code = models.CharField(max_length=50, null=True, blank=True)
    service = models.ForeignKey(Service, blank=True, null=True, related_name='terms', verbose_name=u'Usługa',
                                on_delete=models.CASCADE)
    localization = models.ForeignKey(Localization, blank=True, null=True, related_name='terms',
                                     verbose_name=u'Lokalizacja', on_delete=models.CASCADE)

    def __str__(self):
        if self.patient:
            return self.doctor.__str__() + ' ' + self.patient.__str__() + ' ' + self.datetime.strftime('%Y-%m-%d %H:%M')
        else:
            return self.doctor.__str__() + ' wolny ' + self.datetime.strftime('%Y-%m-%d %H:%M')

    def get_end(self):
        return self.datetime + timezone.timedelta(minutes=self.duration)

    def get_patient(self):
        if self.patient:
            return '%s %s' % (self.patient.first_name, self.patient.last_name)
        else:
            return ''

    def get_title(self):
        if self.patient:
            text = '%s %s' % (self.patient.first_name, self.patient.last_name)
            if self.service:
                text += ' ' + self.service.name
            return text
        else:
            return u'Wolny termin'

    @staticmethod
    def create_terms_for_period(doctor, start, end):
        tmz = timezone.get_current_timezone()
        days = doctor.get_working_hours()
        duration = doctor.visit_duration
        Term.objects.filter(doctor=doctor, datetime__gte=start, datetime__lte=end, status__in=['FREE']).delete()
        start = datetime.datetime.combine(start.date(), datetime.time(0, 0))
        end = datetime.datetime.combine(end.date(), datetime.time(0, 0))
        terms = []

        def move_forward(start, end):
            return start + datetime.timedelta(minutes=duration), end + datetime.timedelta(minutes=duration)
        for i in range(0, (end-start).days):
            day = start + datetime.timedelta(days=i)
            hours = days[day.weekday()]
            if not hours.get('on', True):
                continue
            start_hour = datetime.datetime.combine(day.date(), datetime.time(*[int(h) for h in hours['value'][0].split(':')]))
            end_hour = datetime.datetime.combine(day.date(), datetime.time(*[int(h) for h in hours['value'][1].split(':')]))
            start_visit = start_hour
            end_visit = start_hour + datetime.timedelta(minutes=duration)
            already_filled_dates = Term.objects.filter(doctor=doctor, datetime__gte=start,
                                                       datetime__lte=end).values_list('datetime', flat=True)
            while end_visit <= end_hour:
                if hours.get('break', False):
                    break_start = datetime.time(*[int(h) for h in hours['break'][0].split(':')])
                    break_end = datetime.time(*[int(h) for h in hours['break'][1].split(':')])
                    visit_start = start_visit.time()
                    visit_end = end_visit.time()
                    if break_start < visit_end < break_end or break_start < visit_start < break_end:
                        start_visit, end_visit = move_forward(start_visit, end_visit)
                        continue
                visit_date = datetime.datetime.combine(day.date(), start_visit.time())
                if visit_date not in already_filled_dates:
                    terms.append(Term(doctor=doctor, duration=duration, datetime=visit_date,
                                        status='FREE'))
                start_visit, end_visit = move_forward(start_visit, end_visit)
        Term.objects.bulk_create(terms)
        doctor.terms_generated_till = end.date()
        doctor.save()
        return True


