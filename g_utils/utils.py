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
    if int(birth_date[2]) >= 2:
        birth_date = '20' + birth_date[0:2] + str(int(birth_date[2]) - 2) + birth_date[3:]
    else:
        birth_date = '19' + birth_date
    return datetime.strptime(birth_date, '%Y%m%d')


def merge_jpgs_into_pdf(jpg_files):
    pass
