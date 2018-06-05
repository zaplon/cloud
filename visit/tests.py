from django.test import TestCase, Client
from django.urls import reverse
from visit.models import Visit, TabTypes
from timetable.models import Term, Service
from user_profile.models import Patient, Doctor
from django.contrib.auth.models import User
from django_dynamic_fixture import G


class VisitTestCase(TestCase):

    def setUp(self):
        self.patient = G(Patient)
        self.user = User.objects.create(username='test', email='test@test.pl')
        self.user.set_password('123456')
        self.user.save()
        doctor = G(Doctor, user=self.user, working_hours=[])
        service = G(Service, doctor=doctor)
        self.term = G(Term, service=service, patient=self.patient, doctor=doctor)
        self.visit = G(Visit, term=self.term)
        self.client = Client()
        self.client.login(username=self.user.username, password='123456')

    def test_visit_viewset_returns_patient(self):
        url = reverse('rest:visits-detail', kwargs={'pk': self.term.pk})
        res = self.client.get(url)
        res_json = res.json()
        self.assertTrue('term' in res_json)
        self.assertEqual(res_json['term']['patient']['pesel'], self.patient.pesel)
