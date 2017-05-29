# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.conf import settings
from django.db import models
import json
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.urls import reverse


class Profile(models.Model):
    user = models.OneToOneField(User, related_name='profile')
    mobile = models.IntegerField(blank=True, null=True)
    css = models.CharField(default='classic', choices=(('classic', 'Klasyczny'),), max_length=20, verbose_name='Interfejs')

    # class Meta:
    #     permissions = (
    #         ("edit_term", u"Może edytować terminy"),
    #         ("view_system_settings", u"Może edytować ustawienia systemu"),
    #         ("edit_tab", u"Może edytować zakładki"),
    #         ("edit_visit", u"Może edytować wizyty"),
    #         ("edit_template", u"Może edytować szablony"),
    #         ("View_term", u'Może wyświetlić kalendarz')
    #     )


@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    if not hasattr(instance, 'profile'):
        Profile.objects.create(user=instance)
    else:
        instance.profile.save()


class Specialization(models.Model):
    name = models.CharField(max_length=50)
    code = models.CharField(max_length=10)
    code_misal = models.CharField(max_length=100)

    def __unicode__(self):
        return self.name


class Doctor(models.Model):
    pwz = models.CharField(max_length=7, verbose_name=u'Numer PWZ')
    mobile = models.IntegerField(blank=True, null=True, verbose_name=u'Numer komórki')
    user = models.OneToOneField(settings.AUTH_USER_MODEL, related_name='doctor', verbose_name=u'Lekarz')
    working_hours = models.CharField(max_length=800, blank=True, null=True, verbose_name=u'Godziny pracy')
    visit_duration = models.IntegerField(default=15, verbose_name=u'Czas trwania wizyty')
    terms_generated_till = models.DateField(null=True, blank=True)
    terms_start = models.TimeField(default='09:00')
    terms_end = models.TimeField(default='17:00')
    misal_id = models.CharField(blank=True, null=True, max_length=10)
    title = models.CharField(default='', verbose_name=u'Tytuł', max_length=50)
    specializations = models.ManyToManyField(Specialization, related_name='doctors', verbose_name=u'Specializacje')

    @property
    def name(self):
        return '%s %s %s' % (self.title, self.user.first_name, self.user.last_name)

    def get_working_hours(self):
        if not self.working_hours:
            return []
        return json.loads(self.working_hours)

    def get_name(self):
        return self.__unicode__()

    def __unicode__(self):
        return self.name


@receiver(post_save, sender=Doctor)
def create_doctor_tabs(sender, instance, created, **kwargs):
    from visit.models import Tab, TabParent
    if created:
        # zestaw zakładek
        default = TabParent.objects.get(name='default')
        icd10 = TabParent.objects.get(name='icd10')
        medicines = TabParent.objects.get(name='medicines')
        notes = TabParent.objects.get(name='notes')
        services = TabParent.objects.get(name='services')
        Tab.objects.create(doctor=instance, title='Wywiad', parent=default, order=0)
        Tab.objects.create(doctor=instance, title='Rozpoznanie', parent=icd10, order=1)
        Tab.objects.create(doctor=instance, title='Zalecenia', parent=default, order=2)
        Tab.objects.create(doctor=instance, title='Leki', parent=medicines, order=3)
        Tab.objects.create(doctor=instance, title='Badania dodatkowe', parent=services, order=4)
        Tab.objects.create(doctor=instance, title='Notatki', parent=notes, order=5)


class Patient(models.Model):
    mobile = models.IntegerField(blank=True, null=True, verbose_name=u'Telefon')
    user = models.OneToOneField(settings.AUTH_USER_MODEL, blank=True, null=True)
    first_name = models.CharField(max_length=100, default='', verbose_name=u'Imię')
    last_name = models.CharField(max_length=100, default='', verbose_name=u'Nazwisko')
    pesel = models.CharField(max_length=11, blank=True, null=True, verbose_name=u'Pesel')
    email = models.EmailField(blank=True, null=True, verbose_name=u'Email')
    address = models.CharField(blank=True, null=True, verbose_name=u'Adres', max_length=200)
    info = models.TextField(blank=True, null=True, verbose_name=u'Ważne informacje',
                            help_text=u'Informacje pomocnicze o alergiach, przebytych zabiegach, etc...')

    def __unicode__(self):
        return '%s %s' % (self.first_name, self.last_name)

    def get_absolute_url(self):
        return reverse('patients')


class Note(models.Model):
    text = models.CharField(max_length=1024)
    patient = models.ForeignKey(Patient, related_name='notes')
    doctor = models.ForeignKey(Doctor, related_name='notes')

    def get_author(self):
        return self.doctor.__unicode__()


class Recipe(models.Model):
    doctor = models.ForeignKey(Doctor, related_name='recipes')
    nr = models.CharField(max_length=30)
    was_used = models.BooleanField(blank=False, default=False)


class Code(models.Model):
    code = models.IntegerField()
    created = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, blank=True, null=True, related_name='codes')


class SystemSettings(models.Model):
    logo = models.ImageField(verbose_name='Logo')

    class Meta:
        verbose_name = 'Ustawienia systemowe'
        verbose_name_plural = 'Ustawienia systemowe'

    def __unicode__(self):
        return 'Ustawienia systemowe'
