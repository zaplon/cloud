from django.urls import reverse

from g_utils.utils import GabinetTestCase
from medicine.models import MedicineParent, Medicine
from django_dynamic_fixture import G


class MedicineParentTestCase(GabinetTestCase):

    def setUp(self):
        super(MedicineParentTestCase, self).setUp()
        self.medicine_parent = G(MedicineParent)
        G(Medicine, parent=self.medicine_parent)

    def test_medicine_viewset_returns_children(self):
        url = reverse('rest:medicines-list')
        res = self.client.get(url, {'parent': self.medicine_parent.pk})
        self.assertEqual(len(res.json()['results']), 1)
        res = self.client.get(url, {'parent': 2})
        self.assertEqual(len(res.json()['results']), 0)
