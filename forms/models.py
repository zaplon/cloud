from django.db import models
from django.contrib.auth.models import User


# Create your models here.
class Form(models.Model):
    user = models.ForeignKey(User, related_name='forms')
    created = models.DateTimeField(auto_now_add=True)
    name = models.CharField(max_length=200)
    path = models.CharField(max_length=200)