# -*- coding: utf-8 -*-
from crispy_forms.layout import HTML
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout
from django.forms import ModelForm
from django.urls import reverse
from .models import Template, Tab
from django.forms import HiddenInput, Textarea
from django.utils.translation import ugettext as _


class TemplateForm(ModelForm):
    class Meta:
        model = Template
        fields = ['name', 'key', 'text', 'tab', 'doctor']

    def __init__(self, *args, **kwargs):
        super(TemplateForm, self).__init__(*args, **kwargs)
        self.fields['doctor'].widget = HiddenInput()
        self.fields['text'].widget = Textarea(attrs={'placeholder': _(u'Wpisz treść szablonu')})
        self.helper = FormHelper()
        helper = self.helper
        # helper.form_class = 'form-horizontal'
        # helper.label_class = 'col-md-2'
        # helper.field_class = 'col-md-8'
        if not 'ajax' in kwargs:
            helper.layout = Layout(
                'name',
                'key',
                'text',
                'tab',
                HTML('<hr/>'),
                HTML(u'<div class="pull-left"><a class="btn btn-danger" href="%s">Usuń</a></div>' %
                    reverse('template-delete', kwargs={'pk': self.instance.id})
                    if self.instance.id else ''),
                HTML('<div class="pull-right"><button class="btn btn-primary" type="submit">Zapisz</button>'),
                HTML('<a class="btn btn-default button-margin" href="/templates/">Anuluj</a></div><div class="clearfix"></div>')
            )
        else:
            helper.layout = Layout(
                'name',
                'key',
                'text',
                'tab'
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
            HTML(
                u'<hr/><div class="pull-left"><a class="btn btn-danger" href="%s">Usuń</a></div>' %
                reverse('tab-delete', kwargs={'pk': self.instance.id})
                if self.instance.id else ''),
            HTML("""
                 <div class="pull-right"><button class="btn btn-primary mr-025" type="submit">Zapisz</button>
                 <a class="btn btn-default" href="/tabs/">Anuluj</a></div><div class='clearfix'/>"""),
        )
