# -*- coding: utf-8 -*-
import re

from django.core.management.base import BaseCommand, CommandError
from user_profile.models import Patient


class Command(BaseCommand):
    help = 'Fill addresses'

    def fill_address_details():
        for p in Patient.objects.filter(address__isnull=False, city__isnull=True):
            address = re.sub(' +', ' ', p.address).replace('.', '')
            print('address: %s' % address)
            postal_code_match = re.search(r'[0-9]{2} *- *[0-9]{3}', address)
            if postal_code_match:
                postal_code = postal_code_match.group(0)
                address = address.replace(postal_code, '')
                p.postal_code = postal_code

            street_and_number_match = re.search(' [ul.|ul|UL]+.*[0-9]+[a-zA-Z]*/*[0-9]*', address)
            if street_and_number_match:
                street_and_number = street_and_number_match.group(0).strip()
                address = address.replace(street_and_number, '')
                street_and_number = street_and_number.replace('ul.', ' ').replace('ul', '').replace('UL', '').strip()
                if '/' in street_and_number:
                    parts = street_and_number.split('/')
                    street_and_number, apartment_number = parts[0], parts[1]
                    p.apartment_number = apartment_number
                parts = street_and_number.split(' ')
                p.street = ' '.join(parts[0:-1]).strip()
                p.street_number = parts[-1].strip()

            street_number_match = re.search('[0-9]+[a-zA-Z]*', address)
            if street_number_match:
                street_number = street_number_match.group(0)
                address = address.replace(street_number, '')
                p.street_number = street_number.strip()

            p.city = address.strip()

            p.save()

    def handle(self, *args, **options):
        self.fill_address_details()
