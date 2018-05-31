# -*- coding: utf-8 -*-
from django.core.management.base import BaseCommand, CommandError

from timetable.models import Term, Service, Localization
from visit.models import Icd10, Visit
from user_profile.models import Specialization, Doctor
from medicine.models import Medicine, MedicineParent
from django.core.management import call_command
import csv


class Command(BaseCommand):
    help = 'Clean data'

    def add_arguments(self, parser):
        pass

    def handle(self, *args, **options):
        Visit.objects.all().delete()
        Term.objects.all().delete()
        Service.objects.all().delete()
        Localization.objects.all().delete()
        Doctor.objects.all().delete()