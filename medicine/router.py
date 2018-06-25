from .models import *

APP = 'medicine'
MODELS = ['medicine', 'medicineparent', 'refundation']


class MedicineRouter(object):
    def db_for_read(self, model, **hints):
        if model._meta.app_label == APP and model._meta.model_name in MODELS:
            return 'medicines'

    def db_for_write(self, model, **hints):
        if model._meta.app_label == APP and model._meta.model_name in MODELS:
            return 'medicines'

    def allow_relation(self, obj1, obj2, **hints):
        return True
