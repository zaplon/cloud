from medicine.models import *
from rest_framework import serializers
from user_profile.rest import PatientSerializer, DoctorSerializer


class MedicineParentSerializer(serializers.ModelSerializer):

    class Meta:
        model = MedicineParent
        fields = '__all__'


# Serializers define the API representation.
class MedicineSerializer(serializers.ModelSerializer):
    parent = MedicineParentSerializer(read_only=True)

    class Meta:
        model = Medicine
        fields = '__all__'


# Serializers define the API representation.
class RefundationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Refundation
        fields = ('to_pay', 'recommendations', 'other_recommendations', 'id')


class MedicineToPrescriptionRetrieveSerializer(serializers.ModelSerializer):
    medicine = serializers.SerializerMethodField()
    refundation = RefundationSerializer()

    class Meta:
        model = MedicineToPrescription
        fields = '__all__'

    def get_medicine(self, instance):
        return MedicineSerializer(instance=Medicine.objects.get(id=instance.medicine_id)).data


class PrescriptionRetrieveSerializer(serializers.ModelSerializer):
    patient = PatientSerializer()
    doctor = DoctorSerializer()
    medicines = serializers.ListField(source='get_medicines')

    class Meta:
        model = Prescription
        fields = ['id', 'number', 'date', 'patient', 'doctor', 'medicines', 'permissions', 'nfz', 'external_id',
                  'external_code']


class MedicineToPrescriptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = MedicineToPrescription
        fields = '__all__'


class PrescriptionSerializer(serializers.ModelSerializer):
    medicines = MedicineToPrescriptionSerializer(many=True, read_only=True)

    class Meta:
        model = Prescription
        fields = ['id', 'number', 'date', 'medicines', 'patient', 'doctor', 'nfz', 'permissions', 'realisation_date',
                  'external_id', 'external_code', 'deleted']


class PrescriptionListSerializer(serializers.ModelSerializer):
    patient = serializers.CharField(source='patient.__str__')
    doctor = serializers.CharField(source='doctor.__str__')

    class Meta:
        model = Prescription
        fields = ['id', 'number', 'date', 'patient', 'doctor', 'number_of_medicines', 'external_id', 'external_code',
                  'deleted']
