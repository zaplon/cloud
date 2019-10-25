import urllib
from xml.etree import ElementTree
import urllib.request
from xml.etree.ElementTree import QName

from django.core.management.base import BaseCommand, CommandError
from medicine.models import Medicine, MedicineParent


class MedicineImportException(Exception):
    pass


class Command(BaseCommand):
    growth_xml_source = 'http://pub.rejestrymedyczne.csioz.gov.pl/pobieranie_WS/Pobieranie.ashx?filetype=XMLUpdateFile&regtype=RPL_FILES_GROWTH'
    full_xml_source = 'http://pub.rejestrymedyczne.csioz.gov.pl/pobieranie_WS/Pobieranie.ashx?filetype=XMLUpdateFile&regtype=RPL_FILES_BASE'
    file_name = "meds.xml"
    xml_to_medicine_parent_dict = {
        'nazwaProduktu': 'name', 'moc': 'dose', 'postac': 'form', 'nazwaPowszechnieStosowana': 'inn',
        'podmiotOdpowiedzialny': 'mah', 'numerPozwolenia': 'permission_nr', 'id': 'external_id'
    }
    xml_to_medicine_dict = {
        'kategoriaDostepnosci': 'availability_cat', 'id': 'external_id'
    }

    def add_arguments(self, parser):
        parser.add_argument('import_type', type=str, help='Type of import FULL|GROWTH')

    def get_file(self, import_type):
        if import_type == 'FULL':
            urllib.request.urlretrieve(self.full_xml_source, self.file_name)
        elif import_type == 'GROWTH':
            urllib.request.urlretrieve(self.growth_xml_source, self.file_name)
        else:
            raise MedicineImportException('Wrong type of import: %s' % import_type)

    def parse_file(self):
        namespace = 'http://rejestrymedyczne.csioz.gov.pl/rpl/eksport-danych-v1.0'
        document = ElementTree.parse(self.file_name)
        meds_data = document.findall(str(QName(namespace, 'produktLeczniczy')))
        for med in meds_data:
            to_delete = False
            if med.attrib.get('status') == 'Usuniety':
                to_delete = True
            data = {'in_use': not to_delete}
            active_substances = med.findall('.//{%s}substancjaCzynna' % namespace)
            substances = []
            for substance in active_substances:
                if substance.text:
                    substances.append(substance.text)
            if substances:
                data['composition'] = ' '.join(substances)
            for xml_field, db_field in self.xml_to_medicine_parent_dict.items():
                data[db_field] = med.attrib.get(xml_field, '')
            parent, _ = MedicineParent.objects.update_or_create(name=data['name'], inn=data['inn'], defaults=data)
            sizes = med.findall('.//{%s}opakowanie' % namespace)
            if sizes:
                for child in sizes:
                    data = {'ean': child.attrib.get('kodEAN', ''), 'in_use': True}
                    if child.attrib.get('skasowane', 'NIE') == 'TAK':
                        Medicine.objects.filter(external_id=child.attrib['id']).update(in_use=False)
                        continue
                    for xml_field, db_field in self.xml_to_medicine_dict.items():
                        data[db_field] = child.attrib.get(xml_field, '')
                    data['parent'] = parent
                    data['size'] = '%s %s' % (child.attrib.get('wielkosc'), child.attrib.get('jednostkaWielkosci'))
                    Medicine.objects.update_or_create(external_id=data['external_id'], defaults=data)
                    print('Medicine updated: %s' % data)

    def handle(self, *args, **options):
        import_type = options['import_type']
        self.get_file(import_type)
        if import_type == 'FULL':
            MedicineParent.objects.all().update(in_use=False)
        self.parse_file()

