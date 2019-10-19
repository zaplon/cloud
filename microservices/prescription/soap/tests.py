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
    encoded_prescription = c._sign_prescription(f'{settings.SOAP_DIR}/tests/prescription.xml')
    with open(f'{settings.SOAP_DIR}/tests/prescription_encrypted.txt') as f:
        saved_encoded_prescription = f.read()
    assert encoded_prescription == saved_encoded_prescription


def test_sending_example_prescription():
    c = PrescriptionClient()
    encoded_prescription = c._sign_prescription(f'{settings.SOAP_DIR}/tests/example_prescription.xml')
    prescriptions = [{'recepta':{'identyfikatorDokumentuWPakiecie': 123, 'tresc': encoded_prescription}}]
    # with open(f'{settings.SOAP_DIR}/tests/prescription_encrypted.txt') as f:
    #     prescriptions = [{'recepta':{'identyfikatorDokumentuWPakiecie': '123', 'tresc': f.read().encode()}}]
    res = c.client.service.zapisPakietuRecept(pakietRecept={'recepty': prescriptions})
    print(res)


def test_sending_prescription():
    c = PrescriptionClient()

    pacjent = {'pesel': '88042003997', 'imie': 'Jan', 'drugie_imie': 'Stanisław', 'nazwisko': 'Zapał',
               'kod_pocztowy': '01-105', 'miasto': 'Warszawa',
               'numer_ulicy': '49b', 'numer_lokalu': '153', 'ulica': 'Sowińskiego'}
    lek = {'nazwa': 'Aspiryna', 'kategoria': 'OTC', 'ean': '5909990192618', 'tekst': 'Aspiryna',
           'postac': 'tabletka', 'wielkosc': '10 tabl.'}
    recepta = {'oddzial_nfz': '07', 'uprawnienia_dodatkowe': 'x',
               'numer_recepty': '10010370412139196832256221208216872501117790', 'data_wystawienia': '2019-10-10'}
    podmiot = {'id_lokalne': settings.idPodmiotuOidExt, 'id': settings.idPodmiotuOidExt,
               'id_root': settings.idPodmiotuOidRoot, 'miasto': 'Warszawa', 'numer_domu': '12',
               'regon14': '42625292100002', 'ulica': 'Waryńskiego'}
    pracownik = {'id_ext': '5992363', 'imie': 'Jan', 'nazwisko': 'Kowalski'}
    data = {'pracownik': pracownik, 'podmiot': podmiot, 'leki': [lek], 'recepta': recepta, 'pacjent': pacjent}
    response = c.save_prescriptions(data)
    print(response)
