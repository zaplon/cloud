from __future__ import unicode_literals

from django.db import models

from user_profile.models import Patient, Doctor


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
    external_id = models.IntegerField()
    in_use = models.BooleanField(default=True)


class Medicine(models.Model):
    parent = models.ForeignKey(MedicineParent, related_name='children', on_delete=models.CASCADE)
    size = models.TextField(blank=True, null=True)  # Wielkosc opakowania
    availability_cat = models.TextField(blank=True, null=True)  # Kat. dost.
    ean = models.CharField(max_length=20, blank=True, null=True)  # Kod EAN
    in_use = models.BooleanField(default=True)
    refundation = models.BooleanField(blank=False, default=False)
    external_id = models.IntegerField()


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
   medicine_id = models.IntegerField(db_index=True)
   prescription = models.ForeignKey('Prescription', on_delete=models.CASCADE)
   dosage = models.CharField(max_length=128, default='')
   amount = models.CharField(max_length=128, default='')
   notes = models.CharField(max_length=128, blank=True, null=True)
   refundation = models.ForeignKey(Refundation, blank=True, null=True, on_delete=models.CASCADE)
   prescription = models.ForeignKey('Prescription', related_name='medicines', on_delete=models.CASCADE)


class Prescription(models.Model):
    class Meta:
        ordering = ('-date', )

    number = models.CharField(max_length=16, blank=True, null=True)
    date = models.DateTimeField(auto_now_add=True)
    patient = models.ForeignKey(Patient, related_name='prescriptions', on_delete=models.CASCADE)
    doctor = models.ForeignKey(Doctor, related_name='prescriptions', on_delete=models.CASCADE)
    nfz = models.CharField(max_length=16)
    permissions = models.CharField(max_length=16)
    number_of_medicines = models.IntegerField(default=0)
    realisation_date = models.DateField()
    # body = models.CharField(max_length=512)

    def get_medicines(self):
        from medicine.serializers import MedicineToPrescriptionRetrieveSerializer
        medicines_to_prescription = MedicineToPrescription.objects.filter(prescription_id=self.id)
        medicines_to_prescription = [MedicineToPrescriptionRetrieveSerializer(instance=med) for med in
                                     medicines_to_prescription]
        # medicines_to_prescription = [med.is_valid() for med in medicines_to_prescription]
        return [med.data for med in medicines_to_prescription]

