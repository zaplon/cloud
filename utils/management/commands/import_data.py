# -*- coding: utf-8 -*-
from django.core.management.base import BaseCommand, CommandError
from visit.models import Icd10
from user_profile.models import Specialization
from medicine.models import Medicine, MedicineParent
import csv


class Command(BaseCommand):
    help = 'Import data for catalogue'

    def add_arguments(self, parser):
        parser.add_argument('--delete-all',
                            action='store_true',
                            dest='delete_all',
                            help='Delete all before import')

    def handle(self, *args, **options):
        # with open('utils/initial_data/icd10.csv', 'rb') as csv_file:
        #     data = csv.reader(csv_file, delimiter=',', quotechar='"')
        #     for row in data:
        #         icd, _ = Icd10.objects.get_or_create(desc=row[2], code=row[1])
        #         print icd.desc
        #     print '***** Icd 10 imported *****'
        #
        # with open('utils/initial_data/specializations.csv', 'rb') as csv_file:
        #     data = csv.reader(csv_file, delimiter=',', quotechar='"')
        #     for row in data:
        #         specialization, _ = Specialization.objects.get_or_create(name=row[2], code=row[1], code_misal=row[2])
        #         print specialization.name
        #     print '***** Specializations imported *****'

        with open('utils/initial_data/leki-a.csv', 'rb') as csv_file:
            data = csv.reader(csv_file, delimiter=',', quotechar='"')
            j = 0
            for row in data:
                medicine, _ = MedicineParent.objects.get_or_create(name=row[1], composition=row[2], form=row[3],
                                                                   permission_nr=row[9], mah=row[8], dose=row[4])

                sizes = row[5].split('\r')
                cats = row[6].split('\r')
                print sizes
                for i, ean in enumerate(row[7].split('\r')):
                    m = Medicine.objects.create(parent=medicine, ean=ean, size=sizes[i], availability_cat=cats[i],
                                                   in_use=True)

                print medicine.name
                j += 1
                if j > 100:
                    break
            print '***** Medicines imported *****'


        # with open('utils/initial_data/medicines.csv', 'rb') as csv_file:
        #     data = csv.reader(csv_file, delimiter=',', quotechar='"')
        #     for row in data:
        #         medicine, _ = Medicine.objects.get_or_create(name=row[2], code=row[1], code_misal=row[2])
        #         print medicine.name
        #     print '***** Medicines imported *****'
