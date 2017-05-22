from django.core.management.base import BaseCommand
import requests
import json
import datetime
from django.contrib.auth.models import User, Group
from user_profile.models import Doctor, Specialization
from django.core.exceptions import ObjectDoesNotExist


class Command(BaseCommand):
    API_URL = 'http://10.250.0.2/accounts/api/list_doctors/'

    def handle(self, *args, **options):
        doctor_group = Group.objects.get(name='Doktor')
        res = requests.get(self.API_URL)
        doctors = json.loads(res.content)
        for d in doctors:
            try:
                u = User.objects.get(username=d['code'], email=d['email'])
            except ObjectDoesNotExist:
                try:
                    u = User.objects.create_user(d['code'], d['email'], 'Misal123')
                except:
                    continue
                doc = Doctor.objects.create(user=u, pwz=d['nr'], misal_id=d['code'])
                doc.user.groups.add(doctor_group)
                if 'specialization' in d:
                    for s in d['specialization']:
                        doc.specializations.add(Specialization.objects.get(code=d['code']))
                print 'utworzono %s' % d



