from django.forms import Form, Textarea, IntegerField
from django.forms.fields import CharField, FileField, HiddenInput
from django.http import HttpResponse

from visit.models import Visit
from .models import Result
from django.conf import settings


class ResultForm(Form):
    name = CharField(max_length=100, required=True, label=u'Nazwa pliku')
    file = FileField(label=u'Plik')
    description = CharField(max_length=500, widget=Textarea(), required=False, label=u'Opis')
    visit = IntegerField(widget=HiddenInput())
    module = CharField(max_length=30, widget=HiddenInput(), initial='result.forms')
    klass = CharField(max_length=30, widget=HiddenInput(), initial='ResultForm')

    def save(self, user):
        if settings.USE_ELO:
            return HttpResponse(status=200)
        Result.objects.create(doctor=user.doctor, description=self.cleaned_data['description'],
                              visit=Visit.objects.get(id=self.cleaned_data['visit']), file=self.cleaned_data['file'])


