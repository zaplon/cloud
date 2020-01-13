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
from django.utils.translation import gettext as _

from g_utils.validators import REGONValidator, NIPValidator
from visit.models import TabTypes


class Profile(models.Model):
    class Meta:
        permissions = [
            ("can_view_statistics", "Can view statistics"),
        ]
    CssThemeChoices = (
        ('yeti', 'Yeti'),
        ('minty', 'Minty'),
        ('materia', 'Materia')
    )
    user = models.OneToOneField(User, related_name='profile', on_delete=models.CASCADE)
    mobile = models.IntegerField(blank=False, null=True)
    role = models.CharField(choices=(('doctor', _('Lekarz')), ('admin', _('Administrator')),
                                     ('registration', _('Rejestracja'))), max_length=20)
    css_theme = models.CharField(choices=CssThemeChoices, default='yeti', max_length=10)

    def role_display(self):
        return self.get_role_display()

    # class Meta:
    #     permissions = (
    #         ("edit_term", u"Może edytować terminy"),
    #         ("view_system_settings", u"Może edytować ustawienia systemu"),
    #         ("edit_tab", u"Może edytować zakładki"),
    #         ("edit_visit", u"Może edytować wizyty"),
    #         ("edit_template", u"Może edytować szablony"),
    #         ("View_term", u'Może wyświetlić kalendarz')
    #     )


class NFZSettings(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    typ_podmiotu = models.CharField(max_length=32, choices=(('PRAKTYKA_LEKARSKA', 'Praktyka lekarska'),
                                                            ('PODMIOT_LECZNICZY', 'Podmiot leczniczy')),
                                    default='PRAKTYKA_LEKARSKA')
    rola_biznesowa = models.CharField(max_length=32,
                                      choices=(('LEKARZ_LEK_DENTYSTA_FELCZER', 'LEKARZ_LEK_DENTYSTA_FELCZER'),
                                               ('PIELEGNIARKA_POLOZNA', 'PIELEGNIARKA_POLOZNA')),
                                      default='LEKARZ_LEK_DENTYSTA_FELCZER')
    certificate_tls = models.FileField(null=True, blank=True, upload_to='certs')
    certificate_tls_password = models.CharField(max_length=126, blank=True)
    certificate_wsse = models.FileField(null=True, blank=True, upload_to='certs')
    certificate_wsse_password = models.CharField(max_length=126, blank=True)
    certificate_user = models.FileField(null=True, blank=True, upload_to='certs')
    certificate_user_password = models.CharField(max_length=126, blank=True)
    id_podmiotu_oid_ext = models.CharField(max_length=126, blank=True)
    id_podmiotu_oid_root = models.CharField(max_length=126, blank=True)
    id_podmiotu_lokalne = models.CharField(max_length=126, blank=True)
    id_miejsca_pracy_oid_ext = models.CharField(max_length=8, blank=True)

    @property
    def is_filled_in(self):
        """ Checks if all the fields have been filled """
        fields_names = [f.name for f in self._meta.get_fields()]
        for field_name in fields_names:
            value = getattr(self, field_name)
            if value is None or value == '':
                return False
        return True

    @property
    def id_pracownika_oid_ext(self):
        return self.user.doctor.pwz

    @property
    def id_pracownika_root(self):
        if self.rola_biznesowa == 'LEKARZ_LEK_DENTYSTA_FELCZER':
            return '2.16.840.1.113883.3.4424.1.6.2'
        elif self.rola_biznesowa == 'PIELEGNIARKA_POLOZNA':
            return '2.16.840.1.113883.3.4424.1.6.3'


# @receiver(post_save, sender=User)
# def save_user_profile(sender, instance, **kwargs):
#     if instance.groups.filter(name='Lekarze').exists():
#         if not hasattr(instance, 'doctor'):
#             Doctor.objects.create(user=instance)
#     if not hasattr(instance, 'profile'):
#         Profile.objects.create(user=instance)
#     else:
#         instance.profile.save()


@receiver(post_save, sender=User)
def create_nfz_settings(sender, instance, **kwargs):
    if kwargs.get('created'):
        NFZSettings.objects.get_or_create(id=instance.id, user=instance)


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
    user = models.OneToOneField(settings.AUTH_USER_MODEL, related_name='doctor', verbose_name=u'Lekarz',
                                on_delete=models.CASCADE)
    working_hours = models.CharField(max_length=1000, blank=True, null=True, verbose_name=u'Godziny pracy')
    visit_duration = models.IntegerField(default=15, verbose_name=u'Czas trwania wizyty')
    show_weekends = models.BooleanField(default=False, verbose_name=u'Pokaż weekendy na kalendarzu')
    terms_generated_till = models.DateField(null=True, blank=True)
    terms_start = models.TimeField(default='09:00')
    terms_end = models.TimeField(default='17:00')
    misal_id = models.CharField(blank=True, null=True, max_length=10)
    title = models.CharField(default='', verbose_name=u'Tytuł', max_length=50)
    specializations = models.ManyToManyField(Specialization, related_name='doctors', verbose_name=u'Specializacje')
    # documents_header_left = models.TextField(verbose_name=u'Nagłówek dokumentów (lewa strona)', blank=True)
    # documents_header_right = models.TextField(verbose_name=u'Nagłówek dokumentów (prawa strona)', blank=True)

    class Meta:
        verbose_name = 'Lekarz'
        verbose_name_plural = 'Lekarze'

    @property
    def available_prescriptions(self):
        return self.recipes.filter(date_used__isnull=True).count()

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
        Tab.objects.get_or_create(title='Wywiad', order=1, type=TabTypes.DEFAULT.name, doctor=instance)
        Tab.objects.get_or_create(title='Rozpoznanie', order=2, type=TabTypes.ICD10.name, doctor=instance)
        Tab.objects.get_or_create(title='Badania', order=3, type=TabTypes.DEFAULT.name, doctor=instance)
        Tab.objects.get_or_create(title='Zalecenia', order=4, type=TabTypes.DEFAULT.name, doctor=instance)
        Tab.objects.get_or_create(title='Recepty', order=5, type=TabTypes.MEDICINES.name, doctor=instance)
        Tab.objects.get_or_create(title='Skierowania', order=6, type=TabTypes.EXAMINATIONS.name, doctor=instance)
        Tab.objects.get_or_create(title='Notatki', order=7, type=TabTypes.NOTES.name, doctor=instance)


class Patient(models.Model):
    mobile = models.CharField(blank=True, null=True, verbose_name=u'Telefon', max_length=20)
    user = models.OneToOneField(settings.AUTH_USER_MODEL, blank=True, null=True, on_delete=models.CASCADE)
    first_name = models.CharField(max_length=100, default='', verbose_name=u'Imię')
    second_name = models.CharField(max_length=100, default='', verbose_name=u'Drugie imię')
    last_name = models.CharField(max_length=100, default='', verbose_name=u'Nazwisko')
    gender = models.CharField(max_length=1, verbose_name=u'Płeć', choices=(('M', u'Mężczyzna'), ('F', u'Kobieta')))
    pesel = models.CharField(max_length=11, blank=True, null=True, verbose_name=u'Pesel', unique=True)
    birth_date = models.DateField(blank=True, null=True,  verbose_name='Data urodzenia',
                                  help_text=u'Zostanie odczytana z numeru pesel, jeżeli pozostawiona pusta')
    email = models.EmailField(blank=True, null=True, verbose_name=u'Email')
    postal_code = models.CharField(blank=True, max_length=6, verbose_name='Kod pocztowy')
    street = models.CharField(blank=True, max_length=200, verbose_name='Ulica')
    street_number = models.CharField(blank=True, max_length=10, verbose_name='Numer domu')
    apartment_number = models.CharField(blank=True, max_length=10, verbose_name='Numer lokalu')
    city = models.CharField(blank=True, max_length=100,  verbose_name=u'Miejscowość')
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

    def save(self, *args, **kwargs):
        if self.pesel == '':
            self.pesel = None
        if self.pesel and len(self.pesel) == 11 and not self.birth_date:
            self.birth_date = datetime.datetime.strptime(self.pesel[0:6], '%y%m%d')
        return super().save(*args, **kwargs)


class Note(models.Model):
    text = models.CharField(max_length=1024)
    patient = models.ForeignKey(Patient, related_name='notes', on_delete=models.CASCADE)
    doctor = models.ForeignKey(Doctor, related_name='notes', on_delete=models.CASCADE)
    private = models.BooleanField(default=False)

    def get_author(self):
        return self.doctor.__str__()


class PrescriptionNumber(models.Model):
    doctor = models.ForeignKey(Doctor, related_name='recipes', on_delete=models.CASCADE)
    nr = models.CharField(max_length=30)
    date_used = models.DateTimeField(null=True)

    @staticmethod
    def available(doctor):
        return PrescriptionNumber.objects.filter(doctor=doctor, date_used__isnull=True).count()

    @staticmethod
    def total(doctor):
        return PrescriptionNumber.objects.filter(doctor=doctor).count()


class Code(models.Model):
    code = models.IntegerField()
    created = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, blank=True, null=True, related_name='codes',
                             on_delete=models.CASCADE)


class SystemSettings(models.Model):
    logo = models.ImageField(verbose_name='Logo')
    documents_header_left = models.TextField(verbose_name=u'Nagłówek dokumentów (lewa strona)', blank=True)
    documents_header_right = models.TextField(verbose_name=u'Nagłówek dokumentów (prawa strona)', blank=True)
    regon = models.CharField(max_length=14, blank=True, verbose_name=u'Numer REGON', validators=[REGONValidator()])
    nip = models.CharField(max_length=13, blank=True, verbose_name=u'Numer NIP', validators=[NIPValidator()])
    nfz_department = models.CharField(max_length=2, default='07', verbose_name=u"Oddział NFZ")
    city = models.CharField(max_length=100, blank=True, verbose_name=u'Miejscowość')
    street = models.CharField(max_length=200, blank=True, verbose_name=u'Ulica')
    street_number = models.CharField(max_length=10, blank=True, verbose_name=u'Numer domu')
    postal_code = models.CharField(blank=True, max_length=6, verbose_name='Kod pocztowy')

    class Meta:
        verbose_name = 'Ustawienia systemowe'
        verbose_name_plural = 'Ustawienia systemowe'

    def __str__(self):
        return 'Ustawienia systemowe'


class MobileCode(models.Model):
    code = models.IntegerField()
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    creation_date = models.DateTimeField(auto_now_add=True)
