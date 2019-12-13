# -*- coding: utf-8 -*-
import csv

from django.core.management.base import BaseCommand, CommandError

from django.contrib.auth.models import Permission, Group, User
from user_profile.models import Doctor, Profile



class Command(BaseCommand):
    help = 'Creates a user'

    def add_arguments(self, parser):
        parser.add_argument('type', type=str)
        parser.add_argument('username', type=str)
        parser.add_argument('password', type=str)

    def create_doctor(self, username, password):
        u = User.objects.create_user(username=username, password=password)
        u.groups.add(Group.objects.get(name='Lekarze'))
        Profile.objects.create(user=u, role='doctor')
        Doctor.objects.create(user=u)

    def create_admin(self, username, password):
        u = User.objects.create_user(username=username, password=password)
        u.groups.add(Group.objects.get(name='Administratorzy'))
        Profile.objects.create(user=u, role='admin')
        Doctor.objects.create(user=u)

    def handle(self, *args, **options):
        user_type = options['type'].lower()
        if user_type == 'doctor':
            self.create_doctor(options['username'], options['password'])
        elif user_type == 'admin':
            self.create_admin(options['username'], options['password'])
