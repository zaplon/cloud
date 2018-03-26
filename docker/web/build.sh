#!/usr/bin/env bash
export DJANGO_SETTINGS_MODULE=production_settings
find . -name '*.pyc' -print0 | xargs -0 rm
echo yes | ./manage.py collectstatic
echo yes | ./manage.py compress