# -*- coding: utf-8 -*-
from django.core.management.base import BaseCommand, CommandError
from visit.models import Icd10
from user_profile.models import Specialization
from medicine.models import Medicine
import csv


class Command(BaseCommand):
    help = 'Import data for catalogue'

    def add_arguments(self, parser):
        parser.add_argument('--delete-all',
                            action='store_true',
                            dest='delete_all',
                            help='Delete all before import')

    def handle(self, *args, **options):
        with open('utils/initial_data/icd10.csv', 'rb') as csv_file:
            data = csv.reader(csv_file, delimiter=',', quotechar='"')
            for row in data:
                icd, _ = Icd10.objects.get_or_create(desc=row[2], code=row[1])
                print icd.desc
            print '***** Icd 10 imported *****'

        with open('utils/initial_data/specializations.csv', 'rb') as csv_file:
            data = csv.reader(csv_file, delimiter=',', quotechar='"')
            for row in data:
                specialization, _ = Specialization.objects.get_or_create(name=row[2], code=row[1], code_misal=row[2])
                print specialization.name
            print '***** Specializations imported *****'

        with open('utils/initial_data/medicines.csv', 'rb') as csv_file:
            data = csv.reader(csv_file, delimiter=',', quotechar='"')
            for row in data:
                medicine, _ = Medicine.objects.get_or_create(name=row[2], code=row[1], code_misal=row[2])
                print medicine.name
            print '***** Medicines imported *****'
