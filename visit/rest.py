from django.db.models import Q, Count
from rest_framework import serializers, viewsets
from rest_framework.fields import CharField
from rest_framework.mixins import DestroyModelMixin
from rest_framework.response import Response
from rest_framework.viewsets import ReadOnlyModelViewSet

from g_utils.rest import OnlyDoctorRecords, SearchMixin
from medicine.models import Prescription, MedicineToPrescription, Medicine
from medicine.serializers import PrescriptionSerializer
from timetable.models import Term
from timetable.rest import TermDetailSerializer
from .models import Icd10, Template, Visit, VisitTab, Tab, TabTypes, IcdToVisit
import json


class IcdToVisitSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(source='icd.id')
    code = serializers.CharField(source='icd.code')
    desc = serializers.CharField(source='icd.desc')

    class Meta:
        model = IcdToVisit
        fields = ('id', 'code', 'desc', 'custom_text')


# Serializers define the API representation.
class IcdSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Icd10
        fields = ('id', 'code', 'desc')


class PopularIcdSerializer(serializers.HyperlinkedModelSerializer):
    use_count = serializers.IntegerField()

    class Meta:
        model = Icd10
        fields = ('id', 'code', 'desc', 'use_count')


# ViewSets define the view behavior.
class IcdViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Icd10.objects.all()
    serializer_class = IcdSerializer

    def get_queryset(self):
        q = super(IcdViewSet, self).get_queryset()
        if 'search' in self.request.GET:
            term = self.request.GET['search']
            q = q.filter(Q(desc__icontains=term) | Q(code__icontains=term))
        if 'exclude' in self.request.GET and self.request.GET['exclude']:
            q = q.exclude(id__in=self.request.GET['exclude'].split(','))
        return q


class PopularIcdViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Icd10.objects.all()
    serializer_class = PopularIcdSerializer

    def get_queryset(self):
        q = super(PopularIcdViewSet, self).get_queryset()
        q = q.filter(visits__term__doctor=self.request.user.doctor)
        q = q.annotate(use_count=Count('visits__term__doctor__id')).order_by('-use_count')
        return q


class TemplateSerializer(serializers.ModelSerializer):
    tab_name = CharField(source='tab.name')
    tab_title = CharField(source='tab.title')
    class Meta:
        model = Template
        fields = ('text', 'tab', 'key', 'name', 'tab_title', 'tab_name', 'id')


class TemplateViewSet(SearchMixin, DestroyModelMixin, ReadOnlyModelViewSet):
    queryset = Template.objects.all()
    serializer_class = TemplateSerializer
    search_filters = ['name', 'text']

    def get_queryset(self):
        q = super(TemplateViewSet, self).get_queryset()
        q = q.filter(doctor__user=self.request.user)
        if self.request.GET.get('tab', None):
            q = q.filter(tab__id=self.request.GET['tab'])
        return q


class TabSerializer(serializers.ModelSerializer):
    type = serializers.CharField(source='type_name')

    class Meta:
        model = Tab
        fields = ('id', 'type', 'title', 'enabled', 'order')


class TabViewSet(OnlyDoctorRecords, viewsets.ModelViewSet):
    queryset = Tab.objects.all()
    serializer_class = TabSerializer
    pagination_class = None


class VisitTabSerializer(serializers.ModelSerializer):
    type = serializers.ReadOnlyField()

    class Meta:
        model = VisitTab
        fields = ['id', 'title', 'data', 'type']


class VisitSerializer(serializers.ModelSerializer):
    tabs = VisitTabSerializer(many=True)
    term = TermDetailSerializer()
    icdtovisit_set = IcdToVisitSerializer(many=True)

    class Meta:
        model = Visit
        fields = ['id', 'tabs', 'in_progress', 'term', 'icdtovisit_set']


class VisitViewSet(SearchMixin, viewsets.ModelViewSet):
    queryset = Visit.objects.filter(term__isnull=False)
    serializer_class = VisitSerializer
    fields_mapping = {'patient': 'term__patient__last_name', 'date': 'term__datetime'}
    search_filters = ['term__patient__last_name', 'term__patient__first_name', 'term__patient__pesel']

    def get_queryset(self):
        queryset = super(VisitViewSet, self).get_queryset()
        queryset.filter(doctor__user=self.request.user)
        return queryset

    def retrieve(self, request, *args, **kwargs):
        doctor = self.request.user.doctor
        term = Term.objects.get(id=kwargs['pk'])
        if not term.doctor == doctor:
            return Response(status=403)
        if not term.visit:
            visit = Visit.objects.create()
            term.visit = visit
            term.save()
        else:
            visit = term.visit
        visit.in_progress = True
        visit.save()
        tabs = visit.tabs.all()
        if len(tabs) == 0:
            tabs = visit.create_tabs()
        if len(tabs) > 0:
            tabs[0].is_active = True
        serializer = self.get_serializer(visit)
        return Response(serializer.data)

    def update(self, request, *args, **kwargs):
        term = Term.objects.get(id=kwargs['pk'])
        visit = term.visit
        doctor = self.request.user.doctor
        if not term.doctor == doctor:
            return Response(status=403)
        if request.POST.get('cancel', None):
            visit.in_progress = False
            visit.save()
            return Response(status=200)
        data = request.data['data']
        tmp = request.data.get('tmp', False)

        if not tmp:
            rozpoznanie = list(filter(lambda d: d['type'] == TabTypes.ICD10.name, data))
            if len(rozpoznanie) == 0 or len(rozpoznanie[0]['data']) == 0:
                return Response({'success': False, 'errors': {'rozpoznanie': u'Musisz podać rozpoznanie'}},
                                content_type='application/json')

        for tab in data:
            vt = VisitTab.objects.get(id=tab['id'])
            if vt.type == TabTypes.ICD10.name:
                visit.icdtovisit_set.all().delete()
                for d in tab['data']:
                    IcdToVisit.objects.create(icd_id=d['id'], custom_text=d.get('custom_text', ''), visit=visit)
            else:
                if vt.type == TabTypes.MEDICINES.name:
                    continue
                vt.json = json.dumps(tab['data']) if 'data' in tab else ''
                vt.save()
                visit.tabs.add(vt)

        if not int(tmp):
            term.status = 'FINISHED'
            term.save()
        serializer = self.get_serializer(visit)
        return Response(serializer.data)
