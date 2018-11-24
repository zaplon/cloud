# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.conf import settings
from django.db import models
import json
import datetime
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.urls import reverse

from visit.models import TabTypes


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
    if instance.groups.filter(name='Lekarze').exists():
        if not hasattr(instance, 'doctor'):
            Doctor.objects.create(user=instance)
    if not hasattr(instance, 'profile'):
        Profile.objects.create(user=instance)
    else:
        instance.profile.save()


class Specialization(models.Model):
    name = models.CharField(max_length=50, verbose_name='Nazwa')
    code = models.CharField(max_length=10, verbose_name='Kod')
    code_misal = models.CharField(max_length=100, verbose_name='Kod MISAL')

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Specjalizacja'
        verbose_name_plural = 'Specjalizacje'


class Doctor(models.Model):
    pwz = models.CharField(max_length=7, verbose_name=u'Numer PWZ')
    mobile = models.IntegerField(blank=True, null=True, verbose_name=u'Numer komórki')
    user = models.OneToOneField(settings.AUTH_USER_MODEL, related_name='doctor', verbose_name=u'Lekarz')
    working_hours = models.CharField(max_length=1000, blank=True, null=True, verbose_name=u'Godziny pracy')
    visit_duration = models.IntegerField(default=15, verbose_name=u'Czas trwania wizyty')
    terms_generated_till = models.DateField(null=True, blank=True)
    terms_start = models.TimeField(default='09:00')
    terms_end = models.TimeField(default='17:00')
    misal_id = models.CharField(blank=True, null=True, max_length=10)
    title = models.CharField(default='', verbose_name=u'Tytuł', max_length=50)
    specializations = models.ManyToManyField(Specialization, related_name='doctors', verbose_name=u'Specializacje')

    class Meta:
        verbose_name = 'Lekarz'
        verbose_name_plural = 'Lekarze'

    @property
    def available_prescriptions(self):
        return self.recipes.filter(was_used=False).count()

    @property
    def total_prescriptions(self):
        return self.recipes.count()

    @property
    def name(self):
        return '%s %s %s' % (self.title, self.user.first_name, self.user.last_name)

    @property    
    def next_term(self):
        now = datetime.datetime.now()
        terms = self.terms.filter(datetime__gt=now, status='FREE').order_by('datetime')
        if len(terms) > 0:
            return terms[0].datetime.strftime('%d-%m-%Y')
        else:
            return '-'
    
    def get_working_hours(self):
        if not self.working_hours:
            return []
        return json.loads(self.working_hours)

    def get_name(self):
        return self.__str__()

    def __str__(self):
        return self.name


@receiver(post_save, sender=Doctor)
def create_doctor_tabs(sender, instance, created, **kwargs):
    from visit.models import Tab
    if created:
        for i, type in enumerate(TabTypes):
            Tab.objects.create(doctor=instance, title=type.value, type=type.name, order=i)


class Patient(models.Model):
    mobile = models.CharField(blank=True, null=True, verbose_name=u'Telefon', max_length=20)
    user = models.OneToOneField(settings.AUTH_USER_MODEL, blank=True, null=True)
    first_name = models.CharField(max_length=100, default='', verbose_name=u'Imię')
    last_name = models.CharField(max_length=100, default='', verbose_name=u'Nazwisko')
    pesel = models.CharField(max_length=11, blank=True, null=True, verbose_name=u'Pesel', unique=True)
    email = models.EmailField(blank=True, null=True, verbose_name=u'Email')
    address = models.CharField(blank=True, null=True, verbose_name=u'Adres', max_length=200)
    info = models.TextField(blank=True, null=True, verbose_name=u'Ważne informacje',
                            help_text=u'Informacje pomocnicze o alergiach, przebytych zabiegach, etc...')

    @property
    def name(self):
        return self.__str__()

    @property
    def name_with_pesel(self):
        if self.pesel:
            return '%s (%s)' % (self.name, self.pesel)
        else:
            return self.name

    def __str__(self):
        return '%s %s' % (self.first_name, self.last_name)

    def get_absolute_url(self):
        return reverse('patients')


class Note(models.Model):
    text = models.CharField(max_length=1024)
    patient = models.ForeignKey(Patient, related_name='notes')
    doctor = models.ForeignKey(Doctor, related_name='notes')
    private = models.BooleanField(default=False)

    def get_author(self):
        return self.doctor.__str__()


class Recipe(models.Model):
    doctor = models.ForeignKey(Doctor, related_name='recipes')
    nr = models.CharField(max_length=30)
    was_used = models.BooleanField(blank=False, default=False)

    def available(self, doctor):
        return Recipe.objects.filter(doctor=doctor, was_used=False).count()

    def total(self, doctor):
        return Recipe.objects.filter(doctor=doctor).count()


class Code(models.Model):
    code = models.IntegerField()
    created = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, blank=True, null=True, related_name='codes')


class SystemSettings(models.Model):
    logo = models.ImageField(verbose_name='Logo')
    documents_header = models.TextField(verbose_name=u'Nagłówek dokumentów', blank=True)

    class Meta:
        verbose_name = 'Ustawienia systemowe'
        verbose_name_plural = 'Ustawienia systemowe'

    def __str__(self):
        return 'Ustawienia systemowe'
