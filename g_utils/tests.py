from django.test import TestCase, Client
from django.urls import reverse


class AjaxFormTestCase(TestCase):

    def setUp(self):
        self.url = reverse('get-form')
        self.client = Client()

    def test_form_is_returned(self):
        url = reverse('get-form')
        response = self.client.get(url, {'module': 'user_profile.forms', 'klass': 'PatientForm'})
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.json()['success'])
