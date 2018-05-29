# -*- coding: utf-8 -*-
from django.core.management.base import BaseCommand, CommandError
from visit.models import Icd10, TabParent, TabTypes
from user_profile.models import Specialization
from medicine.models import Medicine, MedicineParent
from django.core.management import call_command
import csv


class Command(BaseCommand):
    help = 'Import data'

    def add_arguments(self, parser):
        parser.add_argument('--delete-all',
                            action='store_true',
                            dest='delete_all',
                            help='Delete all before import')

    def handle(self, *args, **options):
        if options['delete_all']:
            TabParent.objects.all().delete()
            Icd10.objects.all().delete()
            Specialization.objects.all().delete()

            TabParent.objects.get_or_create(name='default', type=TabTypes.DEFAULT, can_add_templates=True)
            TabParent.objects.get_or_create(name='icd10', type=TabTypes.ICD10, obligatory=True)
            TabParent.objects.get_or_create(name='medicines', type=TabTypes.MEDICINES)
            TabParent.objects.get_or_create(name='notes', type=TabTypes.NOTES)
            TabParent.objects.get_or_create(name='services', type=TabTypes.VIDEO)
            TabParent.objects.get_or_create(name='video', type=TabTypes.SERVICES)

        with open('g_utils/initial_data/icd10.csv', 'r', encoding='utf8') as csv_file:
            data = csv.reader(csv_file, delimiter=',', quotechar='"')
            for row in data:
                icd, _ = Icd10.objects.get_or_create(desc=row[2], code=row[1])
                print(icd.desc)
            print('***** Icd 10 imported *****')

        with open('g_utils/initial_data/specializations.csv', 'r', encoding='utf8') as csv_file:
            data = csv.reader(csv_file, delimiter=',', quotechar='"')
            for row in data:
                specialization, _ = Specialization.objects.get_or_create(name=row[1], code=row[2], code_misal=row[2])
                print(specialization.name)
            print ('***** Specializations imported *****')

        call_command('loaddata', 'groups')