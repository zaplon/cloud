# -*- coding: utf-8 -*-
from crispy_forms.layout import HTML
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout
from django.forms import ModelForm
from django.urls import reverse
from .models import Template, Tab, TabTypes
from django.forms import HiddenInput, Textarea
from django.utils.translation import ugettext as _


class TemplateForm(ModelForm):
    save_with_user = True
    horizontal = True

    class Meta:
        model = Template
        fields = ['id', 'name', 'key', 'text', 'tab', 'doctor']

    def clean_tab(self):
        tab = self.cleaned_data['tab']
        return tab

    def __init__(self, *args, **kwargs):
        super(TemplateForm, self).__init__(*args, **kwargs)
        self.fields['doctor'].widget = HiddenInput()
        self.fields['text'].widget = Textarea(attrs={'placeholder': _(u'Wpisz treść szablonu'), 'rows': 10})
        data = kwargs['initial'] if 'initial' in kwargs else kwargs['data'] if 'data' in kwargs else {}
        if 'instance' in kwargs:
            data['user'] = kwargs['instance'].doctor.user

        self.fields['tab'].queryset = Tab.objects.all().filter(doctor__user=data['user'], type=TabTypes.DEFAULT.name)
        self.helper = FormHelper()
        helper = self.helper
        # helper.form_class = 'form-horizontal'
        # helper.label_class = 'col-md-2'
        # helper.field_class = 'col-md-8'
        helper.layout = Layout(
            'name',
            'key',
            'text',
            'tab'
        )

    def save(self, user=False, commit=True):
        self.instance.doctor = user.doctor
        super(TemplateForm, self).save(commit)


class TabForm(ModelForm):
    save_with_user = True

    class Meta:
        model = Tab
        fields = ['id', 'title', 'enabled', 'order', 'type']

    def save(self, user=False, commit=True):
        self.instance.doctor = user.doctor
        super(TabForm, self).save(commit)

    def __init__(self, *args, **kwargs):
        super(TabForm, self).__init__(*args, **kwargs)
        # self.fields['parent'].widget = HiddenInput()
        self.fields['type'].initial = TabTypes.DEFAULT.name
        self.helper = FormHelper()
        helper = self.helper
        helper.field_template = 'form/field.html'
        # helper.form_class = 'form-horizontal'
        # helper.label_class = 'col-md-2'
        # helper.field_class = 'col-md-8'
        helper.layout = Layout(
            'title',
            'order',
            'enabled',
            'type',
            # HTML(
            #     u'<hr/><div class="pull-left"><a class="btn btn-danger" href="%s">Usuń</a></div>' %
            #     reverse('tab-delete', kwargs={'pk': self.instance.id})
            #     if self.instance.id and self.instance.parent.template == 'default.html' else ''),
            # HTML("""
            #      <div class="pull-right"><button class="btn btn-primary mr-025" type="submit">Zapisz</button>
            #      <a class="btn btn-default" href="/tabs/">Anuluj</a></div><div class='clearfix'/>"""),
        )
