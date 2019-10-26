import base64
import os
import subprocess
import tempfile

from requests import Session
from zeep import Client, xsd
from zeep.transports import Transport
from zeep.plugins import HistoryPlugin
from jinja2 import Template

from .utils import PKCS12Manager, Signature
from . import settings


class PrescriptionClient(object):

    def __init__(self):
        pkcs12 = PKCS12Manager(settings.CLIENT_P12, settings.CLIENT_P12_PASS)
        session = Session()
        session.cert = (pkcs12.getCert(), pkcs12.getKey())
        session.verify = False
        transport = Transport(session=session)
        pkcs12 = PKCS12Manager(settings.WSSE_P12, settings.WSSE_P12_PASS)
        self.history = HistoryPlugin()
        self.client = Client(settings.WSDL, wsse=Signature(pkcs12.getKey(), pkcs12.getCert()),
                             transport=transport, plugins=[self.history])
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
                              atrybut__1={'wartosc': settings.idPodmiotuOidExt,
                                          'nazwa': 'urn:csioz:p1:erecepta:kontekst:idPodmiotuOidExt'},
                              atrybut__2={'wartosc': settings.idUzytkownikaOidRoot,
                                          'nazwa': 'urn:csioz:p1:erecepta:kontekst:idUzytkownikaOidRoot'},
                              atrybut__3={'wartosc': settings.idUzytkownikaOidExt,
                                          'nazwa': 'urn:csioz:p1:erecepta:kontekst:idUzytkownikaOidExt'},
                              atrybut__4={'wartosc': settings.idMiejscaPracyOidRoot,
                                          'nazwa': 'urn:csioz:p1:erecepta:kontekst:idMiejscaPracyOidRoot'},
                              atrybut__5={'wartosc': settings.idMiejscaPracyOidExt,
                                          'nazwa': 'urn:csioz:p1:erecepta:kontekst:idMiejscaPracyOidExt'},
                              atrybut__6={'wartosc': settings.rolaBiznesowa,
                                          'nazwa': 'urn:csioz:p1:erecepta:kontekst:rolaBiznesowa'})
        return [header_value]

    def save_prescriptions(self, data):
        prescriptions = []
        leki = data.pop('leki')
        for lek in leki:
            data['lek'] = lek
            prescription = self._prepare_prescription(data)
            prescriptions.append(prescription)
        return self.client.service.zapisPakietuRecept(pakietRecept={'recepty': prescriptions})


    def _prepare_prescription(self, input_data):
        with open(os.path.join(settings.SOAP_DIR, 'xml_templates', 'prescription.xml'), 'r') as f:
            template = Template(f.read())

        pacjent = {'pesel': '', 'imie': '', 'drugie_imie': '', 'nazwisko': '', 'kod_pocztowy': '', 'miasto': '',
                   'numer_ulicy': '', 'numer_lokalu': '', 'ulica': '', **input_data['pacjent']}
        lek = {'nazwa': '', 'categoria': '', 'ean': '', 'tekst': '', 'postac': '', 'wielkosc': '', **input_data['lek']}
        recepta = {'oddzial_nfz': '', 'uprawnienia_dodatkowe': '', 'numer_recepty': '', 'data_wystawienia': '',
                   **input_data['recepta']}
        podmiot = {'id_lokalne': settings.idPodmiotuLokalne, 'id': settings.idPodmiotuOidExt,
                   'id_root': settings.idPodmiotuOidRoot, 'miasto': '', 'numer_domu': '', 'regon14': '', 'ulica': '',
                   'numer_domu': '', **input_data['podmiot']}
        pracownik = {'id_ext': '', 'imie': '', 'nazwisko': '', **input_data['pracownik']}
        data = {'pacjent': pacjent, 'lek': lek, 'podmiot': podmiot, 'recepta': recepta, 'pracownik': pracownik}
        prescription = template.render(data)
        with tempfile.NamedTemporaryFile() as fp:
            fp.write(prescription.encode())
            fp.seek(0)
            prescription_signed = self._sign_prescription(fp.name)
        return {'recepta': {'identyfikatorDokumentuWPakiecie': 1, 'tresc': prescription_signed}}

    def _sign_prescription(self, tmp_prescription):
        signed_prescription = subprocess.check_output(f'java -jar {settings.SOAP_DIR}/prescription_signer/signer.jar "{tmp_prescription}" '
                                                      f'"{settings.PRESCRIPTION_P12}" {settings.PRESCRIPTION_P12_PASS}', shell=True)
        return signed_prescription
