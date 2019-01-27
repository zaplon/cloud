from django.db import models


class ExaminationCategory(models.Model):
    name = models.CharField(max_length=256)


class Examination(models.Model):
    name = models.CharField(max_length=256, verbose_name=u'Nazwa')
    code = models.CharField(max_length=16, verbose_name=u'Kod')
    category = models.ForeignKey(ExaminationCategory, related_name='items')
    is_active = models.BooleanField(default=True)


class Referral(models.Model):
    creation_date = models.DateTimeField(auto_now_add=True)
    examinations = models.ManyToManyField(Examination)
    user_id = models.IntegerField()
    doctor_id = models.IntegerField()