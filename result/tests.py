from django.test import TestCase
from django.test import Client
import json

from django_dynamic_fixture import G

from result.models import Result
from user_profile.models import Patient, Doctor, Specialization


class ResultsTestCase(TestCase):

    def setUp(self):
        patient = G(Patient, pesel='88042003997')

        specialization = G(Specialization, name='ortopeda')
        doctor = G(Doctor)
        doctor.specializations.add(specialization)
        G(Result, patient=patient, doctor=doctor, specialization=specialization)

        specialization = G(Specialization, name='kardiolog')
        doctor = G(Doctor)
        doctor.specializations.add(specialization)
        G(Result, patient=patient, doctor=doctor, specialization=specialization)

        self.client = Client()

    def test_can_get_results(self):
        response = self.client.get('/rest/results/', {'pesel': 88042003997})
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertGreater(len(data), 1)

    def test_results_are_returned_as_categories_when_asked(self):
        response = self.client.get('/rest/results/', {'pesel': 88042003997, 'as_categories': 1})
        data = json.loads(response.content)
        self.assertEqual(data[0]['name'], 'kardiolog')

    def test_category_is_returned_correctly(self):
        response = self.client.get('/rest/results/', {'pesel': 88042003997, 'category': 'ortopeda'})
        data = json.loads(response.content)
        self.assertEqual(len(data['results']), 1)
