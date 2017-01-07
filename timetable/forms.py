from django.forms import ModelForm
from django.forms.utils import flatatt
from django.utils.html import format_html
from django.utils.safestring import mark_safe

from .models import Term
from django.forms.widgets import Select


class PatientSelect(Select):

    def render(self, name, value, attrs=None):
        if value is None:
            value = ''
        final_attrs = self.build_attrs(attrs, name=name)
        output = [format_html('<div class="col-md-9"><select{}></div>', flatatt(final_attrs))]
        options = self.render_options([value])
        if options:
            output.append(options)
        output.append('</select>')
        output.append('</div><div class="col-md-3"><div class="btn btn-sm" id="get-add-patient-form">'
                      '<i class="fa fa-plus" title="Dodaj pacjenta"></i></div></div>')
        html =  mark_safe('\n'.join(output))
        html = '<div class="row">' + html + '</div>'
        return html


class TermForm(ModelForm):
    class Meta:
        model = Term
        fields = ['patient', 'status']
        widgets = {
            'patient': PatientSelect(),
        }
