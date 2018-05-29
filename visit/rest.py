from django.db.models import Q
from rest_framework import serializers, viewsets
from rest_framework.fields import CharField
from rest_framework.response import Response

from g_utils.rest import OnlyDoctorRecords
from timetable.models import Term
from .models import Icd10, Template, Visit, VisitTab, Tab, TabParent, TabTypes
import json


# Serializers define the API representation.
class IcdSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Icd10
        fields = ('id', 'code', 'desc')


# ViewSets define the view behavior.
class IcdViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Icd10.objects.all()
    serializer_class = IcdSerializer

    def get_queryset(self):
        q = super(IcdViewSet, self).get_queryset()
        if 'search' in self.request.GET:
            term = self.request.GET['search']
            q = q.filter(Q(desc__icontains=term) | Q(code__icontains=term))
        if 'exclude' in self.request.GET:
            q = q.exclude(id__in=json.loads(self.request.GET['exclude']))
        return q


class TemplateSerializer(serializers.ModelSerializer):
    tab_name = CharField(source='tab.name')
    class Meta:
        model = Template
        fields = ('text', 'tab', 'key', 'name', 'tab_name')


class TemplateViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Template.objects.all()
    serializer_class = TemplateSerializer
    # pagination_class = None

    def get_queryset(self):
        q = super(TemplateViewSet, self).get_queryset()
        #q = q.filter(doctor__user=self.request.user)
        if self.request.GET.get('tab', None):
            q = q.filter(tab__id=self.request.GET['tab'])
        return q


class TabSerializer(serializers.ModelSerializer):
    type = serializers.CharField(source='parent.type')

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
    class Meta:
        model = Visit
        fields = ['id', 'tabs', 'in_progress']


class VisitViewSet(viewsets.ModelViewSet):
    queryset = Visit.objects.all()
    serializer_class = VisitSerializer

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
            rozpoznanie = filter(lambda d: d['type'] == TabParent.Types.ICD10, data)
            if len(rozpoznanie) == 0 or len(rozpoznanie[0]['data']) == 0:
                return Response(
                    json.dumps({'success': False, 'errors': {'rozpoznanie': u'Musisz podać rozpoznanie'}}),
                    content_type='application/json')

        for tab in data:
            vt = VisitTab.objects.get(id=tab['id'])
            vt.json = json.dumps(tab['data']) if 'data' in tab else ''
            vt.save()
            visit.tabs.add(vt)

            if vt.type == TabTypes.MEDICINES:
                pass

        if not int(tmp):
            term.status = 'finished'
            term.save()
        serializer = self.get_serializer(visit)
        return Response(serializer.data)