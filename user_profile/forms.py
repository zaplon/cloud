# -*- coding: utf-8 -*-
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit, Field, Layout, Div, HTML
from django import forms
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
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
    save_with_user = True
    horizontal = True

    first_name = forms.CharField(max_length=100, label=u'Imię')
    last_name = forms.CharField(max_length=100, label=u'Nazwisko')
    email = forms.EmailField(label=u'Adres email')
    mobile = forms.CharField(max_length=9, label=u'Numer telefonu', required=False)
    form_class = forms.CharField(max_length=50, initial='UserForm', widget=HiddenInput(), required=False)

    def __init__(self, *args, **kwargs):
        if 'user' in kwargs.get('initial', {}):
            u = kwargs['initial'].pop('user')
            kwargs['initial'] = {'first_name': u.first_name, 'last_name': u.last_name, 'email': u.email,
                                 'mobile': u.profile.mobile}
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


class UserModelForm(forms.ModelForm):

    class Meta:
        model = User
        exclude = ('is_staff',)


class DoctorForm(forms.Form):
    save_with_user = True
    horizontal = True

    first_name = forms.CharField(max_length=100, label=u'Imię')
    last_name = forms.CharField(max_length=100, label=u'Nazwisko')
    email = forms.EmailField(label=u'Adres email')
    mobile = forms.CharField(max_length=9, label=u'Numer telefonu', required=False)
    pwz = forms.CharField(max_length=7, label=u'Numer PWZ')
    title = forms.CharField(max_length=50, label=u'Tytuł')
    form_class = forms.CharField(max_length=50, initial='DoctorForm', widget=HiddenInput(), required=False)
    visit_duration = forms.IntegerField(min_value=5, required=True, label='Czas trwania wizyty',
                                        help_text='Liczba minut przypadających na jedną wizytę')
    factory_specializations = forms.MultipleChoiceField(label=u'Specjalizacje', required=False,
                                                        help_text=u'Zaznacz kilka pozycji trzymając wciśnięty klawisz CTRL')
    # documents_header_left = forms.Textarea(label=u'Nagłówek dokumentów (lewa strona)', required=False)
    # documents_header_right = forms.Textarea(label=u'Nagłówek dokumentów (prawa strona)', required=False)

    def __init__(self, *args, **kwargs):
        if 'user' in kwargs.get('initial', {}):
            u = kwargs['initial'].pop('user')
            kwargs['initial'] = {'first_name': u.first_name, 'last_name': u.last_name, 'email': u.email,
                                 'visit_duration': u.doctor.visit_duration,
                                 'mobile': u.profile.mobile, 'pwz': u.doctor.pwz, 'title': u.doctor.title}
        super(DoctorForm, self).__init__(*args, **kwargs)
        self.fields['factory_specializations'].choices = [(s.id, s.name) for s in Specialization.objects.all()]
        if 'initial' in kwargs:
            specs = list(Specialization.objects.filter(doctors=u.doctor).values_list('id', flat=True))
            self.fields['factory_specializations'].initial = specs
        self.helper = FormHelper()
        self.helper.wrapper_class = 'row'
        self.helper.label_class = 'col-md-3'
        self.helper.field_class = 'col-md-9'
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
        user.doctor.visit_duration = self.cleaned_data['visit_duration']
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
    mobile = forms.CharField(max_length=15, label=u'Numer telefonu', required=False)

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
    horizontal = True
    return_result = True
    first_name = forms.CharField(max_length=100, label=u'Imię')
    last_name = forms.CharField(max_length=100, label=u'Nazwisko')
    email = forms.EmailField(label=u'Adres email', required=False)
    pesel = PLPESELField(label=u'Pesel', required=False)
    address = forms.CharField(max_length=200, required=False, label=u'Adres')
    mobile = forms.CharField(max_length=20, label=u'Numer telefonu', required=False)

    def clean_pesel(self):
        pesel = self.cleaned_data['pesel']
        pesel = None if len(pesel) == 0 else pesel
        if pesel and Patient.objects.filter(pesel=pesel).exists():
            raise ValidationError('Istnieje już pacjent o tym numerze pesel')
        return pesel

    def save(self):
        patient = Patient.objects.create(pesel=self.cleaned_data['pesel'], email=self.cleaned_data.get('email', ''),
                                         mobile=self.cleaned_data.get('mobile', ''),
                                         address=self.cleaned_data.get('address', ''),
                               first_name=self.cleaned_data['first_name'], last_name=self.cleaned_data['last_name'])
        return {'id': patient.id, 'label': patient.name_with_pesel}


class PatientModelForm(forms.ModelForm):
    horizontal = True
    pesel = PLPESELField(label=u'Pesel', required=False)
    class Meta:
        model = Patient
        fields = ['first_name', 'last_name', 'pesel', 'address', 'email', 'mobile', 'info']


class SystemForm(forms.ModelForm):
    class Meta:
        model = SystemSettings
        fields = ['logo']

    def __init__(self):
        super(SystemForm, self).__init__()
        self.helper = FormHelper()
        self.helper.wrapper_class = 'row'
        self.helper.label_class = 'col-md-3'
        self.helper.field_class = 'col-md-9'
        self.helper.add_layout(Layout(
            Field('logo', css_class='form-control', wrapper_class='row')
        ))


class UserTabForm(UserForm):
    user_type = forms.ChoiceField(choices=(('doctor', 'Lekarz'), ('worker', 'Pracownik')),
                                  label='Typ użytkownika')
    username = forms.CharField(max_length=128, label=u'Nazwa użytkownika')
    password = forms.CharField(widget=forms.PasswordInput(), label=u'Hasło')
    password2 = forms.CharField(widget=forms.PasswordInput(), label=u'Powtórz hasło')

    field_order = ['user_type', 'username', 'first_name', 'last_name', 'mobile', 'email', 'password', 'password2']


class DoctorTabForm(forms.Form):
    save_with_user = True
    horizontal = True
    mobile = forms.CharField(max_length=9, label=u'Numer telefonu', required=False)
    pwz = forms.CharField(max_length=7, label=u'Numer PWZ')
    title = forms.CharField(max_length=50, label=u'Tytuł')
    form_class = forms.CharField(max_length=50, initial='DoctorTabForm', widget=HiddenInput(), required=False)
    visit_duration = forms.IntegerField(min_value=5, required=True, label='Czas trwania wizyty',
                                        help_text='Liczba minut przypadających na jedną wizytę')
    factory_specializations = forms.MultipleChoiceField(label=u'Specjalizacje', required=False,
                                                        help_text=u'Zaznacz kilka pozycji trzymając wciśnięty klawisz CTRL')

    def __init__(self, *args, **kwargs):
        if 'user' in kwargs.get('initial', {}):
            u = kwargs['initial'].pop('user')
            kwargs['initial'] = {'first_name': u.first_name, 'last_name': u.last_name, 'email': u.email,
                                 'visit_duration': u.doctor.visit_duration,
                                 'mobile': u.profile.mobile, 'pwz': u.doctor.pwz, 'title': u.doctor.title}
        super(DoctorTabForm, self).__init__(*args, **kwargs)
        self.fields['factory_specializations'].choices = [(s.id, s.name) for s in Specialization.objects.all()]
        if 'initial' in kwargs:
            specs = list(Specialization.objects.filter(doctors=u.doctor).values_list('id', flat=True))
            self.fields['factory_specializations'].initial = specs

    def clean_factory_specializations(self):
        return self.cleaned_data['factory_specializations']

    def clean_mobile(self):
        if self.cleaned_data['mobile'] == '':
            return None
        return int(self.cleaned_data['mobile'])

    def save(self, user):
        user.doctor.title = self.data['title']
        user.doctor.pwz = self.data['pwz']
        user.doctor.visit_duration = self.cleaned_data['visit_duration']
        user.save()
        user.doctor.save()
        if 'factory_specializations' in self.cleaned_data:
            user.doctor.specializations.clear()
            for s in self.cleaned_data['factory_specializations']:
                user.doctor.specializations.add(Specialization.objects.get(id=s))


class PermissionsTabForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['groups', 'user_permissions']
