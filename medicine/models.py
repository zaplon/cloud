from __future__ import unicode_literals

from django.core.exceptions import ValidationError
from django.db import models

from g_utils.models import SoftDeleteModel
from user_profile.models import Patient, Doctor
from visit.models import Visit


class MedicineParent(models.Model):
    class Meta:
        ordering = ('name', )
    name = models.CharField(max_length=200)
    composition = models.TextField(blank=True, null=True)  # sklad 1 i 2
    manufacturer = models.TextField(blank=True, null=True)  # Wytworca
    manufacturer_country = models.CharField(max_length=50, blank=True, null=True)  # kraj wytworcy
    permission_nr = models.CharField(max_length=20, blank=True, null=True)  # Numer pozwolenia tylko 1 i 3
    form = models.TextField(blank=True, null=True)  # Postac farmaceutyczna
    mah = models.TextField(blank=True, null=True)  # Podmiot odpowiedzialny
    inn = models.TextField(blank=True, null=True)  # Nazwa INN  tylko 3
    importer = models.TextField(blank=True, null=True)  # Importer rownolegly #tylko 3
    dose = models.TextField(blank=True, null=True)  # Dawka
    user_id = models.IntegerField(blank=True, null=True)
    external_id = models.IntegerField(db_index=True)
    in_use = models.BooleanField(default=True)
    refundation = models.BooleanField(blank=False, default=False)


class Medicine(models.Model):
    parent = models.ForeignKey(MedicineParent, related_name='children', on_delete=models.CASCADE)
    size = models.TextField(blank=True, null=True)  # Wielkosc opakowania
    availability_cat = models.TextField(blank=True, null=True)  # Kat. dost.
    ean = models.CharField(max_length=20, blank=True, null=True)  # Kod EAN
    in_use = models.BooleanField(default=True)
    refundation = models.BooleanField(blank=False, default=False)
    external_id = models.IntegerField(blank=True, null=True, db_index=True)


class Refundation(models.Model):
    substance = models.CharField(max_length=100, blank=True, null=True)
    name = models.CharField(max_length=200, blank=True, null=True)
    size = models.CharField(max_length=150, blank=True, null=True)
    ean = models.CharField(max_length=20, blank=True, null=False)
    group = models.CharField(max_length=200, blank=True, null=True)
    netto = models.CharField(max_length=15, blank=True, null=True)
    brutto = models.CharField(max_length=15, blank=True, null=True)
    detal = models.CharField(max_length=15, blank=True, null=True)
    limit = models.CharField(max_length=15, blank=True, null=True)
    recommendations = models.CharField(max_length=400, blank=True, null=True)
    other_recommendations = models.CharField(max_length=400, blank=True, null=True)
    to_pay = models.CharField(max_length=10, blank=True, null=True)
    patient_price = models.CharField(max_length=10, blank=True, null=True)
    medicine = models.ForeignKey(Medicine, related_name='refundations', on_delete=models.CASCADE)


class MedicineToPrescription(models.Model):
    medicine_id = models.IntegerField(db_index=True, blank=True, null=True)
    prescription = models.ForeignKey('Prescription', on_delete=models.CASCADE)
    dosage = models.CharField(max_length=128, default='')
    amount = models.CharField(max_length=128, default='')
    notes = models.CharField(max_length=128, blank=True, null=True)
    refundation = models.CharField(max_length=10, blank=True)
    prescription = models.ForeignKey('Prescription', related_name='medicines', on_delete=models.CASCADE)
    external_id = models.CharField(max_length=64, blank=True)
    number = models.CharField(max_length=32, blank=True, null=True)
    composition = models.TextField(blank=True)
    composition_name = models.CharField(max_length=256, blank=True)

    @property
    def medicine(self):
        return Medicine.objects.get(id=self.medicine_id)

    def clean(self, *args, **kwargs):
        if not (self.medicine_id or self.composition):
            raise ValidationError('Medicine needs to have composition or medicine_id filled.')
        super().clean(*args, **kwargs)


class Prescription(SoftDeleteModel):
    class Meta:
        ordering = ('-date', )

    number = models.CharField(max_length=32, blank=True, null=True)
    date = models.DateTimeField(auto_now_add=True)
    patient = models.ForeignKey(Patient, related_name='prescriptions', on_delete=models.CASCADE)
    doctor = models.ForeignKey(Doctor, related_name='prescriptions', on_delete=models.CASCADE)
    nfz = models.CharField(max_length=16)
    permissions = models.CharField(max_length=16)
    number_of_medicines = models.IntegerField(default=0)
    realisation_date = models.DateField()
    external_id = models.CharField(max_length=128, blank=True)
    external_code = models.CharField(max_length=32, blank=True)
    visit = models.ForeignKey(Visit, null=True, blank=True, related_name='prescriptions', on_delete=models.CASCADE)
    tmp = models.BooleanField(default=False)
    # body = models.CharField(max_length=512)

    def get_medicines(self):
        from medicine.serializers import MedicineToPrescriptionRetrieveSerializer
        medicines_to_prescription = MedicineToPrescription.objects.filter(prescription_id=self.id)
        medicines_to_prescription = [MedicineToPrescriptionRetrieveSerializer(instance=med) for med in
                                     medicines_to_prescription]
        return [med.data for med in medicines_to_prescription]

    @staticmethod
    def create(doctor, patient, prescription_data, medicines_data):
        p = Prescription.objects.create(doctor=doctor, number=prescription_data['number'], patient=patient,
                                        nfz=prescription_data['nfz'], permissions=prescription_data['permissions'],
                                        number_of_medicines=len(medicines_data),
                                        realisation_date=prescription_data['realisationDate'].split('T')[0])
        for m in medicines_data:
            refundation = int(m['refundation'])
            refundation = refundation if refundation > 0 else None
            MedicineToPrescription.objects.create(prescription=p, medicine_id=m['size'], dosage=m['dosage'],
                                                  amount=m['amount'], notes=m.get('notes', ''),
                                                  refundation_id=refundation)
        return True


class PrescriptionJob(models.Model):
    job_id = models.CharField(max_length=128)
    prescription = models.ForeignKey(Prescription, on_delete=models.CASCADE)
    finished = models.BooleanField(default=False)
