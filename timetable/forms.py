from django.core.exceptions import ValidationError
from django.forms import ModelForm
from django.utils.safestring import mark_safe

from g_utils.fields import AutocompleteWidget
from .models import Term, Service, Localization
from django.forms.widgets import HiddenInput, DateTimeInput


class PatientSelect(AutocompleteWidget):

    def render(self, name, value, attrs=None):
        output = super(PatientSelect, self).render(name, value, attrs)
        output = ['<div class="col-md-9">%s' % output]
        output.append('</div><div class="col-md-3"><div class="btn btn-sm" id="get-add-patient-form">'
                      '<i class="fa fa-plus" title="Dodaj pacjenta"></i></div></div>')
        html = mark_safe('\n'.join(output))
        html = '<div class="row">' + html + '</div>'
        return html


class TermForm(ModelForm):
    class Meta:
        model = Term
        fields = ['patient', 'datetime', 'doctor', 'service', 'id', 'duration', 'status']
        widgets = {
            'patient': PatientSelect(url='/rest/patients/'),
            'doctor': HiddenInput(),
            'id': HiddenInput(),
            'datetime': DateTimeInput(format='%Y-%m-%d %H:%M'),
            'status': HiddenInput()
        }

    def clean_patient(self):
        if self.data['status'] == 'FREE' and not 'patient' in self.data:
            raise ValidationError(u'Wybierz pacjenta')
        else:
            return self.cleaned_data['patient']

    def __init__(self, *args, **kwargs):
        #kwargs['instance'].datetime.replace(tzinfo=None)
        super(TermForm, self).__init__(*args, **kwargs)
        if self.instance and self.instance.patient:
            self.fields['patient'].widget.display = self.instance.patient.__str__()

    def save(self, commit=True):
        if self.data['patient'] and self.instance.status == 'FREE':
            self.instance.status = u'PENDING'
        if 'patient' not in self.data or not self.data['patient']:
            self.instance.status = u'FREE'
        super(TermForm, self).save(commit)


class ServiceForm(ModelForm):
    horizontal = True

    class Meta:
        model = Service
        fields = '__all__'


class LocalizationForm(ModelForm):
    horizontal = True

    class Meta:
        model = Localization
        fields = '__all__'
