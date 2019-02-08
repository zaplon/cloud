#!/usr/bin/env bash
./manage.py load_csv_data
./manage.py import_medicines
./manage.py parse_refundations
./manage.py loaddata auth.json
./manage.py loaddata settings.json
