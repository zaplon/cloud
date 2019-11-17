import os
import copy
import uuid
import codecs
import requests
import json
from datetime import datetime

from django.template.loader import render_to_string
from django.conf import settings
from reportlab.graphics.barcode import createBarcodeDrawing
from reportlab.lib.units import cm
from rest_framework import viewsets, serializers, status
from rest_framework.decorators import action
from rest_framework.response import Response
from wkhtmltopdf.utils import wkhtmltopdf
from g_utils.rest import SearchMixin
from medicine.serializers import *
from user_profile.models import NFZSettings, SystemSettings, PrescriptionNumber
from user_profile.rest import NFZSettingsSerializer


class MedicineParentSerializer(serializers.ModelSerializer):
    class Meta:
        model = MedicineParent
        fields = '__all__'
    children = MedicineSerializer(write_only=True, many=True)

    def __init__(self, *args, **kwargs):
        super(MedicineParentSerializer, self).__init__(*args, **kwargs)
        if 'request' in kwargs['context']:
            self.user = kwargs['context']['request'].user
        else:
            self.user = None

    def create(self, validated_data):
        children = validated_data.pop('children')
        validated_data['user_id'] = self.user.id
        instance = super(MedicineParentSerializer, self).create(validated_data)
        for c in children:
            c.update({'parent': instance, 'in_use': True})
            Medicine.objects.create(**c)
        return instance

    def update(self, instance, validated_data):
        children = validated_data.pop('children')
        validated_data['user_id'] = self.user.id
        instance = super(MedicineParentSerializer, self).update(instance, validated_data)
        for c in children:
            c['parent'] = instance
            Medicine.objects.update_or_create(id=c.get('id', 0), defaults=c)
        return instance


# ViewSets define the view behavior.
class MedicineParentViewSet(SearchMixin, viewsets.ModelViewSet):
    queryset = MedicineParent.objects.filter(in_use=True)
    serializer_class = MedicineParentSerializer
    lookup_field = 'pk'

    def get_queryset(self):
        q = super(MedicineParentViewSet, self).get_queryset()
        search = None
        if 'query' in self.request.GET:
            search = self.request.GET['query']
        if 'search' in self.request.GET:
            search = self.request.GET['search']
        if search:
            q = q.filter(name__icontains=search) | q.filter(composition__icontains=search)
        return q


# ViewSets define the view behavior.
class MedicineViewSet(viewsets.ModelViewSet):
    queryset = Medicine.objects.all()
    serializer_class = MedicineSerializer
    filter_fields = ('parent', )

    def get_queryset(self):
        q = super(MedicineViewSet, self).get_queryset()
        if 'parent_name' in self.request.GET:
            q = q.filter(parent__name=self.request.GET['parent_name'])
        return q


# ViewSets define the view behavior.
class RefundationViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Refundation.objects.all()
    serializer_class = RefundationSerializer
    filter_fields = ('medicine', )
    pagination_class = None

    def get_queryset(self):
        q = super(RefundationViewSet, self).get_queryset()
        search = None
        if 'query' in self.request.GET:
            search = self.request.GET['query']
        if 'search' in self.request.GET:
            search = self.request.GET['search']
        if search:
            q = q.filter(ean=search)
        return q


# ViewSets define the view behavior.
class PrescriptionViewSet(SearchMixin, viewsets.ModelViewSet):
    queryset = Prescription.objects.all()
    serializer_class = PrescriptionSerializer
    search_filters = ['date', 'patient__first_name', 'patient__last_name']

    def _split_input_data(self, data):
        prescriptions_base = copy.deepcopy(data)
        prescriptions = []
        medicines = prescriptions_base.pop('medicines')
        n = 5
        chunks = [medicines[i * n:(i + 1) * n] for i in range((len(medicines) + n - 1) // n)]
        for chunk in chunks:
            prescription = copy.deepcopy(prescriptions_base)
            prescription['medicines'] = chunk
            if prescription.get('number'):
                prescription['number'] = PrescriptionNumber.objects.filter(doctor_id=prescription['doctor'],
                                                                           date_used__isnull=True).last().nr
            else:
                prescription.pop('number', False)
            prescriptions.append(prescription)
        return prescriptions

    def create(self, request):
        prescriptions = []
        for prescription in self._split_input_data(request.data):
            medicines = prescription.pop('medicines')
            serializer = self.get_serializer(data=prescription)
            serializer.is_valid(raise_exception=True)
            self.perform_create(serializer)
            self.save_medicines(serializer.instance, medicines)
            prescriptions.append(serializer.data)
        return Response(prescriptions, status=status.HTTP_201_CREATED)

    def _get_html(self, data, user):
        def _get_pwz(pwz):
            nr = ''.join(['0'] * (7 - len(pwz))) + pwz
            base = '30' + nr
            control_number = 0
            weights = [7, 9, 1, 3, 7, 9, 1, 7, 9]
            for i, val in enumerate(weights):
                try:
                    control_number += val * int(base[i])
                except KeyError:
                    control_number += 0
            control_number = control_number % 10
            return base + str(control_number)
        prescriptions = self._split_input_data(data)
        doctor = Doctor.objects.get(id=prescriptions[0]['doctor'])
        patient = Patient.objects.get(id=prescriptions[0]['patient'])

        barcode = createBarcodeDrawing('Code128', value=patient.pesel, width=5 * cm, height=0.5 * cm)
        barcode_pesel_filename = str(uuid.uuid4())
        barcode.save(formats=['png'], outDir=os.path.join(settings.MEDIA_ROOT, 'tmp', barcode_pesel_filename),
                     _renderPM_dpi=200)

        barcode = createBarcodeDrawing('Code128', value=_get_pwz(doctor.pwz), width=5 * cm, height=0.6 * cm)
        barcode_pwz_filename = str(uuid.uuid4())
        barcode.save(formats=['png'], outDir=os.path.join(settings.MEDIA_ROOT, 'tmp', barcode_pwz_filename),
                     _renderPM_dpi=200)

        context = {'user': doctor.user,
                   'barcodes': {
                       'pesel': f'tmp/{barcode_pesel_filename}', 'pwz': f'tmp/{barcode_pwz_filename}'
                   },
                   'doctor': doctor,
                   'patient': patient,
                   'prescriptions': prescriptions,
                   'APP_URL': settings.APP_URL}
        return render_to_string('pdf/prescriptions.html', context)

    def save_medicines(self, instance, medicines):
        number_of_medicines = 0
        for medicine in medicines:
            medicine['prescription'] = instance.id
            medicine_to_prescription = MedicineToPrescriptionSerializer(data=medicine)
            if medicine_to_prescription.is_valid():
                medicine_to_prescription.save()
                number_of_medicines += 1
        instance.number_of_medicines = number_of_medicines
        instance.save()

    @action(detail=False, methods=['post'])
    def save_in_p1(self, request):
        prescriptions = []
        for prescription in self._split_input_data(request.data):
            medicines = prescription.pop('medicines')
            serializer = self.get_serializer(data=prescription)
            serializer.is_valid(raise_exception=True)
            p1_data = self._prepare_for_p1(serializer.data, medicines)
            res = requests.post('http://prescriptions/api/save_prescription/', json.dumps(p1_data),
                                headers={'Content-type': 'application/json'})
            res_json = json.loads(res.content)
            if 'major' in res_json['wynik'] and res_json['wynik']['major'] == 'urn:csioz:p1:kod:major:Sukces':
                prescription = serializer.data
                prescription['external_id'] = \
                    res_json['potwierdzenieOperacjiZapisu']['wynikZapisuPakietuRecept']['kluczPakietuRecept']
                serializer = self.get_serializer(data=prescription)
                serializer.is_valid(raise_exception=True)
                nr = PrescriptionNumber.objects.filter(doctor_id=prescription['doctor'], date_used__isnull=True).last()
                nr.date_used = datetime.today()
                nr.save()
                self.perform_create(serializer)
                self.save_medicines(serializer.instance, medicines)
                prescriptions.append(serializer.data)
                return Response(prescriptions, status=status.HTTP_201_CREATED)
            else:
                return Response(res_json, status=status.HTTP_400_BAD_REQUEST)

    def _prepare_for_p1(self, prescription_data, medicines):
        patient = Patient.objects.get(id=prescription_data['patient'])
        pacjent = {
            'pesel': patient.pesel, 'imie': patient.first_name,
            'drugie_imie': patient.second_name, 'nazwisko': patient.last_name,
            'kod_pocztowy': patient.postal_code, 'miasto': patient.city,
            'numer_ulicy': patient.street_number, 'numer_lokalu': patient.apartment_number,
            'ulica': patient.street,
            'plec': 'M' if patient.gender == 'M' else 'K'
        }
        system_settings = SystemSettings.objects.get(id=1)
        podmiot = {
            'miasto': system_settings.city,
            'numer_domu': system_settings.street_number,
            'regon14': system_settings.regon,
            'ulica': system_settings.street
        }
        user = Doctor.objects.get(id=prescription_data['doctor']).user
        pracownik = {'imie': user.first_name, 'nazwisko': user.last_name}
        leki = []
        for m in medicines:
            medicine = Medicine.objects.get(id=m['medicine_id'])
            parent = medicine.parent
            tekst = f'{parent.name} {m["amount"]} {m["dosage"]}'
            if m['refundation']:
                tekst = f"{tekst} <br/>Odpłatność: {m['refundation']}"
            leki.append({'nazwa': parent.name, 'kategoria': medicine.availability_cat, 'ean': medicine.ean,
                         'tekst': tekst, 'postac': parent.form, 'wielkosc': m['amount']})
        recepta = {
            'oddzial_nfz': prescription_data['nfz'],
            'uprawnienia_dodatkowe': prescription_data['permissions'],
            'numer_recepty': prescription_data['number'],
            'data_wystawienia': datetime.today().strftime('%Y%m%d')}
        data = {'pacjent': pacjent,
                'pracownik': pracownik,
                'leki': leki,
                'recepta': recepta,
                'podmiot': podmiot,
                'profile': NFZSettingsSerializer(instance=NFZSettings.objects.get(id=user.id)).data}

        # tests
        data['podmiot']['regon14'] = '97619191000009'
        data['pacjent']['pesel'] = '70032816894'
        data['profile']['id_pracownika_oid_ext'] = '5992363'
        # for l in data['leki']:
        #     l['ean'] = '5909990001811'
        return data

    @action(detail=False, methods=['post'])
    def print(self, request):
        output_filename = f'{uuid.uuid4()}.pdf'
        output_filepath = os.path.join(settings.MEDIA_ROOT, 'tmp', output_filename)
        data = self._get_html(request.data, request.user)
        tmp_filepath = os.path.join(settings.MEDIA_ROOT, 'tmp', f'{uuid.uuid4()}.html')
        with codecs.open(tmp_filepath, 'w', encoding='utf-8') as f:
            f.write(data)
        wkhtmltopdf(tmp_filepath, output=output_filepath, page_width=90, page_height=210, margin_left=0,
                    margin_right=0, margin_top=0, margin_bottom=0)
        os.remove(tmp_filepath)
        return Response({'url': f'/media/tmp/{output_filename}'}, content_type='application/json',
                        status=status.HTTP_200_OK)

    def get_serializer_class(self):
        if self.action == 'list':
            return PrescriptionListSerializer
        if self.action == 'retrieve':
            return PrescriptionRetrieveSerializer
        return self.serializer_class

    def get_queryset(self):
        q = super(PrescriptionViewSet, self).get_queryset()
        if 'patient_id' in self.request.GET:
            q = q.filter(patient_id=self.request.GET['patient_id'])
        if 'only_filled' in self.request.GET:
            q = q.filter(medicines__isnull=False)
            q = q.distinct()
        return q.filter(doctor=self.request.user.doctor)
