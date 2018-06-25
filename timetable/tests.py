from django.test import TestCase, Client
from django.urls import reverse
from django_dynamic_fixture import G

from user_profile.models import Doctor, Patient
from django.contrib.auth.models import User
from .models import Term
import datetime
from django.utils import timezone


class TermTestCase(TestCase):
    def setUp(self):
        self.u = User.objects.create(username='jan', email='jan@wp.pl', password='123456')
        self.d = Doctor.objects.create(user=self.u, pwz='123456',
                                       working_hours=u'[{"start":"09:00","end":"17:00","break_start":null,"break_end":null,"dayName":"poniedzia\u0142ek","dayIndex":1},{"start":"09:00","end":"17:00","break_start":null,"break_end":null,"dayName":"wtorek","dayIndex":2},{"start":"09:00","end":"17:00","break_start":null,"break_end":null,"dayName":"\u015broda","dayIndex":3},{"start":"09:00","end":"17:00","break_start":null,"break_end":null,"dayName":"czwartek","dayIndex":4},{"start":"09:00","end":"17:00","break_start":null,"break_end":null,"dayName":"pi\u0105tek","dayIndex":5},{"start":"09:00","end":"17:00","break_start":null,"break_end":null,"dayName":"sobota","dayIndex":6},{"start":"09:00","end":"17:00","break_start":null,"break_end":null,"dayName":"niedziela","dayIndex":0}]')
        self.p = Patient.objects.create(user=self.u)
        self.client = Client()

    def test_can_create_terms_for_period(self):
        now = timezone.now()
        res = Term.create_terms_for_period(self.d, now - timezone.timedelta(days=30), now)
        self.assertEqual(res, True)
        self.assertTrue(Term.objects.all().count() > 100)

    def test_cant_get_terms_when_not_logged_in(self):
        response = self.client.get('/rest/terms/')
        self.assertEqual(response.status_code, 403)

    def test_reserved_visit_has_correct_status(self):
        term = G(Term, doctor=self.d)
        term.patient = self.p
        term.save()
        self.assertEqual(term.status, 'PENDING')

    def test_user_without_permissions_cant_edit_terms(self):
        t = G(Term, doctor=self.d)
        self.client.login(username='jan', password='123456')
        res = self.client.post(reverse('timetable:move-term'))
        self.assertEqual(res.status_code, 403)