# -*- coding: utf-8 -*-
from django.forms import Form, Textarea, IntegerField, ModelForm
from django.forms.fields import CharField, FileField, HiddenInput
from django.http import HttpResponse

from user_profile.models import Patient
from visit.models import Visit
from .models import Result
from django.conf import settings
from g_utils.fields import AutocompleteWidget


class ResultModelForm(ModelForm):
    class Meta:
        model = Result
        fields = ['name', 'file', 'description', 'patient', 'specialization']

    def __init__(self, *args, **kwargs):
        super(ResultModelForm, self).__init__(*args, **kwargs)
        self.fields['description'].widget = Textarea()
        self.fields['patient'].widget = AutocompleteWidget(url='/rest/patients/')
        if self.instance.id:
            self.fields['patient'].widget.display = self.instance.patient.name


class ResultForm(Form):
    name = CharField(max_length=100, required=True, label=u'Nazwa pliku')
    file = FileField(label=u'Plik')
    description = CharField(max_length=500, widget=Textarea(), required=False, label=u'Opis')
    visit = IntegerField(widget=HiddenInput())
    patient = IntegerField(widget=HiddenInput())
    module = CharField(max_length=30, widget=HiddenInput(), initial='result.forms')
    klass = CharField(max_length=30, widget=HiddenInput(), initial='ResultForm')

    def save(self):
        if settings.USE_ELO:
            return HttpResponse(status=200)
        v = Visit.objects.get(id=self.cleaned_data['visit'])
        Result.objects.create(doctor=v.term.doctor, description=self.cleaned_data['description'], name=self.cleaned_data['name'],
                              patient=Patient.objects.get(id=self.cleaned_data['patient']),
                              visit=v, file=self.cleaned_data['file'])
        return HttpResponse(status=200)

