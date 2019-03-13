import json

from django.urls import reverse

from g_utils.utils import GabinetTestCase
from medicine.models import MedicineParent, Medicine
from django_dynamic_fixture import G


class MedicineParentTestCase(GabinetTestCase):

    def setUp(self):
        super(MedicineParentTestCase, self).setUp()
        self.medicine_parent = G(MedicineParent)
        G(Medicine, parent=self.medicine_parent, ean='22222')

    def test_medicine_viewset_returns_children(self):
        url = reverse('rest:medicines-list')
        res = self.client.get(url, {'parent': self.medicine_parent.pk})
        self.assertEqual(len(res.json()['results']), 1)
        res = self.client.get(url, {'parent': 2})
        self.assertEqual(len(res.json()['results']), 0)

    def test_saving_medicine_with_children(self):
        url = reverse('rest:medicine_parents-detail', kwargs={'pk': self.medicine_parent.id})
        data = {'children': [{'size': 100, 'ean': '123456789', 'refundation': True}]}
        res = self.client.patch(url, json.dumps(data), content_type='application/json')
        self.assertEqual(res.status_code, 200)
        self.assertTrue(Medicine.objects.filter(ean='123456789').exists())
