# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models
from user_profile.models import Doctor, Patient
from visit.models import Visit
import datetime
import time
from django.utils import timezone


class Term(models.Model):
    patient = models.ForeignKey(Patient, related_name='terms', blank=True, null=True, verbose_name=u'Pacjent')
    visit = models.ForeignKey(Visit, related_name='terms', blank=True, null=True)
    datetime = models.DateTimeField()
    status = models.CharField(max_length=10, choices=(('CANCELLED', u'Anulowany'), ('PENDING', u'Oczekujący'),
                                                      ('FREE', u'Wolny'),
                                                      ('FINISHED', u'Zakończony')), default='PENDING')
    doctor = models.ForeignKey(Doctor, related_name='terms')
    duration = models.IntegerField(default=15)

    def get_end(self):
        return self.datetime + datetime.timedelta(minutes=self.duration)

    def get_title(self):
        if self.patient:
            return '%s %s' % (self.patient.user.first_name, self.patient.user.last_name)
        else:
            return u'Wolny termin'

    @staticmethod
    def create_terms_for_period(doctor, start, end):
        tmz = timezone.get_current_timezone()
        days = doctor.get_working_hours()
        duration = doctor.visit_duration
        Term.objects.filter(doctor=doctor, datetime__gte=start, datetime__lte=end, status__in=['PENDING', 'CANCELLED']).delete()
        start = datetime.datetime.combine(start.date(), datetime.time(0, 0))
        end = datetime.datetime.combine(end.date(), datetime.time(0, 0))
        for i in range(0, (end-start).days):
            day = start + datetime.timedelta(days=i)
            hours = days[day.weekday()]
            start_hour = datetime.datetime.combine(day.date(), datetime.time(*[int(h) for h in hours['start'].split(':')]))
            end_hour = datetime.datetime.combine(day.date(), datetime.time(*[int(h) for h in hours['end'].split(':')]))
            start_visit = start_hour
            end_visit = start_hour + datetime.timedelta(minutes=duration)
            while end_visit <= end_hour:
                if hours['break_start']:
                    if end_visit.time() > datetime.time(*[int(h) for h in hours['break_start'].split(':')]):
                        continue
                    if start_visit.time() < datetime.time(*[int(h) for h in hours['break_end'].split(':')]):
                        continue
                visit_date = datetime.datetime.combine(day.date(), start_visit.time())
                #print visit_date
                try:
                    Term.objects.get(doctor=doctor, datetime=timezone.make_aware(visit_date, tmz))
                except:
                    Term.objects.create(doctor=doctor, duration=duration, datetime=timezone.make_aware(visit_date, tmz),
                                        status='FREE')
                start_visit = start_visit + datetime.timedelta(minutes=duration)
                end_visit = end_visit + datetime.timedelta(minutes=duration)
        doctor.terms_generated_till = end.date()
        doctor.save()
        return True


