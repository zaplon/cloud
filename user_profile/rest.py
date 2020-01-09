import json

from OpenSSL import crypto
from OpenSSL.crypto import Error
from django.contrib.auth.password_validation import validate_password
from django.db.models import Q, Min
from rest_framework import serializers, viewsets, mixins
from rest_framework.exceptions import ValidationError
from rest_framework.fields import CharField, ListField
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.decorators import action
from django.contrib.auth.models import User, Permission, Group
from django.conf import settings

from g_utils.rest import SearchMixin
from timetable.models import Service, Term
from .models import Doctor, Patient, Note, Specialization, SystemSettings, NFZSettings, Profile
from datetime import datetime, date, timezone


# Serializers define the API representation.
class PatientSerializer(serializers.ModelSerializer):
    # first_name = CharField(source='user.first_name')
    # last_name = CharField(source='user.last_name')
    class Meta:
        model = Patient
        fields = ('id', 'mobile', 'first_name', 'last_name', 'pesel', 'address', 'name_with_pesel', 'info',
                  'street', 'street_number', 'city', 'postal_code', 'gender')

    def get_prescriptions(self, instance):
        pass


class PatientAutocompleteSerializer(serializers.ModelSerializer):
    label = CharField(source='name_with_pesel')
    value = CharField(source='name')

    class Meta:
        model = Patient
        fields = ('label', 'value', 'id')


# ViewSets define the view behavior.
class PatientViewSet(SearchMixin, viewsets.ModelViewSet):
    queryset = Patient.objects.all()
    serializer_class = PatientSerializer
    search_filters = ['last_name', 'first_name', 'pesel']

    def get_serializer_class(self):
        if 'term' in self.request.GET:
            return PatientAutocompleteSerializer
        else:
            return self.serializer_class

    @action(detail=False, methods=['get'])
    def last_served(self, request, *args, **kwargs):
        today = date.today()
        now = datetime.now(timezone.utc)
        terms = Term.objects.filter(doctor__user=request.user, datetime__date=today, patient__isnull=False)
        if not terms:
            return Response(status=404)
        closest_term = min(list(terms), key=lambda x: abs(x.datetime - now))
        data = PatientSerializer(instance=closest_term.patient).data
        return Response(data=data)


# Serializers define the API representation.
class NoteSerializer(serializers.ModelSerializer):
    author = CharField(source='get_author', required=False)

    class Meta:
        model = Note
        fields = ('id', 'text', 'patient', 'doctor', 'author', 'private')


# ViewSets define the view behavior.
class NoteViewSet(viewsets.ModelViewSet):
    queryset = Note.objects.all()
    serializer_class = NoteSerializer
    pagination_class = None

    def get_queryset(self):
        q = super(NoteViewSet, self).get_queryset()
        if 'patient' in self.request.GET:
            q = q.filter(patient__id= self.request.GET['patient'])
        return q

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        if not request.user.is_authenticated or not instance.doctor == request.user.doctor:
            return Response(status=status.HTTP_403_FORBIDDEN)
        self.perform_destroy(instance)
        return Response(status=status.HTTP_204_NO_CONTENT)


class WorkingHoursSerializer(serializers.ModelSerializer):
    working_hours = ListField(source='get_working_hours')

    class Meta:
        model = Doctor
        fields = ['id', 'working_hours', 'terms_start', 'terms_end']

    def save(self, **kwargs):
        days = self._kwargs['data']['days']
        self.instance.working_hours = json.dumps(days)
        working_days = list(filter(lambda d: d['on'], days))
        seq = [datetime.strptime(x['value'][0], '%H:%M') for x in working_days]
        min_time = min(seq)
        seq = [datetime.strptime(x['value'][1], '%H:%M') for x in working_days]
        max_time = max(seq)
        self.instance.terms_start = min_time.time()
        self.instance.terms_end = max_time.time()
        self.instance.terms_generated_till = datetime.today()
        self.instance.save()
        return self.instance


# Serializers define the API representation.
class DoctorSerializer(serializers.HyperlinkedModelSerializer):
    name = CharField(source='get_name')
    working_hours = ListField(source='get_working_hours')
    default_service = serializers.SerializerMethodField()
    default_archive_category = serializers.SerializerMethodField()
    has_many_services = serializers.SerializerMethodField()
    specializations = serializers.PrimaryKeyRelatedField(many=True, queryset=Specialization.objects.all())

    class Meta:
        model = Doctor
        fields = ('mobile', 'pwz', 'terms_start', 'terms_end', 'name', 'id', 'working_hours', 'available_prescriptions',
                  'total_prescriptions', 'visit_duration', 'default_service', 'has_many_services',
                  'specializations', 'default_archive_category')

    def get_default_service(self, obj):
        doctor_services = Service.objects.filter(doctors__in=[obj])
        if doctor_services.count() == 1:
            s = doctor_services.first()
            return {'id': s.id, 'name': s.name}

    def get_default_archive_category(self, obj):
        s = obj.specializations.first()
        if s:
            return SpecializationSerializer(instance=s).data

    def get_has_many_services(self, obj):
        return Service.objects.filter(doctors__in=[obj]).count() > 1

        
class DoctorCalendarSerializer(serializers.ModelSerializer):
    first_term = serializers.DateTimeField(format=settings.DATE_FORMAT)
    working_hours = ListField(source='get_working_hours')

    class Meta:
        model = Doctor
        fields = ('id', 'name', 'first_term', 'terms_start', 'terms_end', 'working_hours', 'visit_duration')


# ViewSets define the view behavior.
class DoctorViewSet(SearchMixin, viewsets.ModelViewSet):
    queryset = Doctor.objects.all()
    serializer_class = DoctorSerializer

    def get_serializer_class(self):
        if 'calendar' in self.request.GET:
            return DoctorCalendarSerializer
        elif 'only_hours' in self.request.GET or 'only_hours' in self.request.data:
            return WorkingHoursSerializer
        else:
            return self.serializer_class

    def get_queryset(self, *args, **kwargs):
        get_params = self.request.GET
        if 'calendar' not in get_params:
            return super().get_queryset()
        q = super(DoctorViewSet, self).get_queryset()
        if 'dateFrom' in get_params:
            dt = datetime.strptime(get_params['dateFrom'], '%Y-%m-%d')
        else:
            dt = datetime.today()
        if 'specialization' in get_params:
            q = q.filter(specializations__id=get_params['specialization'])
        if 'name_like' in get_params:
            q = q.filter(Q(user__first_name__icontains=get_params['name_like']) |
                         Q(user__last_name__icontains=get_params['name_like']))
        q = q.filter(terms__status='FREE', terms__datetime__gt=dt)
        q = q.annotate(first_term=Min('terms__datetime')).order_by('-first_term')
        return q


class UserDetailSerializer(serializers.ModelSerializer):
    doctor = DoctorSerializer(required=False)
    role_display = serializers.CharField(source='profile.role_display', read_only=True)

    class Meta:
        model = User
        fields = [f.name for f in User._meta.fields] + ['role_display', 'doctor']

    def update(self, instance, validated_data):
        instance = super(UserDetailSerializer, self).update(instance, validated_data)
        doctor = validated_data.pop('doctor', False)
        if doctor:
            doctor['working_hours'] = json.dumps(doctor.pop('get_working_hours'))
            specializations = doctor.pop('specializations')
            doctor, _ = Doctor.objects.update_or_create(user=instance, defaults=doctor)
            doctor.specializations.set(specializations)
        return instance


class UserInitSerializer(serializers.ModelSerializer):
    password = serializers.CharField()
    password2 = serializers.CharField(write_only=True)
    role = serializers.ChoiceField(choices=(('doctor', 'Lekarz'), ('admin', 'Administrator'),
                                            ('registration', 'Rejestracja')), write_only=True)
    doctor = DoctorSerializer(read_only=True, required=False)
    role_display = serializers.CharField(source='profile.role_display', read_only=True)
    role_name = serializers.CharField(source='profile.role', read_only=True)

    def validate_password(self, value):
        validate_password(value)
        return value

    def create(self, validated_data):
        password = validated_data.pop('password')
        role = validated_data.pop('role')
        validated_data.pop('password2')
        instance = super(UserInitSerializer, self).create(validated_data)
        instance.set_password(password)
        instance.save()
        Profile.objects.create(role=role, user=instance)
        if role == 'doctor':
            instance.groups.add(Group.objects.get(name='Lekarze'))
            Doctor.objects.create(user=instance)
        if role == 'admin':
            instance.groups.add(Group.objects.get(name='Administratorzy'))
        if role == 'registration':
            instance.groups.add(Group.objects.get(name='Rejestracja'))
        return instance

    def validate(self, data):
        if data.get('password2') != data.get('password'):
            raise serializers.ValidationError({'password': u'Hasła nie są jednakowe'})
        return data

    class Meta:
        model = User
        fields = ('id', 'username', 'first_name', 'last_name', 'password', 'password2', 'role', 'doctor',
                  'role_display', 'role_name')


class UserViewSet(SearchMixin, viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserDetailSerializer
    search_filters = ['last_name', 'first_name', 'username']

    def get_serializer_class(self):
        if self.action == 'create':
            return UserInitSerializer
        else:
            return self.serializer_class


class PermissionSerializer(serializers.ModelSerializer):

    class Meta:
        model = Permission
        fields = '__all__'


class UserSerializer(serializers.ModelSerializer):
    can_edit_terms = serializers.SerializerMethodField('check_if_can_edit_terms')
    can_edit_visits = serializers.SerializerMethodField('check_if_can_edit_visits')
    setup_needed = serializers.SerializerMethodField('check_if_setup_needed')
    modules = serializers.SerializerMethodField('get_user_modules')
    type = serializers.SerializerMethodField('get_user_type')
    doctor = DoctorSerializer()
    user_permissions = serializers.SerializerMethodField('get_all_permissions')
    system_settings = serializers.SerializerMethodField()
    css_theme = serializers.CharField(source='profile.css_theme')
    role = serializers.CharField(source='profile.role')

    def get_system_settings(self, instance):
        settings = SystemSettings.objects.first()
        nfz_settings = NFZSettings.objects.get(user=instance)
        return {'documents_header_left': settings.documents_header_left, 'logo': settings.logo.url,
                'regon': settings.regon, 'nip': settings.nip,
                'nfz_department': settings.nfz_department,
                'nfz': NFZSettingsSerializer(instance=nfz_settings).data,
                'documents_header_right': settings.documents_header_right}

    def get_all_permissions(self, instance):
        if instance.is_superuser:
            user_permissions = Permission.objects.all()
        else:
            user_permissions = instance.user_permissions.all()
        groups_permissions = Permission.objects.filter(group__user=instance)
        all_permissions = user_permissions | groups_permissions
        serializer = PermissionSerializer(all_permissions, many=True)
        return serializer.data

    def get_user_type(self, instance):
        try:
            instance.doctor
            return 'doctor'
        except:
            return 'user'

    def get_user_modules(self, instance):
        modules = []
        for module in settings.MODULES:
            if type(module[0]) == list:
                for m in module[0]:
                    if instance.has_perm(m):
                        modules.append(module[1])
            else:
                if module[0] is True or instance.has_perm(module[0]):
                    modules.append(module[1])
        if self.instance.is_staff:
            modules.append('admin')
        return modules

    def check_if_setup_needed(self, instance):
        if hasattr(instance, 'doctor') and instance.profile.role == 'doctor':
            d = instance.doctor
            if len(d.pwz) == 0 or len(d.user.last_name) == 0:
                return 1
            if d.working_hours is None:
                return 2
        else:
            u = instance
            if not u.last_name:
                return 1
        return 0

    def check_if_can_edit_terms(self, instance):
        return instance.has_perm('timetable.change_term')

    def check_if_can_edit_visits(self, instance):
        return instance.has_perm('visit.change_visit')

    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'can_edit_terms', 'can_edit_visits', 'setup_needed', 'modules', 'type',
                  'doctor', 'user_permissions', 'system_settings', 'css_theme', 'role')


class UserDetailsView(APIView):

    queryset = User.objects.none()

    def get(self, request):
        if not request.user.is_authenticated:
            return Response(status=403)
        return Response(UserSerializer(instance=request.user).data)


class SpecializationSerializer(serializers.ModelSerializer):

    class Meta:
        model = Specialization
        fields = '__all__'


class SpecializationViewSet(SearchMixin, viewsets.ReadOnlyModelViewSet):
    serializer_class = SpecializationSerializer
    queryset = Specialization.objects.all()


class PermissionSerializer(serializers.ModelSerializer):

    class Meta:
        model = Permission
        fields = '__all__'


class PermissionViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = PermissionSerializer
    queryset = Permission.objects.all()


class GroupSerializer(serializers.ModelSerializer):

    class Meta:
        model = Group
        fields = '__all__'


class GroupViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = GroupSerializer
    queryset = Group.objects.all()


class SystemSettingsSerializer(serializers.ModelSerializer):
    class Meta:
        model = SystemSettings
        fields = '__all__'


class SystemSettingsViewSet(mixins.RetrieveModelMixin, mixins.UpdateModelMixin, viewsets.GenericViewSet):
    serializer_class = SystemSettingsSerializer
    queryset = SystemSettings.objects.all()


class BookingSystemSettingsSerializer(serializers.ModelSerializer):
    class Meta:
        model = SystemSettings
        fields = ('documents_header_left', 'documents_header_right')


class InfoViewSet(viewsets.ReadOnlyModelViewSet):
    permission_classes = [AllowAny]
    serializer_class = BookingSystemSettingsSerializer
    queryset = SystemSettings.objects.all()


class NFZSettingsSerializer(serializers.ModelSerializer):
    class Meta:
        model = NFZSettings
        read_only_fields = ['id_pracownika_oid_ext', 'id_podmiotu_oid_root', 'id_podmiotu_oid_ext']
        fields = [f.name for f in NFZSettings._meta.get_fields()] + ['id_pracownika_oid_ext']

    def get_info_from_cert(self, attrs):
        cert_file = attrs.get('certificate_wsse') or self.instance.certificate_wsse
        if not cert_file:
            return attrs
        cert_password = attrs.get('certificate_wsse_password') or self.instance.certificate_wsse_password
        try:
            cert = crypto.load_pkcs12(cert_file.read(), cert_password).get_certificate()
        except Error:
            raise ValidationError({'certificate_wsse_password': 'Nie udało się odczytać certyfikatu przy użyciu podanego hasła.'})
        subject = cert.get_subject()
        id_root, id_ext = subject.serialNumber.replace(' ', '').split(':')
        attrs['id_podmiotu_oid_root'] = id_root
        attrs['id_podmiotu_oid_ext'] = id_ext
        return attrs

    def validate(self, attrs):
        attrs = self.get_info_from_cert(attrs)
        return super().validate(attrs)


class NFZSettingsViewSet(viewsets.ModelViewSet):
    serializer_class = NFZSettingsSerializer
    queryset = NFZSettings.objects.all()
