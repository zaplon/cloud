from g_utils.utils import GabinetTestCase
from user_profile.models import Doctor


class CreateUserTestCase(GabinetTestCase):

    def test_create_new_user(self):
        response = self.client.post('/rest/users/',
                                    {'role': 'registration', 'username': 'test_register',
                                     'password': 'PXCASaa!!', 'password2': 'PXCASaa!!'})
        self.assertEqual(response.status_code, 201)
        logged_in = self.client.login(username='test_register', password='PXCASaa!!')
        self.assertTrue(logged_in)

    def test_passwords_need_to_match(self):
        response = self.client.post('/rest/users/',
                                    {'username': 'test_register', 'role': 'registration',
                                     'password': 'PXCASaa!!', 'password2': 'PXCASaa!!33'})
        self.assertEqual(response.status_code, 400)
        errors = response.json()
        self.assertIn('password', errors)

    def test_doctor_instance_is_created_when_role_is_doctor(self):
        response = self.client.post('/rest/users/',
                                    {'role': 'doctor', 'username': 'test_register',
                                     'password': 'PXCASaa!!', 'password2': 'PXCASaa!!'})
        self.assertEqual(response.status_code, 201)
        self.assertTrue(Doctor.objects.filter(user__username=response.json()['username']).exists())

