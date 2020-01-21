import json

from django.urls import reverse

from g_utils.utils import GabinetTestCase
from medicine.models import MedicineParent, Medicine
from django_dynamic_fixture import G

from user_profile.models import Patient, Doctor, PrescriptionNumber


class MedicineParentTestCase(GabinetTestCase):

    def setUp(self):
        super(MedicineParentTestCase, self).setUp()
        self.medicine_parent = G(MedicineParent)
        G(Medicine, parent=self.medicine_parent, ean='22222')

    def test_medicine_viewset_returns_children(self):
        url = reverse('rest:medicines-list')
        res = self.client.get(url, {'parent': self.medicine_parent.pk})
        self.assertEqual(len(res.json()['results']), 1)

    def test_saving_medicine_with_children(self):
        url = reverse('rest:medicine_parents-detail', kwargs={'pk': self.medicine_parent.id})
        data = {'children': [{'size': 100, 'ean': '123456789', 'refundation': True}]}
        res = self.client.patch(url, json.dumps(data), content_type='application/json')
        self.assertEqual(res.status_code, 200)
        self.assertTrue(Medicine.objects.filter(ean='123456789').exists())


class PrescriptionTestCase(GabinetTestCase):

    def setUp(self):
        super().setUp()
        doctor = G(Doctor, id=1, user=self.user)
        G(Patient, id=1)
        G(PrescriptionNumber, doctor=doctor)
        self.prescription_data = {"patient": 1, "doctor": 1, "medicines": [
            {"medicine_id": 51230, "dosage": "2x1", "amount": "40", "notes": "uwaga", "refundation": None}], "nfz": "7",
                                  "realisation_date": "2019-11-06", "permissions": "X", "number": '123',
                                  "date": "2019-11-06T23:00:00.000Z"}

    def test_creating_prescription(self):
        # url = reverse('rest:prescriptions-create')
        url = '/rest/prescriptions/'
        res = self.client.post(url, json.dumps(self.prescription_data), content_type='application/json')
        self.assertEqual(res.status_code, 201)
        response_json = res.json()
        self.assertEqual(response_json['patient'], 1)
