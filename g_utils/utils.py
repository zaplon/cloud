from django.contrib.auth.models import User
from django.test import TestCase, Client


class GabinetTestCase(TestCase):

    def setUp(self):
        super(GabinetTestCase, self).setUp()
        self.user = User.objects.create_user('test', 'test@test.pl', '123456')
        self.user.is_active = True
        self.user.is_superuser = True
        self.user.save()
        self.client = Client()
        self.client.login(username=self.user.username, password='123456')
