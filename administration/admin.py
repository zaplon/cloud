# -*- coding: utf-8 -*-
import json

from django.contrib import admin
from django.contrib.auth.forms import UserCreationForm, UsernameField
from django.contrib.auth.models import User, Group
from django.contrib.auth.admin import UserAdmin, UserChangeForm, GroupAdmin, csrf_protect_m
from django.contrib.sites.models import Site
from django.forms import ModelForm, Widget, ChoiceField, HiddenInput
from django.template import loader
from django.forms.fields import CharField
from rest_framework.authtoken.models import Token

from administration.settings import *
from django.utils.translation import ugettext_lazy as _

from timetable.models import Service, Localization
from user_profile.models import SystemSettings, Doctor, Specialization

admin.site.site_title = 'Administracja'
admin.site.site_header = 'Administracja'


def translate_permissions(perms):
    trans_dict = {'Can': u'Może', 'delete': u'usunąć', 'create': u'utworzyć', 'add': u'dodać', 'change': u'zmienić',
                  'user': u'użytkownika', 'term': 'termin', 'visit': u'wizytę'}
    new_perms = []
    for p in perms:
        name = p[1].split('|')[-1]
        for t in trans_dict:
            name = name.replace(t, trans_dict[t])
        new_perms.append([p[0], name])
    return new_perms


class UserChangeForm(UserChangeForm):

    def __init__(self, *args, **kwargs):
        super(UserChangeForm, self).__init__(*args, **kwargs)


class UserCreationForm(UserCreationForm):
    role = ChoiceField(label=_('Rola'), choices=(('DOCTOR', 'Lekarz'), ('REGISTRATION', 'Rejestracja'),
                                                 ('ADMINISTRATION', 'Administracja')))

    class Meta:
        model = User
        fields = ("username", "role")
        field_classes = {'username': UsernameField}


class HoursWidget(Widget):

    def __init__(self, working_hours='', attrs=None):
        if attrs is not None:
            self.attrs = attrs.copy()
        else:
            self.attrs = {}
        self.working_hours = working_hours


    def render(self, name, value, attrs=None):
        if not self.working_hours:
            days = [{'name': 'Poniedziałek', 'value': ['09:00', '17:00'], 'on': True},
                    {'name': 'Wtorek', 'value': ['09:00', '17:00'], 'on': True},
                    {'name': 'Środa', 'value': ['09:00', '17:00'], 'on': True},
                    {'name': 'Czwartek', 'value': ['09:00', '17:00'], 'on': True},
                    {'name': 'Piątek', 'value': ['09:00', '17:00'], 'on': True},
                    {'name': 'Sobota', 'value': ['09:00', '17:00'], 'on': False},
                    {'name': 'Niedziela', 'value': ['09:00', '17:00'], 'on': False}]
        else:
            days = json.loads(self.working_hours)
        return loader.render_to_string('user_profile/admin/fields/working_hours.html', {'days': days})


class DoctorForm(ModelForm):

    class Meta:
        fields = ['pwz', 'mobile', 'title', 'working_hours', 'working_hours_editor', 'specializations']

    def __init__(self, *args, **kwargs):
        super(DoctorForm, self).__init__(*args, **kwargs)


class DoctorInline(admin.StackedInline):
    model = Doctor
    can_delete = False
    verbose_name_plural = 'Profil'
    fk_name = 'user'
    extra = 0
    form = DoctorForm


class UserAdmin(UserAdmin):
    inlines = []
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        (_('Personal info'), {'fields': ('first_name', 'last_name', 'email')}),
        (_('Permissions'), {'fields': ('is_active', 'is_staff',
                                       'groups', 'user_permissions')}),
        (_('Important dates'), {'fields': ('last_login', 'date_joined')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'role', 'password1', 'password2'),
        }),
    )
    form = UserChangeForm
    add_form = UserCreationForm

    def render_change_form(self, request, context, add=False, change=False, form_url='', obj=None):
        if not request.user.is_superuser:
            form = context['adminform'].form
            perms = [p[0] for p in PERMISSIONS]
            if 'user_permissions' in form.fields:
                form.fields['user_permissions'].queryset = form.fields['user_permissions'].queryset.filter(codename__in=perms)
                choices = translate_permissions(list(form.fields['user_permissions'].choices))
                form.fields['user_permissions'].choices = choices
        return super(UserAdmin, self).render_change_form(request, context, add, change, form_url, obj)

    def get_form(self, request, obj=None, **kwargs):
        """
        Use special form during user creation
        """
        defaults = {}
        if obj is None:
            defaults['form'] = self.add_form
        else:
            if obj.groups.filter(name='Lekarze').exists():
                self.inlines = (DoctorInline,)
        defaults.update(kwargs)
        return super(UserAdmin, self).get_form(request, obj, **defaults)

    def save_model(self, request, obj, form, change):
        obj.save()
        if 'role' in form.cleaned_data:
            role = form.cleaned_data['role']
            if role == 'DOCTOR':
                obj.groups.add(Group.objects.get(name='Lekarze'))
            if role == 'REGISTRATION':
                obj.groups.add(Group.objects.get(name='Rejestracja'))
            if role == 'ADMINISTRATION':
                obj.groups.add(Group.objects.get(name='administracja'))


class GroupForm(ModelForm):
    class Meta:
        model = Group
        fields = '__all__'


class GroupAdmin(GroupAdmin):
    form = GroupForm

    def render_change_form(self, request, context, add=False, change=False, form_url='', obj=None):
        if not request.user.is_superuser:
            form = context['adminform'].form
            perms = [p[0] for p in PERMISSIONS]
            form.fields['permissions'].queryset = form.fields['permissions'].queryset.filter(codename__in=perms)
            choices = translate_permissions(list(form.fields['permissions'].choices))
            form.fields['permissions'].choices = choices
        return super(GroupAdmin, self).render_change_form(request, context, add, change, form_url, obj)


class ServiceAdmin(admin.ModelAdmin):
    fields = ['name', 'code', 'doctors']


class SystemSettingsAdmin(admin.ModelAdmin):

    @csrf_protect_m
    def changelist_view(self, request, extra_context=None):
        SystemSettings.objects.get_or_create(pk=1)
        return self.changeform_view(request, '1', '', extra_context)


admin.site.unregister(User)
admin.site.unregister(Group)
admin.site.unregister(Site)
admin.site.unregister(Token)
admin.site.register(Service, ServiceAdmin)
admin.site.register(Localization)
admin.site.register(Specialization)
admin.site.register(User, UserAdmin)
admin.site.register(Group, GroupAdmin)
admin.site.register(SystemSettings, SystemSettingsAdmin)
