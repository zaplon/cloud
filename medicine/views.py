import zipfile
from xml.dom import minidom

from rest_framework.response import Response
from rest_framework.views import APIView

from medicine.models import Prescription, PrescriptionNumber


class AddPrescriptionNumbersView(APIView):
    queryset = Prescription.objects.all()

    def post(self, request):
        if request.FILES['file'].name.find('.xmz') > 0:
            source = zipfile.ZipFile(request.FILES['file']).read(request.FILES['file'].name[0:-3] + 'xml')
        else:
            source = request.FILES['file'].read()
        try:
            xml = minidom.parseString(source)
        except:
            return Response(status=400, data=u'Błąd przetwarzania pliku.')

        # node = xml.getElementsByTagName('lekarz')
        ns = xml.getElementsByTagName('n')
        for n in ns:
            val = n.childNodes[0].nodeValue
            try:
                PrescriptionNumber.objects.get(number=val)
            except:
                r = PrescriptionNumber(doctor=self.request.user.doctor, number=val)
                r.save()
            return Response(status=200)
