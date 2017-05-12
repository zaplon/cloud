from .models import *

APP = 'medicine'

class MedicineRouter(object):
    def db_for_read(self, model, **hints):
        if model._meta.app_label == APP:
            return 'medicines'

    def db_for_write(self, model, **hints):
        if model._meta.app_label == APP:
            return 'medicines'
