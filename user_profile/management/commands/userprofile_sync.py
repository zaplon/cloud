from django.core.management.base import BaseCommand
import requests
import json
import datetime
from django.contrib.auth.models import User
from user_profile.models import Doctor


class Command(BaseCommand):
    API_URL = 'http://10.250.0.2/accounts/api/list_doctors/'

    def handle(self, *args, **options):
        res = requests.get(self.API_URL)
        doctors = json.loads(res.content)
        for d in doctors:
            try:
                u = User.objects.get(username=d['code'])
            except:
                u = User.objects.create_user(d['code'], d['email'], 'Misal123')
                d = Doctor.objects.create(user=u, pwz=d['nr'])
                print 'utworzono %s' % d



