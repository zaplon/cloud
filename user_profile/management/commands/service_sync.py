from django.core.management.base import BaseCommand
import requests
import json
import datetime
from django.contrib.auth.models import User, Group
from user_profile.models import Doctor
from timetable.models import Service
from django.core.exceptions import ObjectDoesNotExist


class Command(BaseCommand):
    API_URL = 'http://rezerwacja.rentgen.pl/api/services/'

    def handle(self, *args, **options):
        res = requests.get(self.API_URL, headers={'token': '123'})
        services = json.loads(res.content)
        for s in services:
            try:
                s = Service.objects.get(code=s['code'].replace(' ', ''))               
             except ObjectDoesNotExist:
                ser = Service(code=s['code'].replace(' ', ''))
                print 'utworzono %s' % ser
              ser.name = s['name']
              ser.price = s['price']
              docs = json.loads(s['doctors'])
              for d in docs:
                ser.doctors.add(Doctor.objects.get(misal_id=d))
              print 'zaktualizowano %s' % ser  
