import json

from django.db.models import Q, Min
from rest_framework import serializers, viewsets
from rest_framework.fields import CharField, ListField
from rest_framework.response import Response
from rest_framework import status
from rest_framework.views import APIView
from django.contrib.auth.models import User, Permission
from django.conf import settings

from g_utils.rest import SearchMixin
from .models import Doctor, Patient, Note, Specialization
from datetime import datetime


# Serializers define the API representation.
class PatientSerializer(serializers.ModelSerializer):
    # first_name = CharField(source='user.first_name')
    # last_name = CharField(source='user.last_name')
    class Meta:
        model = Patient
        fields = ('id', 'mobile', 'first_name', 'last_name', 'pesel', 'address', 'name_with_pesel')


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
        if not request.user.is_authenticated() or not instance.doctor == request.user.doctor:
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
        self.instance.save()
        return self.instance


# Serializers define the API representation.
class DoctorSerializer(serializers.HyperlinkedModelSerializer):
    name = CharField(source='get_name')
    working_hours = ListField(source='get_working_hours')

    class Meta:
        model = Doctor
        fields = ('mobile', 'pwz', 'terms_start', 'terms_end', 'name', 'id', 'working_hours', 'available_prescriptions',
                  'total_prescriptions', 'visit_duration')
        
        
class DoctorCalendarSerializer(serializers.ModelSerializer):
    first_term = serializers.DateTimeField(format=settings.DATE_FORMAT)

    class Meta:
        model = Doctor
        fields = ('id', 'name', 'first_term', 'terms_start', 'terms_end')


# ViewSets define the view behavior.
class DoctorViewSet(viewsets.ModelViewSet, SearchMixin):
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
        if hasattr(self.request.user, 'doctor') and 'id' not in kwargs:
            return Doctor.objects.filter(user=self.request.user)
        else:
            get_params = self.request.GET
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
        return modules

    def check_if_setup_needed(self, instance):
        if hasattr(instance, 'doctor'):
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
                  'doctor', 'user_permissions')


class UserDetailsView(APIView):

    queryset = User.objects.none()

    def get(self, request):
        if not request.user.is_authenticated():
            return Response(status=403)
        return Response(UserSerializer(instance=request.user).data)


class SpecializationSerializer(serializers.ModelSerializer):

    class Meta:
        model = Specialization
        fields = '__all__'


class SpecializationViewSet(viewsets.ReadOnlyModelViewSet, SearchMixin):
    serializer_class = SpecializationSerializer
    queryset = Specialization.objects.all()
