from django.test import TestCase
from user_profile.models import Doctor, Patient
from django.contrib.auth.models import User
from .models import Term
import datetime
from django.utils import timezone


class TermTestCase(TestCase):
    def setUp(self):
        self.u = User.objects.create(username='jan', email='jan@wp.pl')
        self.d = Doctor.objects.create(user=self.u, pwz='123456',
                                       working_hours=u'[{"start":"09:00","end":"17:00","break_start":null,"break_end":null,"dayName":"poniedzia\u0142ek","dayIndex":1},{"start":"09:00","end":"17:00","break_start":null,"break_end":null,"dayName":"wtorek","dayIndex":2},{"start":"09:00","end":"17:00","break_start":null,"break_end":null,"dayName":"\u015broda","dayIndex":3},{"start":"09:00","end":"17:00","break_start":null,"break_end":null,"dayName":"czwartek","dayIndex":4},{"start":"09:00","end":"17:00","break_start":null,"break_end":null,"dayName":"pi\u0105tek","dayIndex":5},{"start":"09:00","end":"17:00","break_start":null,"break_end":null,"dayName":"sobota","dayIndex":6},{"start":"09:00","end":"17:00","break_start":null,"break_end":null,"dayName":"niedziela","dayIndex":0}]')
        self.p = Patient.objects.create(user=self.u)

    def test_can_create_terms_for_period(self):
        now = timezone.now()
        res = Term.create_terms_for_period(self.d, self.p, now - timezone.timedelta(days=30), now)
        self.assertEqual(res, False)
