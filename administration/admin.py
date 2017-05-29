# -*- coding: utf-8 -*-
from django.contrib import admin
from django.contrib.auth.models import User, Group
from django.contrib.auth.admin import UserAdmin, UserChangeForm, GroupAdmin
from django.forms import ModelForm
from django.urls import reverse
from django.utils.safestring import mark_safe

from administration.settings import *
from django.utils.translation import ugettext_lazy as _

from timetable.models import Service, Localization
from user_profile.models import SystemSettings, Doctor

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
    pass


class DoctorInline(admin.StackedInline):
    model = Doctor
    can_delete = False
    verbose_name_plural = 'Profil'
    fk_name = 'user'


class UserAdmin(UserAdmin):
    inlines = (DoctorInline, )
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        (_('Personal info'), {'fields': ('first_name', 'last_name', 'email')}),
        (_('Permissions'), {'fields': ('is_active', 'is_staff',
                                       'groups', 'user_permissions')}),
        (_('Important dates'), {'fields': ('last_login', 'date_joined')}),
    )
    form = UserChangeForm

    def render_change_form(self, request, context, add=False, change=False, form_url='', obj=None):
        if not request.user.is_superuser:
            form = context['adminform'].form
            perms = [p[0] for p in PERMISSIONS]
            form.fields['user_permissions'].queryset = form.fields['user_permissions'].queryset.filter(codename__in=perms)
            choices = translate_permissions(list(form.fields['user_permissions'].choices))
            form.fields['user_permissions'].choices = choices
        return super(UserAdmin, self).render_change_form(request, context, add, change, form_url, obj)


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


admin.site.unregister(User)
admin.site.unregister(Group)
admin.site.register(Doctor)
admin.site.register(Service)
admin.site.register(Localization)
admin.site.register(User, UserAdmin)
admin.site.register(Group, GroupAdmin)
admin.site.register(SystemSettings)
