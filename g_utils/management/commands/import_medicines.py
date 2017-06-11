# -*- coding: utf-8 -*-
from django.core.management.base import BaseCommand, CommandError
from visit.models import Icd10
from user_profile.models import Specialization
from medicine.models import Medicine, MedicineParent
import csv


class Command(BaseCommand):
    help = 'Import data'

    def add_arguments(self, parser):
        parser.add_argument('--delete-all',
                            action='store_true',
                            dest='delete_all',
                            help='Delete all before import')

    def handle(self, *args, **options):

        MedicineParent.objects.all().delete()
        Medicine.objects.all().delete()


        with open('g_utils/initial_data/leki-a.csv', 'rU') as csv_file:
            data = csv.reader(csv_file, delimiter=',', quotechar='"')
            j = 0
            for row in data:
                # j += 1
                # if j > 100:
                #     break
                medicine, _ = MedicineParent.objects.get_or_create(name=row[1], composition=row[2], form=row[3],
                                                                   permission_nr=row[9], mah=row[8], dose=row[4],
                                                                   manufacturer_country=row[11])

                sizes = row[5].split('\n')
                cats = row[6].split('\n')
                print sizes
                for i, ean in enumerate(row[7].split('\n')):
                    size = sizes[i] if i < len(sizes) else ' '
                    m = Medicine.objects.create(parent=medicine, ean=ean, size=size, availability_cat=cats[i],
                                                   in_use=True)

                print medicine.name
            print '***** Medicines A imported *****'

        with open('g_utils/initial_data/leki-b.csv', 'rU') as csv_file:
            data = csv.reader(csv_file, delimiter=',', quotechar='"')
            for row in data:
                medicine, _ = MedicineParent.objects.get_or_create(name=row[1], composition=row[2], form=row[3],
                                                                   mah=row[8], dose=row[4], manufacturer_country=row[10])

                sizes = row[5].split('\n')
                cats = row[7].split('\n')
                print sizes
                for i, ean in enumerate(row[6].split('\n')):
                    try:
                        size = sizes[i]
                    except:
                        size = ' '
                    m = Medicine.objects.create(parent=medicine, ean=ean, size=size, availability_cat=cats[i],
                                                   in_use=True)

                print medicine.name
            print '***** Medicines B imported *****'

        with open('g_utils/initial_data/leki-c.csv', 'rU') as csv_file:
            data = csv.reader(csv_file, delimiter=',', quotechar='"')
            for row in data:
                medicine, _ = MedicineParent.objects.get_or_create(name=row[1], form=row[3], manufacturer_country=row[11],
                                                                   permission_nr=row[9], mah=row[10], dose=row[4])

                sizes = row[5].split('\n')
                cats = row[6].split('\n')
                for i, ean in enumerate(row[7].split('\n')):
                    try:
                        size = sizes[i] if i < len(sizes) else ' '
                    except:
                        size = ' '
                    m = Medicine.objects.create(parent=medicine, ean=ean, size=size, availability_cat=cats[i],
                                                   in_use=True)

                print medicine.name
            print '***** Medicines C imported *****'



