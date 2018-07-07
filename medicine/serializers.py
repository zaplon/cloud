from medicine.models import *
from rest_framework import serializers
from user_profile.rest import PatientSerializer, DoctorSerializer


class MedicineParentSerializer(serializers.ModelSerializer):

    class Meta:
        model = MedicineParent
        fields = '__all__'


# Serializers define the API representation.
class MedicineSerializer(serializers.ModelSerializer):
    parent = MedicineParentSerializer()

    class Meta:
        model = Medicine
        fields = '__all__'


# Serializers define the API representation.
class RefundationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Refundation
        fields = ('to_pay', 'recommendations', 'other_recommendations', 'id')


class MedicineToPrescriptionRetrieveSerializer(serializers.ModelSerializer):
    medicine = MedicineSerializer()
    refundation = RefundationSerializer()

    class Meta:
        model = MedicineToPrescription
        fields = '__all__'


class PrescriptionRetrieveSerializer(serializers.ModelSerializer):
    patient = PatientSerializer()
    doctor = DoctorSerializer()
    medicines = serializers.ListField(source='get_medicines')

    class Meta:
        model = Prescription
        fields = ['number', 'date', 'patient', 'doctor', 'medicines', 'permissions', 'nfz']


class MedicineToPrescriptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = MedicineToPrescription
        fields = '__all__'


class PrescriptionSerializer(serializers.ModelSerializer):
    # medicines = MedicineToPrescriptionSerializer(many=True)

    def save(self, **kwargs):
        instance = super(PrescriptionSerializer, self).save(**kwargs)
        for medicine in self.initial_data['medicines']:
            medicine['prescription'] = instance.id
            medicine_to_prescription = MedicineToPrescriptionSerializer(data=medicine)
            if medicine_to_prescription.is_valid():
                medicine_to_prescription.save()

    class Meta:
        model = Prescription
        fields = '__all__'


class PrescriptionListSerializer(serializers.ModelSerializer):
    patient = serializers.CharField(source='patient.__str__')
    doctor = serializers.CharField(source='doctor.__str__')

    class Meta:
        model = Prescription
        fields = ['id', 'number', 'date', 'patient', 'doctor']