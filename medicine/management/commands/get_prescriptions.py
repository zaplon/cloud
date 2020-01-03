import json

import requests
from django.core.management.base import BaseCommand

from medicine.models import PrescriptionJob
from user_profile.models import NFZSettings
from user_profile.rest import NFZSettingsSerializer


class Command(BaseCommand):

    def handle(self, *args, **options):
        for job in PrescriptionJob.objects.filter(finished=False):
            profile = NFZSettingsSerializer(instance=NFZSettings.objects.get(user__doctor=job.prescription.doctor))
            res = requests.post('http://prescriptions/api/get_prescription/',
                                json={'job_id': job.job_id, 'profile': profile.data})
            print(res.content)
            res_json = json.loads(res.content)
            if 'major' in res_json['wynik'] and res_json['wynik']['major'] == 'urn:csioz:p1:kod:major:Sukces':
                prescription = job.prescription
                prescription.external_id = \
                    res_json['potwierdzenieOperacjiZapisu']['wynikZapisuPakietuRecept']['kluczPakietuRecept']
                prescription.external_code = \
                    res_json['potwierdzenieOperacjiZapisu']['wynikZapisuPakietuRecept']['kodPakietuRecept']
                prescription.save()
                for i, medicine in enumerate(prescription.medicines.all()):
                    medicine.external_id = res_json['potwierdzenieOperacjiZapisu']['wynikZapisuPakietuRecept']
                    ['wynikWeryfikacji']['weryfikowanaRecepta'][i]['kluczRecepty']
                    medicine.save()
                job.finished = True
                job.save()

