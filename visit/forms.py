from crispy_forms.layout import HTML
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout
from django.forms import ModelForm
from .models import Template, Tab
from django.forms import HiddenInput


class TemplateForm(ModelForm):
    class Meta:
        model = Template
        fields = ['name', 'title', 'key', 'text', 'tab']

    def __init__(self, *args, **kwargs):
        super(TemplateForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        helper = self.helper
        #helper.form_class = 'form-horizontal'
        #helper.label_class = 'col-md-2'
        #helper.field_class = 'col-md-8'
        helper.layout = Layout(
            'name',
            'title',
            'key',
            'text',
            'tab',
            HTML('<button class="btn btn-success" type="submit">Zapisz</button>')
        )


class TabForm(ModelForm):
    class Meta:
        model = Tab
        fields = ['title', 'template', 'doctor']

    def __init__(self, *args, **kwargs):
        super(TabForm, self).__init__(*args, **kwargs)
        self.fields['doctor'].widget = HiddenInput()
        self.helper = FormHelper()
        helper = self.helper
        #helper.form_class = 'form-horizontal'
        #helper.label_class = 'col-md-2'
        #helper.field_class = 'col-md-8'
        helper.layout = Layout(
            'title',
            'template',
            HTML('<button class="btn btn-success" type="submit">Zapisz</button>')
        )

