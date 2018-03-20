#!/usr/bin/env bash
export DJANGO_SETTINGS_MODULE=production_settings
./manage.py collectstatic
./manage.py compress
./manage.py migrate --database=default
./manage.py migrate --database=medicines
