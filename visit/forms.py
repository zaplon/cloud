# -*- coding: utf-8 -*-
from crispy_forms.layout import HTML
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout
from django.forms import ModelForm
from django.urls import reverse
from .models import Template, Tab
from django.forms import HiddenInput


class TemplateForm(ModelForm):
    class Meta:
        model = Template
        fields = ['name', 'key', 'text', 'tab', 'doctor']

    def __init__(self, *args, **kwargs):
        super(TemplateForm, self).__init__(*args, **kwargs)
        self.fields['doctor'].widget = HiddenInput()
        self.helper = FormHelper()
        helper = self.helper
        # helper.form_class = 'form-horizontal'
        # helper.label_class = 'col-md-2'
        # helper.field_class = 'col-md-8'
        helper.layout = Layout(
            'name',
            'key',
            'text',
            'tab',
            HTML('<button class="btn btn-success" type="submit">Zapisz</button>')
        )


class TabForm(ModelForm):
    class Meta:
        model = Tab
        fields = ['title', 'template', 'doctor', 'enabled']

    def __init__(self, *args, **kwargs):
        super(TabForm, self).__init__(*args, **kwargs)
        self.fields['doctor'].widget = HiddenInput()
        self.helper = FormHelper()
        helper = self.helper
        helper.field_template = 'form/field.html'
        # helper.form_class = 'form-horizontal'
        # helper.label_class = 'col-md-2'
        # helper.field_class = 'col-md-8'
        helper.layout = Layout(
            'title',
            'template',
            'enabled',
            HTML('<button class="btn btn-success mr-025" type="submit">Zapisz</button>'),
            HTML(
                u'<a class="btn btn-danger" href="%s">Usuń</a>' % reverse('tab-delete', kwargs={'pk': self.instance.id})
                if self.instance.id else '')
        )
