# -*- coding: utf-8 -*-
import json

from django.http import HttpResponse
from reportlab.graphics.barcode import createBarcodeDrawing
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.pdfgen import canvas
import datetime
import os
from django.conf import settings
import json
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import Paragraph

from g_utils.views import get_client_location_code

pdfmetrics.registerFont(TTFont('Arial', 'Arial.ttf'))
pdfmetrics.registerFont(TTFont('Arialb', 'ArialBold.ttf'))


def print_recipe(request):
    file_name = datetime.datetime.now().strftime("%s") + '.pdf'
    recipe_file = os.path.join(settings.MEDIA_ROOT, 'tmp', 'pdf', 'recipes', file_name)
    if 'medicines' in request.POST and len(request.POST['medicines']) > 0:
        medicines = json.loads(request.POST.get('medicines', "[]"))
    else:
        medicines = []
    patient = json.loads(request.POST.get('patient', "{}"))
    realisation_date = request.POST.get('realisationDate', "")
    realisation_date = datetime.datetime.strptime(realisation_date, '%Y-%m-%d').strftime('%d.%m.%Y')
    c = canvas.Canvas(recipe_file, pagesize=(10 * cm, 29.7 * cm))
    for page in range(0, int(len(medicines)/5)+1):
        c = recipe_lines(c)
        c = recipe_es(c, patient, realisation_date)
        c = recipe_texts(request, c, request.user)
        c = recipe_medicines(c, medicines)
        c.showPage()
    c.save()
    return HttpResponse(json.dumps({'url': '/media/tmp/pdf/recipes/' + file_name}), content_type='application/json')


def recipe_medicines(c, medicines):
    styles = getSampleStyleSheet()
    styles.add(ParagraphStyle(name='style', fontName='Arial', fontSize=7))
    c.setFont("Arialb", 9)
    offset = 1.65*cm
    top = 21.5*cm
    for m in medicines:
        txt = "%s %s %s" % (m['selection']['name'], m['dose'], m['dosage'])
        par = Paragraph(txt, styles['style'])
        par.wrapOn(c, 7.0 * cm, 3 * cm)
        par.drawOn(c, 0.5*cm, top)
        top -= offset
    return c


def recipe_lines(c, tab1=0.3):
    # przesuniecie - 0.45
    offset = 1.6
    x = tab1
    width = 9.5
    start = 7.65
    ph = 29.7

    c.line(x * cm, (ph - 7) * cm, (x + width) * cm, (ph - 7) * cm)
    c.line(x * cm, (ph - 3.75) * cm, (x + width) * cm, (ph - 3.75) * cm)
    c.line(8.0 * cm, (ph - 3.75) * cm, 8.0 * cm, (ph - 7) * cm)
    c.line(8.0 * cm, (ph - 5.5) * cm, (x + width) * cm, (ph - 5.5) * cm)
    c.line(tab1 * cm, (ph - 18.7) * cm, (tab1 + 4.5) * cm, (ph - 18.7) * cm)
    c.line(tab1 * cm, (ph - 17.2) * cm, (tab1 + width) * cm, (ph - 17.2) * cm)
    c.line((tab1 + 4.5) * cm, (ph - 17.2) * cm, (tab1 + 4.5) * cm, (ph - 20.5) * cm)
    # c.rect(tab1*cm, 0.5*cm, width*cm, 20*cm)
    # c.rect(tab1*cm, (ph-19)*cm, 5*cm, 1.5*cm)
    # c.rect(tab1*cm, (ph-20.5)*cm, 5*cm, 1.5*cm)
    # c.rect((tab1+5)*cm, (ph-20.5)*cm, 5*cm, 3*cm)

    c.setDash(4, 2)
    c.setStrokeColor((0.5, 0.5, 0.5))
    c.line(8.0 * cm, (ph - 7.1) * cm, 8.0 * cm, (ph - 15.5) * cm)
    for i in range(0, 6):
        c.line(x * cm, (ph - start - i * offset) * cm, (x + width) * cm, (ph - start - i * offset) * cm)
    return c


def recipe_es(c, patient, realisation_date, permissions='X', nfz='7'):

    if 'pesel' not in patient or not patient['pesel']:
        patient['pesel'] = ''

    if patient['pesel'][6:9] == '999':
        patient['pesel'] = ''

    doct_margin_left = 1
    doct_margin_top = 25
    tab1 = 0
    tab2 = 8
    ab = 29.7
    patient_margin_left = 0.3

    patient['address'] = 'ul. Okrezna 87 02-033 warszawa'
    patient['pesel'] = '88042003997'

    c.setFont("Arial", 9)
    styles = getSampleStyleSheet()
    styles.add(ParagraphStyle(name='PolishS', fontName='Arial', fontSize=9))
    styles.add(ParagraphStyle(name='address', fontName='Arial', fontSize=7))
    # informacje o pacjencie
    name = patient['first_name'] + ' ' + patient['last_name']
    c.drawString((patient_margin_left + tab1) * cm, (doct_margin_top) * cm, name.encode('utf-8'))
    if 'address' in patient and patient['address'] and len(patient['address']) > 0:
        # p.drawString((doct_margin_left+tab1)*cm, (doct_margin_top+pat-0.5)*cm, patient['address'].encode('utf-8'))
        par = Paragraph(patient['address'].encode('utf-8'), styles['address'])
        par.wrapOn(c, 6.0 * cm, (2) * cm)
        par.drawOn(c, (patient_margin_left + tab1) * cm, (doct_margin_top - 0.8) * cm)
    # drukowany pesel

    pes = str(patient['pesel'])
    weights = [1, 3, 7, 9, 1, 3, 7, 9, 1, 3, 7, 9, 1, 3, 7, 9, 1, 3, 7, 9, 1, 3, 7, 9, 1, 3, 7, 9]
    res = sum([int(pes[i]) * weights[i] for i in range(0, len(pes))]) % 10
    pes += str(res)

    if len(pes) > 8:
        b = createBarcodeDrawing('Code128', value=pes, width=5 * cm, height=0.5 * cm)

    c.drawString((patient_margin_left + 1.3) * cm, (doct_margin_top - 2.1) * cm,
                 patient['pesel'].encode('utf-8'))
    if len(pes) > 8:
        b.drawOn(c, (patient_margin_left + 0.0) * cm, (doct_margin_top - 1.7) * cm)
    c.drawString((tab2 + doct_margin_left) * cm, (ab - 6.8) * cm, permissions.encode('utf-8'))

    c.drawString((tab2 + doct_margin_left) * cm, (ab - 5.0) * cm, nfz.encode('utf-8'))

    date = datetime.date.today().strftime('%d.%m.%Y')

    c.drawString((tab1 + 1 + doct_margin_left) * cm, (ab - 18.3 + doct_margin_top) * cm, date)
    c.drawString((tab1 + 1 + doct_margin_left) * cm, (ab - 18.3 - 1.8) * cm, realisation_date)

    return c


def recipe_texts(request, p, us, doct_margin_left=0, doct_margin_top=0, recNr='0000000000'):
    useNr = False
    p.setFont("Arial", 9)

    x = 0.25
    y = 29.2
    p.drawString((x + 0) * cm, (y - 0.4) * cm, 'Recepta')
    if useNr and recNr:
        p.drawString((x + 3) * cm, (y - 0.4) * cm, recNr)
    p.setFont("Arialb", 8)
    code = get_client_location_code(request)
    if code == 'KEN':
        p.drawString((x + 0) * cm, (y - 0.9) * cm, 'FILIA NR 2 PRZEDSIĘBIORSTWA PODMIOTU LECZNICZEGO')
        p.drawString((x + 0) * cm, (y - 1.2) * cm, 'SPÓŁDZIELNIA PRACY SPECJALISTÓW RENTGENOLOGÓW')
        p.drawString((x + 0) * cm, (y - 1.5) * cm, '02-797 WARSZAWA')
        p.drawString((x + 0) * cm, (y - 1.8) * cm, 'AL. KEN 19')
        p.drawString((x + 0) * cm, (y - 2.1) * cm, 'Tel.:224467777')
        p.drawString((x + 0) * cm, (y - 2.4) * cm, 'REGON:000840941')
    elif code == 'PDT':
        p.drawString((x + 0) * cm, (y - 0.9) * cm, 'FILIA NR 3 PRZEDSIĘBIORSTWA PODMIOTU LECZNICZEGO')
        p.drawString((x + 0) * cm, (y - 1.2) * cm, 'SPÓŁDZIELNIA PRACY SPECJALISTÓW RENTGENOLOGÓW')
        p.drawString((x + 0) * cm, (y - 1.5) * cm, '01-194 WARSZAWA')
        p.drawString((x + 0) * cm, (y - 1.8) * cm, 'MŁYNARSKA 8/12')
        p.drawString((x + 0) * cm, (y - 2.1) * cm, 'Tel.:226327705')
        p.drawString((x + 0) * cm, (y - 2.4) * cm, 'REGON:000840941')
    else:
        p.drawString((x + 0) * cm, (y - 0.9) * cm, 'FILIA NR 1 PRZEDSIĘBIORSTWA PODMIOTU LECZNICZEGO')
        p.drawString((x + 0) * cm, (y - 1.2) * cm, 'SPÓŁDZIELNIA PRACY SPECJALISTÓW RENTGENOLOGÓW')
        p.drawString((x + 0) * cm, (y - 1.5) * cm, '00-655 WARSZAWA')
        p.drawString((x + 0) * cm, (y - 1.8) * cm, 'WARYŃSKIEGO 9')
        p.drawString((x + 0) * cm, (y - 2.1) * cm, 'Tel.:226251590')
        p.drawString((x + 0) * cm, (y - 2.4) * cm, 'REGON:000840941')

    p.setFont("Arial", 9)

    b = createBarcodeDrawing('Code128', value="20008409410000", width=5 * cm, height=0.6 * cm)
    p.drawString((x + 6.7) * cm, (y - 3.1) * cm, "20008409410000")
    b.drawOn(p, (x + 5.4) * cm, (y - 2.75) * cm)

    p.drawString((x + 0) * cm, (y - 3.15) * cm, 'Świadczeniodawca')
    p.drawString((x + 0) * cm, (y - 3.7) * cm, 'Pacjent')
    p.drawString((x + 7.82) * cm, (y - 3.7) * cm, 'Oddział NFZ')
    p.drawString((x + 7.82) * cm, (y - 5.45) * cm, 'Uprawnienia')
    p.drawString((x + 7.82) * cm, (y - 5.75) * cm, 'dodatkowe')
    p.drawString((x + 0) * cm, (y - 6.35) * cm, 'PESEL')
    p.drawString((x + 0) * cm, (y - 7.0) * cm, 'Rp')
    p.drawString((x + 7.82) * cm, (y - 7.0) * cm, 'Odpłatność')
    p.drawString((x + 0.0) * cm, (y - 17.0) * cm, 'Data wystawienia:')
    p.drawString((x + 4.6) * cm, (y - 17.0) * cm, 'Dane i podpis lekarza')
    p.drawString((x + 0) * cm, (y - 18.6) * cm, 'Data realizacji "od dnia":')
    # p.drawString((x+5.4)*cm,(y-20.0)*cm, 'KOD')

    p.drawString((x + 4.6) * cm, (y - 19.8) * cm, 'Wydruk własny')
    if useNr:
        b = createBarcodeDrawing('Code128', value=str(recNr), width=6 * cm, height=0.6 * cm)
        p.drawString((x + 2.7) * cm, (y - 16.4) * cm, str(recNr))
        b.drawOn(p, (x + 1.6) * cm, (y - 16.05) * cm)

    styles = getSampleStyleSheet()
    styles.add(ParagraphStyle(name='PolishS', fontName='Arial', fontSize=9))
    par = Paragraph(us.first_name + ' ' + us.last_name, styles['PolishS'])
    w, h = par.wrapOn(p, 4.5 * cm, (5) * cm)
    par.drawOn(p, (5.0) * cm, (y - 17.3) * cm - h)
    b = createBarcodeDrawing('Code128', value=str('30' + us.doctor.pwz + '7'), width=5 * cm, height=0.6 * cm)
    p.drawString((x + 5.5) * cm, (y - 18.4) * cm - h, str(us.doctor.pwz))
    b.drawOn(p, (x + 3.9) * cm, (y - 18.1) * cm - h)

    # p.drawString((x+5.5)*cm,(y-17.8)*cm, title)
    # p.drawString((x+5.5)*cm,(y-18.3)*cm, us.name)

    return p