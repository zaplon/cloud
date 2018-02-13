from django.core.management.base import BaseCommand, CommandError
from user_profile.models import Doctor, Patient
from timetable.models import Term
import requests
import json
import datetime


class Command(BaseCommand):
    API_URL = 'https://rezerwacja.rentgen.pl/api/sync'

    def handle(self, *args, **options):
        for d in Doctor.objects.all().exclude(misal_id__isnull=True).exclude(user__last_name='')[0:20]:
            res = requests.get(self.API_URL + '?id=' + d.misal_id)
            visits = json.loads(res.content)
            for v in visits:
                dt = datetime.datetime.strptime(v['date'] + ' ' + v['hour'], '%Y-%m-%d %H:%M')
                if not v['free']:
                    name_parts = v['patient']['name'].split(' ')
                    first_name = name_parts[0]
                    if len(name_parts) > 1:
                        last_name = name_parts[1]
                    else:
                        last_name = ' '
                    p, _ = Patient.objects.get_or_create(pesel=v['patient']['pesel'], first_name=first_name, last_name=last_name)
                try:
                    t = Term.objects.get(datetime=dt, doctor=d)
                except:
                    t = Term(datetime=dt, doctor=d)
                if not v['free']:
                    t.patient = p
                print v
                t.status = 'FREE' if v['free'] else 'PENDING'
                t.save()
                print('Zapisano %s' % t)




