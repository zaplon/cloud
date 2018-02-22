from django.views.generic import TemplateView
from .models import MedicineParent, Prescription


class MedicineView(TemplateView):
    template_name = 'medicine/medicine.html'

    def get_context_data(self, **kwargs):
        pk = kwargs['pk']
        object = MedicineParent.objects.get(id=pk)
        ctx = {'medicines': object.children.all(), 'object': object}
        return ctx


class PrescriptionView(TemplateView):
    template_name = 'medicine/prescription.html'

    def get_context_data(self, **kwargs):
        pk = kwargs['pk']
        object = Prescription.objects.get(id=pk)
        ctx = {'object': object}
        return ctx


