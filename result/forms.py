from django.forms import Form, Textarea
from django.forms.fields import CharField, FileField, HiddenInput
from django.http import HttpResponse

from .models import Result
from django.conf import settings


class ResultForm(Form):
    name = CharField(max_length=100, required=True, label=u'Nazwa pliku')
    file = FileField(label=u'Plik')
    description = CharField(max_length=500, widget=Textarea(), required=False)
    module = CharField(max_length=30, widget=HiddenInput(), initial='result.forms')
    klass = CharField(max_length=30, widget=HiddenInput(), initial='ResultForm')

    def save(self):
        if settings.USE_ELO:
            return HttpResponse(status=200)


