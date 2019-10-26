import base64
import subprocess

from lxml import etree
from .client import PrescriptionClient
from . import settings


def test_client():
    c = PrescriptionClient()
    try:
        data = {'dataWystawieniaReceptyDo': '2019-09-30T09:57:33',
                'dataWystawieniaReceptyOd': '2019-09-28T09:57:33',
                'statusRecepty': 'WYSTAWIONA'}
        c.client.service.wyszukanieReceptWystawiajacego(kryteriaWyszukiwaniaRecept=data)
    except:
        print(c.history.last_sent)
        print(etree.tostring((c.history.last_sent['envelope'])))
        print(c.history.last_received)
        raise


def test_signing_prescription():
    c = PrescriptionClient()
    c._sign_prescription(f'{settings.SOAP_DIR}/tests/prescription.xml')


def test_sending_example_prescription():
    c = PrescriptionClient()
    encoded_prescription = c._sign_prescription(f'{settings.SOAP_DIR}/tests/example_prescription.xml')
    prescriptions = [{'recepta':{'identyfikatorDokumentuWPakiecie': 123, 'tresc': encoded_prescription}}]
    # with open(f'{settings.SOAP_DIR}/tests/example_prescription.xml') as f:
    #      tresc = f.read().encode()
    #      prescriptions = [{'recepta':{'identyfikatorDokumentuWPakiecie': 1, 'tresc': tresc[0:-1]}}]
    res = c.client.service.zapisPakietuRecept(pakietRecept={'recepty': prescriptions})
    print(res)


def test_sending_prescription():
    c = PrescriptionClient()

    pacjent = {'pesel': '70032816894', 'imie': 'Jan', 'drugie_imie': 'Stanisław', 'nazwisko': 'Zapał',
               'kod_pocztowy': '01-105', 'miasto': 'Warszawa',
               'numer_ulicy': '49b', 'numer_lokalu': '153', 'ulica': 'Sowińskiego'}
    lek = {'nazwa': 'Aspiryna', 'kategoria': 'OTC', 'ean': '5909990192618', 'tekst': 'Aspiryna',
           'postac': 'tabletka', 'wielkosc': 10}
    recepta = {'oddzial_nfz': '07', 'uprawnienia_dodatkowe': 'x',
               'numer_recepty': '1001037041213919683225', 'data_wystawienia': '20191020'}
    podmiot = {'id_lokalne': settings.idPodmiotuLokalne, 'id': settings.idPodmiotuOidExt,
               'id_root': settings.idPodmiotuOidRoot, 'miasto': 'Warszawa', 'numer_domu': '12',
               'regon14': '97619191000009', 'ulica': 'Waryńskiego'}
    pracownik = {'id_ext': '5992363', 'imie': 'Jan', 'nazwisko': 'Kowalski'}
    data = {'pracownik': pracownik, 'podmiot': podmiot, 'leki': [lek], 'recepta': recepta, 'pacjent': pacjent}
    response = c.save_prescriptions(data)
    print(response)
