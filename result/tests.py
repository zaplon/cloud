from django.test import TestCase
from elo.views import getPatientData
from django.test import Client
import json


class ResultsTestCase(TestCase):
    def test_can_get_results(self):
        c = Client()
        response = c.get('/rest/results/', {'pesel': 88042003997})
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertGreater(len(data), 1)



