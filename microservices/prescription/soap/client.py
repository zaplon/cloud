import os
import subprocess
import tempfile
import lxml.etree as ET


from lxml import etree
from requests import Session
from zeep import Client, xsd
from zeep.helpers import serialize_object
from zeep.transports import Transport
from zeep.plugins import HistoryPlugin
from jinja2 import Template, FileSystemLoader, Environment

from .utils import PKCS12Manager, Signature
from . import settings


class PrescriptionXMLHandler(object):
    def __init__(self, input_data):
        self.nfz_settings = input_data

    def _get_prescription_xml(self, input_data):
        pacjent = {'pesel': '', 'imie': '', 'drugie_imie': '', 'nazwisko': '', 'kod_pocztowy': '', 'miasto': '',
                   'numer_ulicy': '', 'numer_lokalu': '', 'plec': '', 'ulica': '', **input_data['pacjent']}
        lek = {'nazwa': '', 'kategoria': '', 'ean': '', 'tekst': '', 'postac': '', 'numer_recepty': '',
               'wielkosc': '', **input_data['lek']}
        if lek.get('refundacja_kod', '100%') != '100%':
            lek['jest_refundowany'] = True
        else:
            lek['jest_refundowany'] = False
        recepta = {'oddzial_nfz': '', 'uprawnienia_dodatkowe': '',  'data_wystawienia': '',
                   **input_data['recepta']}
        podmiot = {'id_lokalne': self.nfz_settings['id_podmiotu_lokalne'], 'id': self.nfz_settings['id_podmiotu_oid_ext'],
                   'id_root': settings.idPodmiotuOidRoot, 'miasto': '', 'numer_domu': '',
                   'regon14': '',
                   'ulica': '', 'numer_domu': '', **input_data['podmiot']}
        pracownik = {'id_ext': self.nfz_settings['id_pracownika_oid_ext'], 'imie': '', 'nazwisko': '',
                     'telefon_rodzaj': 'PUB',
                     **input_data['pracownik']}
        data = {'pacjent': pacjent, 'lek': lek, 'podmiot': podmiot, 'recepta': recepta, 'pracownik': pracownik}

        if lek['jest_refundowany']:
            with open(os.path.join(settings.SOAP_DIR, 'xml_templates', 'recepta_refundowana.xml'), 'r') as f:
                template = Environment(loader=FileSystemLoader(os.path.join(settings.SOAP_DIR, "xml_templates/"))).from_string(f.read())
        else:
            with open(os.path.join(settings.SOAP_DIR, 'xml_templates', 'recepta.xml'), 'r') as f:
                template = Environment(loader=FileSystemLoader(os.path.join(settings.SOAP_DIR, "xml_templates/"))).from_string(f.read())

        return template.render(data)

    def get_prescription_html(self, data):
        docs = {}
        leki = data.pop('leki')
        tmp_files = []
        for i, lek in enumerate(leki):
            data['lek'] = lek
            if i == 0:
                dom = ET.fromstring(self._get_prescription_xml(data).encode())
                continue
            xml = self._get_prescription_xml(data)
            tmp_file = tempfile.NamedTemporaryFile(suffix='.xml')
            tmp_file.write(xml.encode())
            tmp_file.seek(0)
            tmp_files.append(tmp_file)
            docs[f'doc{i + 1}FN'] = ET.XSLT.strparam(tmp_file.name)
        xslt_tree = ET.parse(f'{settings.SOAP_DIR}/prescription.xsl')
        xslt = ET.XSLT(xslt_tree)
        try:
            if data['recepta'].get('kluczPakietu'):
                new_dom = xslt(dom, kluczPakietu=ET.XSLT.strparam(data['recepta']['kluczPakietu']),
                               receptWPakiecie=str(len(leki)), kodPakietu=data['recepta']['kodPakietu'], **docs)
            else:
                new_dom = xslt(dom, receptWPakiecie=str(len(leki)), **docs)
        finally:
            for tmp_file in tmp_files:
                tmp_file.close()
        return ET.tostring(new_dom, pretty_print=True)


class PrescriptionSigningError(Exception):
    pass


class PrescriptionClient(PrescriptionXMLHandler):
    @staticmethod
    def _get_cert_location(cert_path):
        if 'certs' in cert_path:
            return f'/certs/{cert_path.split("/")[-1]}'
        else:
            return cert_path

    def __init__(self, input_data):
        super().__init__(input_data)
        pkcs12 = PKCS12Manager(self._get_cert_location(input_data.pop('certificate_tls')),
                               input_data.pop('certificate_tls_password'))
        session = Session()
        session.cert = (pkcs12.getCert(), pkcs12.getKey())
        session.verify = False
        transport = Transport(session=session)
        pkcs12 = PKCS12Manager(self._get_cert_location(input_data.pop('certificate_wsse')),
                               input_data.pop('certificate_wsse_password'))
        self.history = HistoryPlugin()
        if settings.USE_TRANSPORT:
            self.client = Client(settings.WSDL, wsse=Signature(pkcs12.getKey(), pkcs12.getCert()),
                                 transport=transport, plugins=[self.history])
        else:
            self.client = Client(settings.WSDL, wsse=Signature(pkcs12.getKey(), pkcs12.getCert()), plugins=[self.history])
        if input_data['rola_biznesowa'] == 'LEKARZ_LEK_DENTYSTA_FELCZER':
            input_data['id_pracownika_oid_root'] = '2.16.840.1.113883.3.4424.1.6.2'
        elif input_data['rola_biznesowa'] == 'PIELEGNIARKA_POLOZNA':
            input_data['id_pracownika_oid_root'] = '2.16.840.1.113883.3.4424.1.6.3'
        input_data['certificate_user'] = self._get_cert_location(input_data['certificate_user'])
        self.client.set_default_soapheaders(self._add_headers())

    def _add_headers(self):
        header_ns = 'http://csioz.gov.pl/p1/kontekst/mt/v20170510'
        attr = xsd.Element(f'{{{header_ns}}}atrybut',
                           xsd.ComplexType([
                               xsd.Attribute('nazwa', xsd.String()),
                               xsd.Element(f'{{{header_ns}}}wartosc', xsd.String())
                           ]))
        header = xsd.Element(
            f'{{{header_ns}}}kontekstWywolania',
            xsd.ComplexType([attr] * 7)
        )
        header_value = header(atrybut={'wartosc': settings.idPodmiotuOidRoot,
                                       'nazwa': 'urn:csioz:p1:erecepta:kontekst:idPodmiotuOidRoot'},
                              atrybut__1={'wartosc': self.nfz_settings['id_podmiotu_oid_ext'],
                                          'nazwa': 'urn:csioz:p1:erecepta:kontekst:idPodmiotuOidExt'},
                              atrybut__2={'wartosc': self.nfz_settings['id_pracownika_oid_root'],
                                          'nazwa': 'urn:csioz:p1:erecepta:kontekst:idUzytkownikaOidRoot'},
                              atrybut__3={'wartosc': self.nfz_settings['id_pracownika_oid_ext'],
                                          'nazwa': 'urn:csioz:p1:erecepta:kontekst:idUzytkownikaOidExt'},
                              atrybut__4={'wartosc': settings.idMiejscaPracyOidRoot,
                                          'nazwa': 'urn:csioz:p1:erecepta:kontekst:idMiejscaPracyOidRoot'},
                              atrybut__5={'wartosc': self.nfz_settings['id_miejsca_pracy_oid_ext'],
                                          'nazwa': 'urn:csioz:p1:erecepta:kontekst:idMiejscaPracyOidExt'},
                              atrybut__6={'wartosc': self.nfz_settings['rola_biznesowa'],
                                          'nazwa': 'urn:csioz:p1:erecepta:kontekst:rolaBiznesowa'})
        return [header_value]

    def test_connection(self):
            data = {'dataWystawieniaReceptyDo': '2019-09-30T09:57:33',
                    'dataWystawieniaReceptyOd': '2019-09-28T09:57:33',
                    'statusRecepty': 'WYSTAWIONA'}
            try:
                self.client.service.wyszukanieReceptWystawiajacego(kryteriaWyszukiwaniaRecept=data)
            except:
                print(etree.tostring(self.history.last_received['envelope']))
                return False
            return True

    def save_prescriptions(self, data):
        prescriptions = []
        leki = data.pop('leki')
        recepta = self.client.get_type('{http://csioz.gov.pl/p1/erecepta/mt/v20170510}ReceptaMT')
        recepty = self.client.get_type('{http://csioz.gov.pl/p1/erecepta/mt/v20170510}ReceptyMT')
        for i, lek in enumerate(leki):
            data['lek'] = lek
            prescription = self._prepare_prescription(data)
            prescriptions.append(recepta(tresc=prescription, identyfikatorDokumentuWPakiecie=i + 1))
        objects = recepty(prescriptions)
        res = self.client.service.zapisPakietuRecept(pakietRecept={'recepty': objects})
        if 'major' in res['wynik'] and res['wynik']['major'] == 'urn:csioz:p1:kod:major:Sukces':
            status = True
        else:
            status = False
        return status, serialize_object(res)

    def cancel_prescription(self, data):
        tresc = self._prepare_prescription_cancellation(data)
        with open('prescription.xml', 'wb') as f:
            f.write(tresc)
        res = self.client.service.zapisDokumentuAnulowaniaRecepty(kluczRecepty={
            'kluczRecepty': data['recepta']['external_id']}, dokumentAnulowaniaRecepty={'tresc': tresc})
        if 'major' in res['wynik'] and res['wynik']['major'] == 'urn:csioz:p1:kod:major:Sukces':
            status = True
        else:
            status = False
        return status, serialize_object(res)

    def _prepare_prescription_cancellation(self, input_data):
        with open(os.path.join(settings.SOAP_DIR, 'xml_templates', 'anulowanie_recepty.xml'), 'r') as f:
            template = Template(f.read())
        document = template.render(input_data)
        document_signed = self.sign_prescription_from_string(document, self.nfz_settings['certificate_user'],
                                                             self.nfz_settings['certificate_user_password'])
        return document_signed

    def _prepare_prescription(self, input_data):
        prescription = self._get_prescription_xml(input_data)
        with open('prescription.xml', 'w') as f:
            f.write(prescription)
        prescription_signed = self.sign_prescription_from_string(prescription, self.nfz_settings['certificate_user'],
                                                                 self.nfz_settings['certificate_user_password'])
        return prescription_signed
        # return {'recepta': {'identyfikatorDokumentuWPakiecie': i, 'tresc': prescription_signed}}

    @staticmethod
    def _sign_prescription(tmp_prescription, prescription_p12, prescription_p12_pass):
        signed_prescription = subprocess.check_output(f'java --illegal-access=warn -jar {settings.SOAP_DIR}/prescription_signer/signer.jar "{tmp_prescription}" '
                                                      f'"{prescription_p12}" "{prescription_p12_pass}"', shell=True)
        if b'ERROR pl' in signed_prescription:
            raise PrescriptionSigningError
        return signed_prescription[signed_prescription.find(b'<'):-1]

    @staticmethod
    def sign_prescription_from_string(data, prescription_p12, prescription_p12_pass):
        with tempfile.NamedTemporaryFile() as fp:
            fp.write(data.encode())
            fp.seek(0)
            prescription_signed = PrescriptionClient._sign_prescription(fp.name, prescription_p12, prescription_p12_pass)
        return prescription_signed



