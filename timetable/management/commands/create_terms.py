# -*- coding: utf-8 -*-
import csv
from datetime import datetime, timedelta

from django.core.management.base import BaseCommand, CommandError

from django.contrib.auth.models import Permission, Group, User
from django.core.management import call_command

from timetable.models import Term
from visit.models import Icd10
from user_profile.models import Specialization, Doctor, SystemSettings
from django.core.files import File


class Command(BaseCommand):
    help = 'Create terms for doctors'

    def handle(self, *args, **options):
        end_date = datetime.now() + timedelta(days=31)
        for d in Doctor.objects.all():
            start_date = d.terms_generated_till
            if start_date >= end_date:
                continue
            Term.create_terms_for_period(d, start_date, end_date)

