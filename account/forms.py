# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import random
import re

from g_utils.views import send_sms_code

try:
    from collections import OrderedDict
except ImportError:
    OrderedDict = None

from django import forms
from django.utils.encoding import force_text
from django.utils.translation import ugettext_lazy as _

from django.contrib import auth
from django.contrib.auth import get_user_model

from account.hooks import hookset
from account.models import EmailAddress
from account.utils import get_user_lookup_kwargs
from django.conf import settings
from django.forms.fields import CharField
from django.core.exceptions import ObjectDoesNotExist
from django.forms.fields import HiddenInput
import datetime
from user_profile.models import Code
from django.contrib.auth.models import User
alnum_re = re.compile(r"^\w+$")


class PasswordField(forms.CharField):

    def __init__(self, *args, **kwargs):
        kwargs.setdefault("widget", forms.PasswordInput(render_value=False))
        self.strip = kwargs.pop("strip", True)
        super(PasswordField, self).__init__(*args, **kwargs)

    def to_python(self, value):
        if value in self.empty_values:
            return ""
        value = force_text(value)
        if self.strip:
            value = value.strip()
        return value


class SignupForm(forms.Form):

    username = forms.CharField(
        label=_("Username"),
        max_length=30,
        widget=forms.TextInput(),
        required=True
    )
    password = PasswordField(
        label=_("Password"),
        strip=settings.ACCOUNT_PASSWORD_STRIP,
    )
    password_confirm = PasswordField(
        label=_("Password (again)"),
        strip=settings.ACCOUNT_PASSWORD_STRIP,
    )
    email = forms.EmailField(
        label=_("Email"),
        widget=forms.TextInput(), required=True)

    def clean_username(self):
        if not alnum_re.search(self.cleaned_data["username"]):
            raise forms.ValidationError(_("Usernames can only contain letters, numbers and underscores."))
        User = get_user_model()
        lookup_kwargs = get_user_lookup_kwargs({
            "{username}__iexact": self.cleaned_data["username"]
        })
        qs = User.objects.filter(**lookup_kwargs)
        if not qs.exists():
            return self.cleaned_data["username"]
        raise forms.ValidationError(_("This username is already taken. Please choose another."))

    def clean_email(self):
        value = self.cleaned_data["email"]
        qs = EmailAddress.objects.filter(email__iexact=value)
        if not qs.exists() or not settings.ACCOUNT_EMAIL_UNIQUE:
            return value
        raise forms.ValidationError(_("A user is registered with this email address."))

    def clean(self):
        if "password" in self.cleaned_data and "password_confirm" in self.cleaned_data:
            if self.cleaned_data["password"] != self.cleaned_data["password_confirm"]:
                raise forms.ValidationError(_("You must type the same password each time."))
        return self.cleaned_data


class LoginForm(forms.Form):

    password = PasswordField(
        label=_("Password"),
        strip=settings.ACCOUNT_PASSWORD_STRIP,
        required=True if settings.USE_SMS_LOGIN else False
    )
    remember = forms.BooleanField(
        label=_("Remember Me"),
        required=False
    )
    user = None

    def clean(self):
        if self._errors:
            return
        user = auth.authenticate(**self.user_credentials())
        if user:
            if user.is_active:
                self.user = user
            else:
                raise forms.ValidationError(_("This account is inactive."))
        else:
            raise forms.ValidationError(self.authentication_fail_message)
        return self.cleaned_data

    def user_credentials(self):
        return hookset.get_user_credentials(self, self.identifier_field)


class MobileForm(forms.Form):
    set_mobile = forms.IntegerField(label='Telefon',
                             help_text=u'Numer wykorzysytwany jest jedynie do przesyłania kodów do logowania')
    username = forms.CharField(widget=HiddenInput())

    def clean_set_mobile(self):
        mobile = self.cleaned_data['set_mobile']
        return mobile

    def save(self):
        u = User.objects.get(username=self.cleaned_data['username'])
        if hasattr(u, 'doctor'):
            u.doctor.mobile = self.cleaned_data['set_mobile']
            u.doctor.save()
        if hasattr(u, 'profile'):
            u.profile.mobile = self.cleaned_data['set_mobile']
            u.save()


class LoginUsernameForm(LoginForm):

    username = forms.CharField(label=_("Username"), max_length=30)
    authentication_fail_message = _("The username and/or password you specified are not correct.")
    identifier_field = "username"
    code = CharField(max_length=6, required=False, label=u'Kod', help_text=u'Wpisz kod, który przyszedł na telefon komórkowy')

    def generate_code(self, user):
        code = Code.objects.create(code=random.randint(100000, 999999), user=user)
        return code

    def clean(self):
        if settings.USE_SMS_LOGIN:
            try:
                self.user = User.objects.get(username=self.data['username'])
            except ObjectDoesNotExist:
                try:
                    self.user = User.objects.get(username=self.data['username'].upper())
                except ObjectDoesNotExist:
                    raise forms.ValidationError(_("Użytkownik o podanym loginie nie istnieje"))
            if 'code' in self.data:
                deadline = datetime.datetime.now() - datetime.timedelta(minutes=15)
                try:
                    if not settings.SIMULATE_SMS_LOGIN:
                        code = Code.objects.get(code=self.data['code'], user=self.user,
                                                created__gte=deadline)
                        send_sms_code(code, self.user.doctor.phone, self.user.username)
                except ObjectDoesNotExist:
                    raise forms.ValidationError(_("Kod sms się nie zgadza"))
            else:
                code = self.generate_code(self.user)
            return True
        super(LoginUsernameForm, self).clean()

    def __init__(self, *args, **kwargs):
        super(LoginUsernameForm, self).__init__(*args, **kwargs)
        if settings.USE_SMS_LOGIN:
            if 'initial' in kwargs and 'code' in kwargs['initial']:
                field_order = ["username", "code"]
                self.fields['username'].widget = HiddenInput()
                self.fields['code'].required = True
            else:
                field_order = ["username"]
        else:
            field_order = ["username", "password", "remember"]
        if not OrderedDict or hasattr(self.fields, "keyOrder"):
            self.fields.keyOrder = field_order
        else:
            self.fields = OrderedDict((k, self.fields[k]) for k in field_order)


class LoginEmailForm(LoginForm):

    email = forms.EmailField(label=_("Email"))
    authentication_fail_message = _("The email address and/or password you specified are not correct.")
    identifier_field = "email"

    def __init__(self, *args, **kwargs):
        super(LoginEmailForm, self).__init__(*args, **kwargs)
        field_order = ["email", "password", "remember"]
        if not OrderedDict or hasattr(self.fields, "keyOrder"):
            self.fields.keyOrder = field_order
        else:
            self.fields = OrderedDict((k, self.fields[k]) for k in field_order)


class ChangePasswordForm(forms.Form):

    password_current = forms.CharField(
        label=_("Current Password"),
        widget=forms.PasswordInput(render_value=False)
    )
    password_new = forms.CharField(
        label=_("New Password"),
        widget=forms.PasswordInput(render_value=False)
    )
    password_new_confirm = forms.CharField(
        label=_("New Password (again)"),
        widget=forms.PasswordInput(render_value=False)
    )

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop("user")
        super(ChangePasswordForm, self).__init__(*args, **kwargs)

    def clean_password_current(self):
        if not self.user.check_password(self.cleaned_data.get("password_current")):
            raise forms.ValidationError(_("Please type your current password."))
        return self.cleaned_data["password_current"]

    def clean_password_new_confirm(self):
        if "password_new" in self.cleaned_data and "password_new_confirm" in self.cleaned_data:
            if self.cleaned_data["password_new"] != self.cleaned_data["password_new_confirm"]:
                raise forms.ValidationError(_("You must type the same password each time."))
        return self.cleaned_data["password_new_confirm"]


class PasswordResetForm(forms.Form):

    email = forms.EmailField(label=_("Email"), required=True)

    def clean_email(self):
        value = self.cleaned_data["email"]
        if not EmailAddress.objects.filter(email__iexact=value).exists():
            raise forms.ValidationError(_("Email address can not be found."))
        return value


class PasswordResetTokenForm(forms.Form):

    password = forms.CharField(
        label=_("New Password"),
        widget=forms.PasswordInput(render_value=False)
    )
    password_confirm = forms.CharField(
        label=_("New Password (again)"),
        widget=forms.PasswordInput(render_value=False)
    )

    def clean_password_confirm(self):
        if "password" in self.cleaned_data and "password_confirm" in self.cleaned_data:
            if self.cleaned_data["password"] != self.cleaned_data["password_confirm"]:
                raise forms.ValidationError(_("You must type the same password each time."))
        return self.cleaned_data["password_confirm"]


class SettingsForm(forms.Form):

    email = forms.EmailField(label=_("Email"), required=True)
    timezone = forms.ChoiceField(
        label=_("Timezone"),
        choices=[("", "---------")] + settings.ACCOUNT_TIMEZONES,
        required=False
    )
    if settings.USE_I18N:
        language = forms.ChoiceField(
            label=_("Language"),
            choices=settings.ACCOUNT_LANGUAGES,
            required=False
        )

    def clean_email(self):
        value = self.cleaned_data["email"]
        if self.initial.get("email") == value:
            return value
        qs = EmailAddress.objects.filter(email__iexact=value)
        if not qs.exists() or not settings.ACCOUNT_EMAIL_UNIQUE:
            return value
        raise forms.ValidationError(_("A user is registered with this email address."))
