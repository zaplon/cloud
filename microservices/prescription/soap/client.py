import json
import os
import subprocess
import tempfile

from lxml import etree
from requests import Session
from zeep import Client, xsd
from zeep.helpers import serialize_object
from zeep.transports import Transport
from zeep.plugins import HistoryPlugin
from jinja2 import Template

from .utils import PKCS12Manager, Signature
from . import settings


class PrescriptionClient(object):

    @staticmethod
    def _get_cert_location(cert_path):
        if 'certs' in cert_path:
            return f'/certs/{cert_path.split("/")[-1]}'
        else:
            return cert_path

    def __init__(self, input_data):
        pkcs12 = PKCS12Manager(self._get_cert_location(input_data.pop('certificate_tls')),
                               input_data.pop('certificate_tls_password'))
        session = Session()
        session.cert = (pkcs12.getCert(), pkcs12.getKey())
        session.verify = False
        transport = Transport(session=session)
        pkcs12 = PKCS12Manager(self._get_cert_location(input_data.pop('certificate_wsse')),
                               input_data.pop('certificate_wsse_password'))
        self.history = HistoryPlugin()
        self.client = Client(settings.WSDL, wsse=Signature(pkcs12.getKey(), pkcs12.getCert()),
                             transport=transport, plugins=[self.history])
        if input_data['rola_biznesowa'] == 'LEKARZ_LEK_DENTYSTA_FELCZER':
            input_data['id_pracownika_oid_root'] = '2.16.840.1.113883.3.4424.1.6.2'
        elif input_data['rola_biznesowa'] == 'PIELEGNIARKA_POLOZNA':
            input_data['id_pracownika_oid_root'] = '2.16.840.1.113883.3.4424.1.6.3'
        input_data['certificate_user'] = self._get_cert_location(input_data['certificate_user'])
        self.nfz_settings = input_data
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
        for i, lek in enumerate(leki):
            data['lek'] = lek
            prescription = self._prepare_prescription(data, i + 1)
            prescriptions.append(prescription)
        res = self.client.service.zapisPakietuRecept(pakietRecept={'recepty': prescriptions})
        if 'major' in res['wynik'] and res['wynik']['major'] == 'urn:csioz:p1:kod:major:Sukces':
            status = True
        else:
            status = False
        return status, serialize_object(res)

    def cancel_prescription(self, data):
        tresc = self._prepare_prescription_cancellation(data)
        res = self.client.service.zapisDokumentuAnulowaniaRecepty(kluczRecepty={
            'kluczRecepty': data['prescription']['external_id']}, dokumentAnulowaniaRecepty={'tresc': tresc})
        if 'major' in res['wynik'] and res['wynik']['major'] == 'urn:csioz:p1:kod:major:Sukces':
            status = True
        else:
            status = False
        return status

    def _prepare_prescription_cancellation(self, input_data):
        with open(os.path.join(settings.SOAP_DIR, 'xml_templates', 'cancel_prescription.xml'), 'r') as f:
            template = Template(f.read())
        document = template.render(input_data)
        document_signed = self.sign_prescription_from_string(document, self.nfz_settings['certificate_user'],
                                                             self.nfz_settings['certificate_user_password'])
        return document_signed


    def _prepare_prescription(self, input_data, i):
        with open(os.path.join(settings.SOAP_DIR, 'xml_templates', 'prescription.xml'), 'r') as f:
            template = Template(f.read())

        pacjent = {'pesel': '', 'imie': '', 'drugie_imie': '', 'nazwisko': '', 'kod_pocztowy': '', 'miasto': '',
                   'numer_ulicy': '', 'numer_lokalu': '', 'ulica': '', **input_data['pacjent']}
        lek = {'nazwa': '', 'categoria': '', 'ean': '', 'tekst': '', 'postac': '', 'wielkosc': '', **input_data['lek']}
        recepta = {'oddzial_nfz': '', 'uprawnienia_dodatkowe': '', 'numer_recepty': '', 'data_wystawienia': '',
                   **input_data['recepta']}
        podmiot = {'id_lokalne': self.nfz_settings['id_podmiotu_lokalne'], 'id': self.nfz_settings['id_podmiotu_oid_ext'],
                   'id_root': settings.idPodmiotuOidRoot, 'miasto': '', 'numer_domu': '',
                   'regon14': '',
                   'ulica': '', 'numer_domu': '', **input_data['podmiot']}
        pracownik = {'id_ext': self.nfz_settings['id_pracownika_oid_ext'], 'imie': '', 'nazwisko': '',
                     **input_data['pracownik']}
        data = {'pacjent': pacjent, 'lek': lek, 'podmiot': podmiot, 'recepta': recepta, 'pracownik': pracownik}
        print(data)
        prescription = template.render(data)
        prescription_signed = self.sign_prescription_from_string(prescription, self.nfz_settings['certificate_user'],
                                                                 self.nfz_settings['certificate_user_password'])
        return {'recepta': {'identyfikatorDokumentuWPakiecie': i, 'tresc': prescription_signed}}

    @staticmethod
    def _sign_prescription(tmp_prescription, prescription_p12, prescription_p12_pass):
        signed_prescription = subprocess.check_output(f'java -jar {settings.SOAP_DIR}/prescription_signer/signer.jar "{tmp_prescription}" '
                                                      f'"{prescription_p12}" "{prescription_p12_pass}"', shell=True)
        return signed_prescription

    @staticmethod
    def sign_prescription_from_string(data, prescription_p12, prescription_p12_pass):
        with tempfile.NamedTemporaryFile() as fp:
            fp.write(data.encode())
            fp.seek(0)
            prescription_signed = PrescriptionClient._sign_prescription(fp.name, prescription_p12, prescription_p12_pass)
        return prescription_signed
