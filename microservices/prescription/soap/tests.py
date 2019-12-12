import uuid
from datetime import datetime
from time import sleep

from lxml import etree
from .client import PrescriptionClient
from . import settings


def create_client():
    input_data = {'certificate_tls': settings.CLIENT_P12, 'certificate_tls_password': settings.CLIENT_P12_PASS,
                  'certificate_wsse': settings.WSSE_P12, 'certificate_wsse_password': settings.WSSE_P12_PASS,
                  'certificate_user': settings.PRESCRIPTION_P12,
                  'certificate_user_password': settings.PRESCRIPTION_P12_PASS,
                  'id_podmiotu_oid_root': settings.idPodmiotuOidRoot, 'id_podmiotu_oid_ext': settings.idPodmiotuOidExt,
                  'id_podmiotu_lokalne': settings.idPodmiotuLokalne,
                  'id_pracownika_oid_root': settings.idPracownikaOidRoot,
                  'id_pracownika_oid_ext': settings.idPracownikaOidExt,
                  'id_miejsca_pracy_oid_root': settings.idMiejscaPracyOidRoot,
                  'id_miejsca_pracy_oid_ext': settings.idMiejscaPracyOidExt, 'rola_biznesowa': settings.rolaBiznesowa}
    return PrescriptionClient(input_data)


def test_client():
    c = create_client()
    try:
        data = {'dataWystawieniaReceptyDo': '2019-09-30T09:57:33',
                'dataWystawieniaReceptyOd': '2019-09-28T09:57:33',
                'statusRecepty': 'WYSTAWIONA'}
        c.client.service.wyszukanieReceptWystawiajacego(kryteriaWyszukiwaniaRecept=data)
    except:
        print(c.history.last_sent)
        print(etree.tostring((c.history.last_sent['envelope'])))
        print(etree.tostring(c.history.last_received['envelope']))
        raise


def test_signing_prescription():
    c = create_client()
    c._sign_prescription(f'{settings.SOAP_DIR}/tests/prescription.xml', settings.PRESCRIPTION_P12,
                         settings.PRESCRIPTION_P12_PASS)


def test_sending_example_prescription():
    c = create_client()
    encoded_prescription = c._sign_prescription(f'{settings.SOAP_DIR}/tests/example_prescription.xml',
                                                settings.PRESCRIPTION_P12, settings.PRESCRIPTION_P12_PASS)
    prescriptions = [{'recepta': {'identyfikatorDokumentuWPakiecie': 123, 'tresc': encoded_prescription}}]
    # with open(f'{settings.SOAP_DIR}/tests/example_prescription.xml') as f:
    #      tresc = f.read().encode()
    #      prescriptions = [{'recepta':{'identyfikatorDokumentuWPakiecie': 1, 'tresc': tresc[0:-1]}}]
    res = c.client.service.zapisPakietuRecept(pakietRecept={'recepty': prescriptions})
    print(res)


def get_prescription_data():
    today = datetime.today().strftime('%Y%m%d')
    pacjent = {'pesel': '70032816894', 'imie': 'Jan', 'drugie_imie': 'Stanisław', 'nazwisko': 'Zapał',
               'kod_pocztowy': '01-105', 'miasto': 'Warszawa', 'plec': 'M',
               'data_urodzenia': '19880420',
               'numer_ulicy': '49b', 'numer_lokalu': '153', 'ulica': 'Sowińskiego'}
    leki = [{'nazwa': 'Aspiryna', 'kategoria': 'OTC', 'ean': '05909990760619', 'tekst': 'Aspiryna',
             'refundacja_kod': '100%', 'refundacja_tekst': '100%', 'external_id': '100083164',
             'postac': 'tabletka', 'wielkosc': 10,
             'numer_recepty': str(uuid.uuid1()).replace('-', '')[0:22]},
            # {'nazwa': 'Aspiryna2', 'kategoria': 'OTC', 'ean': '05909990760619', 'tekst': 'Aspiryna 2',
            #  'refundacja_kod': '100%', 'refundacja_tekst': '100%', 'external_id': '100083164',
            #  'postac': 'tabletka', 'wielkosc': 10, 'numer_recepty': str(uuid.uuid1()).replace('-', '')[0:22]}
            ]
    recepta = {'oddzial_nfz': '07', 'uprawnienia_dodatkowe': 'x', 'data_wystawienia': today,
               'kluczPakietu': '11010203040506070809101112131415161718192011', 'kodPakietu': '0987'}
    podmiot = {'id_lokalne': settings.idPodmiotuLokalne, 'id': settings.idPodmiotuOidExt,
               'id_root': settings.idPodmiotuOidRoot, 'miasto': 'Warszawa', 'numer_domu': '12',
               'regon14': '97619191000009', 'ulica': 'Waryńskiego'}
    pracownik = {'id_ext': '5992363', 'imie': 'Jan', 'nazwisko': 'Kowalski', 'telefon': '504485575'}
    data = {'pracownik': pracownik, 'podmiot': podmiot, 'leki': leki, 'recepta': recepta, 'pacjent': pacjent}

    return data


def test_sending_prescription():
    c = create_client()
    data = get_prescription_data()
    status, response = c.save_prescriptions(data)
    assert status


def test_sending_recepture_prescription():
    c = create_client()
    data = get_prescription_data()
    data['leki'] = [{'nazwa': 'Syrop z cebuli', 'jest_recepturowy': True, 'refundacja_tekst': '50%',
                     'jest_refundowany': True, 'ilosc': '100g', 'receptura': 'Wycisnąć cebulę',
                     'refundacja_kod': '50%', 'numer_recepty': str(uuid.uuid1()).replace('-', '')[0:22]}]
    status, response = c.save_prescriptions(data)
    print(response)
    assert status


def test_cancelling_prescription():
    c = create_client()
    data = get_prescription_data()
    number = data['leki'][0]['numer_recepty']
    status, response = c.save_prescriptions(data)
    assert status
    external_id = \
    response['potwierdzenieOperacjiZapisu']['wynikZapisuPakietuRecept']['wynikWeryfikacji']['weryfikowanaRecepta'][0][
        'kluczRecepty']
    # external_id = response['potwierdzenieOperacjiZapisu']['wynikZapisuPakietuRecept']['kluczPakietuRecept']
    data = {'pacjent': {'imie': 'Jan', 'nazwisko': 'Zapała', 'plec': 'M', 'data_urodzenia': '', 'miasto': 'Warszawa',
                        'kod_pocztowy': '02-933', 'ulica': 'Okrężna', 'numer_ulicy': '87', 'numer_lokalu': '12',
                        'drugie_imie': 'Stan', 'data_urodzenia': '19880101'},
            "numer_anulowania": str(uuid.uuid1()).replace('-', '')[0:22],
            'profile': {'id': 1, 'user': 1, 'rola_biznesowa': 'LEKARZ_LEK_DENTYSTA_FELCZER',
                        'certificate_tls': '/media/certs/Podmiot_leczniczy_158-TLS.p12',
                        'certificate_tls_password': 'VfkxFEnqyt',
                        'certificate_wsse': '/media/certs/Podmiot_leczniczy_158-WSS.p12',
                        'certificate_wsse_password': 'VfkxFEnqyt',
                        'certificate_user': '/media/certs/Adam158_Leczniczy.p12',
                        'certificate_user_password': 'VfkxFEnqyt', 'id_podmiotu_oid_ext': '000000926670',
                        'id_podmiotu_lokalne': '2.16.840.1.113883.3.4424.2.7.293', 'id_miejsca_pracy_oid_ext': '4',
                        'id_pracownika_oid_ext': '1111113'},
            'podmiot': {'id_lokalne': settings.idPodmiotuLokalne, 'id': settings.idPodmiotuOidExt,
                        'id_root': settings.idPodmiotuOidRoot, 'miasto': 'Warszawa', 'numer_domu': '12',
                        'regon14': '97619191000009', 'ulica': 'Waryńskiego'},
            'lekarz': {'imie': 'Jan', 'nazwisko': 'Zapałł'},
            'recepta': {'data_wystawienia': '20191204', 'wersja': 1, 'root': '2.16.840.1.113883.3.4424.2.7.293.2.1',
                        'numer': number, 'external_id': external_id}
            }
    # tests
    data['podmiot']['regon14'] = '97619191000009'
    data['pacjent']['pesel'] = '70032816894'
    data['profile']['id_pracownika_oid_ext'] = '5992363'
    status, response = c.cancel_prescription(data)
    print(response)
    assert status


def test_printing_prescription():
    c = create_client()
    data = get_prescription_data()
    prescription = c.get_prescription_html(data)
    with open('t.html', 'wb') as f:
        f.write(prescription)
    assert '<html' in prescription.decode()
