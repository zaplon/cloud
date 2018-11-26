import json
from datetime import datetime
from django.shortcuts import render
from django.utils.text import slugify

from visit.views import GabinetPdfView


class ReferralPdfView(GabinetPdfView):
    def get(self, request, *args, **kwargs):
        patient = json.loads(self.request.GET['patient'])
        self.template_name = 'pdf/referral.html'
        self.cmd_options = {'page-width': 95, 'page-height': 297, 'orientation': 'Portrait'}
        if patient['last_name']:
            self.filename = 'skierowanie_' + slugify(self.patient['last_name'])
        else:
            self.filename = 'skierowanie_' + self.now.strftime('%s')
        return super(ReferralPdfView, self).get(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        examinations = json.loads(self.request.GET['examinations'])
        patient = json.loads(self.request.GET['patient'])
        doctor = self.request.user.doctor
        today = datetime.today().strftime('%d/%m/%Y')
        ctx = {'examinations': examinations, 'doctor': doctor, 'patient': patient, 'date': today}
        if 'icd' in self.request.GET:
            ctx['icd'] = json.loads(self.request.GET['icd'])
        return ctx


