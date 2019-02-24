from datetime import datetime
from dateutil.relativedelta import relativedelta

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


def get_age_from_pesel(pesel):
    if len(pesel) < 6:
        return ''
    return relativedelta(datetime.now(), get_birth_date_from_pesel(pesel)).years


def get_birth_date_from_pesel(pesel):
    if len(pesel) < 6:
        return ''
    birth_date = pesel[0:6]
    return datetime.strptime(birth_date, '%y%m%d')

