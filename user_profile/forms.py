# -*- coding: utf-8 -*-
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit, Field, Layout, Div, HTML
from django import forms
from django.forms.fields import TimeField


class HoursForm(forms.Form):
    start = TimeField()
    end = TimeField()
    break_start = TimeField(required=False)
    break_end = TimeField(required=False)

    def clean(self):
        pass


class DoctorForm(forms.Form):
    first_name = forms.CharField(max_length=100, label=u'Imię')
    last_name = forms.CharField(max_length=100, label=u'Nazwisko')
    email = forms.EmailField(label=u'Adres email')
    mobile = forms.CharField(max_length=9, label=u'Numer telefonu', required=False)
    pwz = forms.CharField(max_length=7, label=u'Numer PWZ')

    def __init__(self, *args, **kwargs):
        super(DoctorForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.wrapper_class = 'row'
        self.helper.label_class = 'col-md-2'
        self.helper.field_class = 'col-md-10'
        self.helper.add_layout(Layout(
            Field('first_name', css_class='form-control', wrapper_class='row'),
            Field('last_name', css_class='form-control', wrapper_class='row'),
            Field('email', css_class='form-control', wrapper_class='row'),
            Field('mobile', css_class='form-control', wrapper_class='row'),
            Field('pwz', css_class='form-control', wrapper_class='row')
        ))
