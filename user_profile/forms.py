# -*- coding: utf-8 -*-
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit, Field, Layout, Div, HTML
from django import forms
from django.forms.fields import TimeField
from django.forms.widgets import HiddenInput

from user_profile.models import Patient, Specialization, SystemSettings
from localflavor.pl.forms import PLPESELField


class HoursForm(forms.Form):
    start = TimeField()
    end = TimeField()
    break_start = TimeField(required=False)
    break_end = TimeField(required=False)

    def clean(self):
        pass


class UserForm(forms.Form):
    first_name = forms.CharField(max_length=100, label=u'Imię')
    last_name = forms.CharField(max_length=100, label=u'Nazwisko')
    email = forms.EmailField(label=u'Adres email')
    mobile = forms.CharField(max_length=9, label=u'Numer telefonu', required=False)
    form_class = forms.CharField(max_length=50, initial='UserForm', widget=HiddenInput(), required=False)

    def __init__(self, *args, **kwargs):
        super(UserForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.wrapper_class = 'row'
        self.helper.label_class = 'col-md-2'
        self.helper.field_class = 'col-md-10'
        self.helper.add_layout(Layout(
            Field('first_name', css_class='form-control', wrapper_class='row'),
            Field('last_name', css_class='form-control', wrapper_class='row'),
            Field('email', css_class='form-control', wrapper_class='row'),
            Field('mobile', css_class='form-control', wrapper_class='row'),
            Field('form_class', css_class='form-control', wrapper_class='row')
        ))

    def clean_mobile(self):
        if self.cleaned_data['mobile'] == '':
            return None
        return int(self.cleaned_data['mobile'])

    def save(self, user):
        user.first_name = self.data['first_name']
        user.last_name = self.data['last_name']
        user.email = self.data['email']
        user.profile.mobile = self.cleaned_data['mobile']
        user.save()


class DoctorForm(forms.Form):
    first_name = forms.CharField(max_length=100, label=u'Imię')
    last_name = forms.CharField(max_length=100, label=u'Nazwisko')
    email = forms.EmailField(label=u'Adres email')
    mobile = forms.CharField(max_length=9, label=u'Numer telefonu', required=False)
    pwz = forms.CharField(max_length=7, label=u'Numer PWZ')
    title = forms.CharField(max_length=50, label=u'Tytuł')
    form_class = forms.CharField(max_length=50, initial='DoctorForm', widget=HiddenInput(), required=False)
    factory_specializations = forms.MultipleChoiceField(label=u'Specjalizacje', required=False,
                                                        help_text=u'Zaznacz kilka pozycji trzymając wciśnięty klawisz CTRL')

    def __init__(self, *args, **kwargs):
        super(DoctorForm, self).__init__(*args, **kwargs)
        self.fields['factory_specializations'].choices = [(s.id, s.name) for s in Specialization.objects.all()]
        if 'doctor' in self.initial:
            specs = list(Specialization.objects.filter(doctors=self.initial['doctor']).values_list('id', flat=True))
            self.fields['factory_specializations'].initial = specs
        self.helper = FormHelper()
        self.helper.wrapper_class = 'row'
        self.helper.label_class = 'col-md-2'
        self.helper.field_class = 'col-md-10'
        self.helper.add_layout(Layout(
            Field('title', css_class='form-control', wrapper_class='row'),
            Field('first_name', css_class='form-control', wrapper_class='row'),
            Field('last_name', css_class='form-control', wrapper_class='row'),
            Field('email', css_class='form-control', wrapper_class='row'),
            Field('mobile', css_class='form-control', wrapper_class='row'),
            Field('pwz', css_class='form-control', wrapper_class='row'),
            Field('factory_specializations', css_class='form-control', wrapper_class='row'),
            Field('form_class', css_class='form-control', wrapper_class='row')
        ))

    def clean_factory_specializations(self):
        return self.cleaned_data['factory_specializations']

    def clean_mobile(self):
        if self.cleaned_data['mobile'] == '':
            return None
        return int(self.cleaned_data['mobile'])

    def save(self, user):
        user.doctor.title = self.data['title']
        user.first_name = self.data['first_name']
        user.last_name = self.data['last_name']
        user.email = self.data['email']
        user.doctor.pwz = self.data['pwz']
        user.doctor.mobile = self.cleaned_data['mobile']
        user.save()
        user.doctor.save()
        if 'factory_specializations' in self.cleaned_data:
            user.doctor.specializations.clear()
            for s in self.cleaned_data['factory_specializations']:
                user.doctor.specializations.add(Specialization.objects.get(id=s))
            pass


class FullPatientForm(forms.Form):
    first_name = forms.CharField(max_length=100, label=u'Imię')
    last_name = forms.CharField(max_length=100, label=u'Nazwisko')
    email = forms.EmailField(label=u'Adres email')
    mobile = forms.CharField(max_length=9, label=u'Numer telefonu', required=False)

    def __init__(self, *args, **kwargs):
        super(FullPatientForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.wrapper_class = 'row'
        self.helper.label_class = 'col-md-2'
        self.helper.field_class = 'col-md-10'
        self.helper.add_layout(Layout(
            Field('first_name', css_class='form-control', wrapper_class='row'),
            Field('last_name', css_class='form-control', wrapper_class='row'),
            Field('email', css_class='form-control', wrapper_class='row'),
            Field('mobile', css_class='form-control', wrapper_class='row'),
        ))


class PatientForm(forms.Form):
    first_name = forms.CharField(max_length=100, label=u'Imię')
    last_name = forms.CharField(max_length=100, label=u'Nazwisko')
    email = forms.EmailField(label=u'Adres email', required=False)
    pesel = PLPESELField(label=u'Pesel', required=False)

    def save(self):
        Patient.objects.create(pesel=self.cleaned_data['pesel'], email=self.cleaned_data['email'],
                               first_name=self.cleaned_data['first_name'], last_name=self.cleaned_data['last_name'])
        return True


class PatientModelForm(forms.ModelForm):
    pesel = PLPESELField(label=u'Pesel', required=False)
    class Meta:
        model = Patient
        fields = ['first_name', 'last_name', 'pesel', 'email', 'info']


class SystemForm(forms.ModelForm):
    class Meta:
        model = SystemSettings
        fields = ['logo']

    def __init__(self):
        super(SystemForm, self).__init__()
        self.helper = FormHelper()
        self.helper.wrapper_class = 'row'
        self.helper.label_class = 'col-md-2'
        self.helper.field_class = 'col-md-10'
        self.helper.add_layout(Layout(
            Field('logo', css_class='form-control', wrapper_class='row')
        ))
