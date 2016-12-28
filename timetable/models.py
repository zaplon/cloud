from __future__ import unicode_literals

from django.db import models
from user_profile.models import Doctor, Patient
from visit.models import Visit
import datetime
import time
from django.utils import timezone


class Term(models.Model):
    patient = models.ForeignKey(Patient, related_name='terms')
    visit = models.ForeignKey(Visit, related_name='terms', blank=True, null=True)
    datetime = models.DateTimeField()
    status = models.CharField(max_length=10, choices=(('CANCELLED', 'cancelled'), ('PENDING', 'pending'),
                                                      ('FINISHED', 'finished')), default='PENDING')
    doctor = models.ForeignKey(Doctor, related_name='terms')
    duration = models.IntegerField(default=15)

    def get_end(self):
        return self.datetime + datetime.timedelta(minutes=self.duration)

    def get_title(self):
        return '%s %s' % (self.patient.user.first_name, self.patient.user.last_name)

    @staticmethod
    def create_terms_for_period(doctor, patient, start, end):
        days = doctor.get_working_hours()
        duration = doctor.visit_duration
        Term.objects.filter(doctor=doctor, datetime__gte=start, datetime__lte=end, status__in=['PENDING', 'CANCELLED']).delete()
        start = datetime.datetime.combine(start.date(), datetime.time(0, 0))
        end = datetime.datetime.combine(end.date(), datetime.time(0, 0))

        for i in range(0, (end-start).days):
            day = start + datetime.timedelta(days=1)
            hours = days[day.weekday()]
            start_hour = datetime.datetime.combine(day.date(), datetime.time(*[int(h) for h in hours['start'].split(':')]))
            end_hour = datetime.datetime.combine(day.date(), datetime.time(*[int(h) for h in hours['end'].split(':')]))
            start_visit = start_hour
            end_visit = start_hour + datetime.timedelta(minutes=duration)
            while end_visit < end_hour:
                start_visit = start_visit + datetime.timedelta(minutes=duration)
                end_visit = end_visit + datetime.timedelta(minutes=duration)
                visit_date = datetime.datetime.combine(day.date(), start_visit.time())
                print visit_date
                Term.objects.create(doctor=doctor, duration=duration, patient = patient,
                                    datetime=visit_date)
            return True


