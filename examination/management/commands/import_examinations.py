# -*- coding: utf-8 -*-
import json
import os

from django.core.management.base import BaseCommand
from examination.models import Examination, ExaminationCategory


class Command(BaseCommand):
    help = 'Import data'

    def handle(self, *args, **options):
        with open(os.path.join('examination', 'initial_data', 'examinations.json'), encoding='utf8') as f:
            data = json.loads(f.read())
        for category, items in data.items():
            examinations = []
            c, _ = ExaminationCategory.objects.get_or_create(name=category)
            for item in items:
                examinations.append(Examination(name=item, code=item[0:3], category=c))
            Examination.objects.bulk_create(examinations)
