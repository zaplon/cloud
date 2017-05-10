# -*- coding: utf-8 -*-
from suds.client import Client
import logging
import suds
import base64
import traceback
from django.http import HttpResponse
import json, os, time, math, datetime
from gabinet import settings
from django.conf import settings
from xml.etree.ElementTree import Element, SubElement, tostring
import codecs, zipfile
from operator import itemgetter
from user_profile.models import Patient

url = 'https://10.200.0.4/elo_webservice/EloWS.asmx?WSDL'
url2 = 'https://10.200.0.4/elo_webservice/EloWS.asmx?WSDL'
usr = 'GabImport'
psw = 'ub3Ese4TQLHz'
system = 'Gabinet'


def isAnal(request):
    usernames = ['panaw', 'panak', 'panap', 'PANAW', 'PANAK', 'PANAP']
    if request.user.username in usernames:
        return True
    else:
        return False


def uploadToElo(zipfile='/home/gabinet/app/media/tmp/elo.zip',
                metafile='/home/gabinet/app/media/tmp/meta.xml', ex=None, save=False):
    try:
        logging.basicConfig(level=logging.INFO)
        logging.getLogger('suds.client').setLevel(logging.CRITICAL)
        zipfile_enc = base64.b64encode(open(zipfile, 'rb').read())
        metafile_enc = base64.b64encode(open(metafile, 'rb').read())
        client = Client(url, faults=True)
        msg = client.service['EloWSSoap'].AddNewDoc(usr, psw, system, zipfile_enc, metafile_enc)
        if msg is True:
            if save:
                ex.in_elo = True
                ex.dont_send_to_elo = False
                ex.save()
            #print ex.patient.pesel
            print 'ELO Received Data!'
            return True
        else:
            if save:
                ex.in_elo = False
                ex.save()
            print 'ELO Returned ERROR!'
            return False
    except suds.WebFault as detail:
        #print unicode(detail)
        return False
    except Exception as exc:
        #print unicode(traceback.format_exc())
        return False


def getPatient(pesel, request):
    # flaga czy jest to sztuczny pesel
    notPesel = False
    if pesel[6:9] == '999':
        notPesel = True
        try:
            patientName = Patient.objects.filter(pesel=pesel)[0].last_name.strip().upper()
        except:
            pass
        pesel = pesel[0:6]
    else:
        pesel = pesel
    try:
        client = Client(url2, faults=True, timeout=150)
    except:
        return False
    try:
        res = client.service['EloWSSoap'].getPatientsList(usr, psw, pesel)
    except:
        return False
    # ex = Examination.objects.get(doctor=request.user.doctor, ongoing=True)
    #patientName = ex.patient.last_name
    try:
        if notPesel:
            for p in res[0]:
                if p['nazwiskoImie'].strip() == patientName:
                    return [p, client]
                else:
                    return [res, client]
        else:
            return [res[0], client]
    except:
        return False


def getPatientData(pesel, request, fromDate=None):
    res = getPatient(pesel, request)
    if not res:
        ls = []
        if len(ls) == 0:
            return HttpResponse(json.dumps({'text': 'Brak pacjenta w archiwum'}))
        else:
            ls = sorted(ls, key=itemgetter('text'), reverse=False)
            return HttpResponse(json.dumps(ls), content_type="application/json")
    pat = res[0]
    try:
        if len(pat[0][0][0]) > 1:
            pat = pat[0]
    except:
        pass
    peselID = ''
    name = ''
    client = res[1]
    res = []
    ls = []
    keys = {}
    npat = []
    pesels = []
    for p in pat:
        peselID = p[1]
        if p[0]:
            name = p[0].encode('utf8')
        else:
            name = 'Brak nazwiska'
        if peselID in pesels:
            continue
        pesels.append(peselID)
        npat.append([peselID, name])

    if len(npat) > 1:
        patients = []
        many = True
    else:
        many = False
    for p in npat:
        name = p[1]
        docs = client.service['EloWSSoap'].getDocList(usr, psw, p[0])
        if len(docs[0]) > 0:
            for d in docs[0]:

                if d['typZlecenia']:
                    d['typZlecenia'] = d['typZlecenia'].upper()

                #ograniczenie dla RTG
                if request.user.username in ['rtg','RTG'] and d['typZlecenia'] not in ['RTG', 'rtg','R','r']:
                    continue

                # ograniczenia dla analityki
                if d['typZlecenia'] in ['ANALITYKA', 'ANALITYCZNE']:
                    d['typZlecenia'] = 'ANALITYKA'
                if isAnal(request) and d['typZlecenia'] not in ['ANALITYKA']:
                    try:
                        if d['typZlecenia'].find('ANALITYKA') == -1:
                            continue
                    except:
                        continue
                if d['typZlecenia'] == 'KARDI':
                    d['typZlecenia'] = 'KARDIOLOG'

                if d['typZlecenia'] == 'GASTROSKOPIA':
                    d['typZlecenia'] = 'GASTROLOG'


                date = d['dataBadania']
                if not date:
                    date = 'Brak informacji o dacie'

                node = {'text': d['dataBadania'], 'id': str(d['docID']), 'name': d['badaniaNazwy']}
                if d['typZlecenia'] in keys:
                    test = True
                    if len(ls[keys[d['typZlecenia']]]['children']) > 1:
                        for k in ls[keys[d['typZlecenia']]]['children']:
                            pass
                            # if k['text'] == node['text']:
                            #    test = False
                    if test:
                        rs = filter(lambda child: child['text'] == d['dataBadania'],
                                    ls[keys[d['typZlecenia']]]['children'])
                        if len(rs) < 10 or isAnal(request):
                            ls[keys[d['typZlecenia']]]['children'].append(node)
                else:
                    keys[d['typZlecenia']] = len(keys)
                    ls.append({'text': d['typZlecenia'], "isFolder": True, 'children': [node]})
        if many:
            patients.append({'text': name, "isFolder": True, 'children': ls})
            ls = []
            keys = {}
    if many:
        if len(patients) > 0:
            patients = sorted(patients, key=itemgetter('text'), reverse=False)
            return HttpResponse(json.dumps(patients), content_type="application/json")
        else:
            return HttpResponse(json.dumps({'text': 'Brak wyników'}), content_type="application/json")

    if len(ls) > 0:
        ls = sorted(ls, key=itemgetter('text'), reverse=False)
        return HttpResponse(json.dumps(ls), content_type="application/json")
    else:
        return HttpResponse(json.dumps({'text': 'Brak wyników'}), content_type="application/json")


if __name__ == "__main__":
    uploadToElo()


def sortEls(el):
    return el['text']


def getDoc(request, id):
    client = Client(url2, faults=True)
    res = client.service['EloWSSoap'].getDoc(usr, psw, id)
    data = res['plik']
    roz = res['typPliku']
    dt = int(time.time())
    name = settings.MEDIA_ROOT + '/tmp/' + str(dt) + roz
    name2 = '/media/tmp/' + str(dt) + roz
    # zapisujemy do pliku tymczasowego
    f = open(name, 'wb')
    f.write(base64.decodestring(res['plik']))
    f.close()

    return HttpResponse(name2)


def makeFiles(ex, type, pdf, xml='meta.xml', place='SPSR-WAR'):
    # meta xml
    root = Element('przesylka')
    pacjent = SubElement(root, "pacjent")
    child2 = SubElement(pacjent, "nazwisko")
    child2.text = ex.patient.last_name
    child2 = SubElement(pacjent, "pesel")
    child2.text = ex.patient.pesel
    child2 = SubElement(pacjent, "adres")
    child2.text = ex.patient.address
    badania = SubElement(root, "badania")
    badanie = SubElement(badania, "badanie")
    icds10 = ex.icd10.all()
    for b in icds10:
        icd10 = b.code
        icd = SubElement(badanie, "icd")
        icd.text = icd10
    lekarze = SubElement(badania, "lekarze")
    lekarz = SubElement(lekarze, "lekarz")
    lekarz.text = ex.doctor.user.name
    kod = SubElement(badanie, "kod")
    kod.text = ex.doctor.user.username
    nazwa = SubElement(badanie, "nazwa")
    nazwa.text = type
    child2 = SubElement(badanie, "lokalizacja")
    child2.text = place

    zlecenie = SubElement(root, "zlecenie")
    child2 = SubElement(zlecenie, "data")
    child2.text = ex.date.strftime("%Y-%m-%d")
    child2 = SubElement(zlecenie, "godzina")
    child2.text = ex.date.strftime("%H:%M")
    child2 = SubElement(zlecenie, "numerzewnetrzny")
    child2.text = ex.misal_id
    child2 = SubElement(zlecenie, "typzlecenia")
    if ex.clinic:
        child2.text = ex.clinic.nice_name
    else:
        try:
            child2.text = ex.doctor.specialization.all()[0].code_misal
        except:
            child2.text = None
            if child2.text == None:
                child2.text = getSpecFromName(ex)

    platnik = SubElement(root, 'platnik')
    symbol = SubElement(platnik, 'symbol')
    symbol.text = ex.institution
    nazwa = SubElement(platnik, 'nazwa')
    nazwa.text = ex.institution

    zleceniodawca = SubElement(root, "zleceniodawca")

    f = codecs.open(xml, "w+")
    try:
        f.write(tostring(root, encoding='utf-8'))  # Write a string to a file
    finally:
        f.close()

    #tworzenie zip
    compression = zipfile.ZIP_DEFLATED
    zf = zipfile.ZipFile(settings.MEDIA_ROOT+'elo.zip', mode='w')
    #zf.write(xml, arcname='elo.xml', compress_type=compression)
    #zf.write("/home/gabinet/trunk/django_project/portal/static/tmp/meta.xml", arcname='meta.xml', compress_type=compression)
    zf.write(pdf, arcname='elo.pdf', compress_type=compression)
    zf.close()
    return uploadToElo(settings.MEDIA_ROOT+'elo.zip', xml)


def getSpecFromName(ex):
    if ex.doctor.user.username.find('LK') > -1:
        nazwa = "Kardiolog"
    elif ex.doctor.user.username.find('OO') > -1:
        nazwa = 'Okulista'
    elif ex.doctor.user.username.find('LO') > -1:
        nazwa = 'Ortopeda'
    elif ex.doctor.user.username.find('LI') > -1:
        nazwa = 'Internista'
    elif ex.doctor.user.username.find('LD') > -1:
        nazwa = 'Dermatolog'
    else:
        nazwa = 'Wizyta'
        
        


def metaElo(ex, code, dst=None):
    #elo.xml
    #root = Element('visit')
    #f = codecs.open(STATIC_ROOT + "portal/tmp/elo.xml", "w+")
    #try:
    #    f.write(tostring(root,encoding='utf-8')) # Write a string to a file
    #finally:
    #    f.close()

    root = Element('przesylka')
    pacjent = SubElement(root, "pacjent")
    child2 = SubElement(pacjent, "nazwisko")
    child2.text = ex.patient.last_name
    child2 = SubElement(pacjent, "pesel")
    child2.text = ex.patient.pesel
    child2 = SubElement(pacjent, "adres")
    child2.text = ex.patient.address
    badania = SubElement(root, "badania")
    badanie = SubElement(badania, "badanie")
    icds10 = ex.icd10.all()
    for b in icds10:
        icd10 = b.code
        icd = SubElement(badanie, "icd")
        icd.text = icd10
    lekarze = SubElement(badania, "lekarze")
    lekarz = SubElement(lekarze, "lekarz")
    lekarz.text = ex.doctor.user.name
    kod = SubElement(badanie, "kod")
    kod.text = ex.doctor.user.username
    nazwa = SubElement(badanie, "nazwa")
    # try:
    #     nazwa.text = ex.doctor.specialization.all()[0].name
    # except:
    #     nazwa.text = ex.user.getSpecFromName()
    nazwa.text = code
    child2 = SubElement(badanie, "lokalizacja")
    child2.text = 'SPSR-WAR'

    zlecenie = SubElement(root, "zlecenie")
    child2 = SubElement(zlecenie, "data")
    child2.text = ex.date.strftime("%Y-%m-%d")
    child2 = SubElement(zlecenie, "godzina")
    child2.text = ex.date.strftime("%H:%M")
    child2 = SubElement(zlecenie, "numerzewnetrzny")
    child2.text = ex.misal_id
    child2 = SubElement(zlecenie, "typzlecenia")
    # try:
    #     child2.text = ex.doctor.specialization.all()[0].code_misal
    # except:
    #     child2.text = ex.user.getSpecFromName()
    child2.text = code

    zleceniodawca = SubElement(root, "zleceniodawca")
    zleceniodawca.text = ex.institution

    if dst:
        f = codecs.open(dst, "w+")
    else:
        f = codecs.open(settings.MEDIA_ROOT + "tmp/meta.xml", "w+")
    try:
        f.write(tostring(root, encoding='utf-8'))  # Write a string to a file
    finally:
        f.close()
