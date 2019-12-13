# -*- coding: utf-8 -*-
import csv

from django.core.management.base import BaseCommand, CommandError

from django.contrib.auth.models import Permission, Group, User
from django.core.management import call_command
from visit.models import Icd10
from user_profile.models import Specialization, Doctor, SystemSettings
from django.core.files import File


class Command(BaseCommand):
    help = 'Prepares environment'

    def load_icd10(self):
        with open('g_utils/initial_data/icd10.csv', 'r', encoding='utf8') as csv_file:
            data = csv.reader(csv_file, delimiter=',', quotechar='"')
            for row in data:
                icd, _ = Icd10.objects.get_or_create(desc=row[2], code=row[1])
                print(icd.desc)
            print('***** Icd 10 imported *****')

    def load_specializations(self):
        with open('g_utils/initial_data/specializations.csv', 'r', encoding='utf8') as csv_file:
            data = csv.reader(csv_file, delimiter=',', quotechar='"')
            for row in data:
                specialization, _ = Specialization.objects.get_or_create(name=row[1], code=row[2], code_misal=row[2])
                print(specialization.name)
            print('***** Specializations imported *****')

    def create_groups(self):
        groups = {'Lekarze': ['_visit', '_result', '_term', '_medicine', '_template', '_tab',
                              'can_add_prescription', '_prescriptionnumber', '_refundation',
                              '_nfzsettings', '_patient'],
                  'Administratorzy': ['_term',  '_result', '_user', '_service', '_localization', '_patient',
                                      '_systemsettings']}
        for group_name, permissions_patterns in groups.items():
            permissions = Permission.objects.none()
            for p in permissions_patterns:
                permissions |= Permission.objects.filter(codename__icontains=p)
            group, _ = Group.objects.get_or_create(name=group_name)
            group.permissions.add(*permissions)

    def create_system_settings(self):
        system_settings = SystemSettings.objects.create(id=1)
        with open('g_utils/initial_data/logo.png', 'rb') as f:
            system_settings.logo.save(f.name, File(f))

    def handle(self, *args, **options):
        self.create_groups()
        self.load_icd10()
        self.load_specializations()
        self.create_system_settings()
        call_command('get_medicines', 'FULL')
        call_command('parse_refundations')
