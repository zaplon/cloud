#!/usr/bin/env bash
./manage.py migrate
./manage.py migrate --database=medicines
./manage.py setup
./manage.py create_user doctor lekarz Gabinet123
./manage.py create_user admin admin Gabinet123
