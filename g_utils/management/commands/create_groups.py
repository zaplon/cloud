# -*- coding: utf-8 -*-
import csv

from django.core.management.base import BaseCommand, CommandError

from django.contrib.auth.models import Permission, Group, User
from django.core.management import call_command
from visit.models import Icd10
from user_profile.models import Specialization, Doctor, SystemSettings
from django.core.files import File


class Command(BaseCommand):
    help = 'Create required groups'

    def create_groups(self):
        groups = {'Lekarze': ['_visit', '_result', '_term', '_medicine', '_template', '_tab',
                              'can_add_prescription', '_prescriptionnumber', '_refundation', '_prescription',
                              '_nfzsettings', '_patient'],
                  'Rejestracja': ['_term', '_patient', 'view_medicine', '_result'],
                  'Administratorzy': ['_term',  '_result', '_user', '_service', '_localization', '_patient',
                                      '_systemsettings', 'can_view_statistics']}
        for group_name, permissions_patterns in groups.items():
            permissions = Permission.objects.none()
            for p in permissions_patterns:
                permissions |= Permission.objects.filter(codename__icontains=p)
            group, _ = Group.objects.get_or_create(name=group_name)
            group.permissions.add(*permissions)

    def handle(self, *args, **options):
        self.create_groups()

