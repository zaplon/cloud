# -*- coding: utf-8 -*-
import json
import math
from random import randint
from django.http import HttpResponse
from reportlab.lib import colors
from reportlab.graphics.barcode import createBarcodeDrawing
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph
from reportlab.lib.units import cm
from reportlab.lib.pagesizes import A5
from reportlab.lib.enums import TA_JUSTIFY, TA_CENTER
from reportlab.pdfgen import canvas
import datetime
import os
from django.conf import settings
import json
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from rest_framework.views import APIView

from g_utils.views import get_client_location_code
from medicine.models import Medicine, Prescription, MedicineToPrescription
from result.utils import save_document
from user_profile.models import PrescriptionNumber, Patient

pdfmetrics.registerFont(TTFont('Arial', 'Arial.ttf'))
pdfmetrics.registerFont(TTFont('Arialb', 'ArialBold.ttf'))


class RecipePrintException(Exception):
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return repr(self.value)


class PrintRecipe(APIView):
    queryset = Prescription.objects.all()

    def post(self, request):
        file_name = datetime.datetime.now().strftime("%s") + '.pdf'
        recipe_file = os.path.join(settings.MEDIA_ROOT, 'tmp', 'pdf', 'recipes', file_name)
        data = request.data
        if 'medicines' in data and len(data['medicines']) > 0:
            medicines = data.get('medicines', [])
        else:
            medicines = []
        patient = data.get('patient', {})
        patient_id = patient
        patient = Patient.objects.get(id=patient)
        realisation_date = data.get('realisationDate', "")
        system_settings = data['system_settings']
        c = canvas.Canvas(recipe_file, pagesize=(10 * cm, 29.7 * cm))
        for page in range(0, int(len(medicines) / 5) + 1):
            try:
                c = recipe_lines(c)
                c = recipe_es(c, patient, realisation_date)
                c = recipe_texts(request, c, request.user, system_settings)
                c = recipe_medicines(c, medicines)
                c.showPage()
            except RecipePrintException as e:
                return HttpResponse(json.dumps({'success': False, 'message': e.value}), content_type='application/json')

        c.save()
        save_document('Recepta', patient_id, recipe_file, request.user)
        return HttpResponse(json.dumps({'success': True, 'url': '/media/tmp/pdf/recipes/' + file_name}),
                            content_type='application/json')


def recipe_medicines(c, medicines):
    styles = getSampleStyleSheet()
    styles.add(ParagraphStyle(name='style', fontName='Arial', fontSize=7))
    c.setFont("Arialb", 9)
    offset = 1.65 * cm
    top = 21.5 * cm
    for m in medicines:

        txt = "%s %s %s" % (m['name'], m['dose'], m['dosage'])
        par = Paragraph(txt, styles['style'])
        par.wrapOn(c, 7.0 * cm, 3 * cm)
        par.drawOn(c, 0.5 * cm, top)

        par = Paragraph(m.get('refundations', [{'to_pay': '100%'}])[0]['to_pay'], styles['style'])
        par.wrapOn(c, 1.0 * cm, 3 * cm)
        par.drawOn(c, 8.5 * cm, top)

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

    if patient.pesel and patient.pesel[6:9] == '999':
        patient['pesel'] = ''

    doct_margin_left = 1
    doct_margin_top = 25
    tab1 = 0
    tab2 = 8
    ab = 29.7
    patient_margin_left = 0.3


    c.setFont("Arial", 9)
    styles = getSampleStyleSheet()
    styles.add(ParagraphStyle(name='PolishS', fontName='Arial', fontSize=9))
    styles.add(ParagraphStyle(name='address', fontName='Arial', fontSize=7))
    # informacje o pacjencie
    name = patient.__str__()
    c.drawString((patient_margin_left + tab1) * cm, (doct_margin_top) * cm, name.encode('utf-8'))
    if len(patient.address) > 0:
        # p.drawString((doct_margin_left+tab1)*cm, (doct_margin_top+pat-0.5)*cm, patient['address'].encode('utf-8'))
        par = Paragraph(patient.address.encode('utf-8'), styles['address'])
        par.wrapOn(c, 6.0 * cm, (2) * cm)
        par.drawOn(c, (patient_margin_left + tab1) * cm, (doct_margin_top - 0.8) * cm)
    # drukowany pesel

    pes = str(patient.pesel)
    weights = [1, 3, 7, 9, 1, 3, 7, 9, 1, 3, 7, 9, 1, 3, 7, 9, 1, 3, 7, 9, 1, 3, 7, 9, 1, 3, 7, 9]
    res = sum([int(pes[i]) * weights[i] for i in range(0, len(pes))]) % 10
    pes += str(res)

    if len(pes) > 8:
        b = createBarcodeDrawing('Code128', value=pes, width=5 * cm, height=0.5 * cm)

    c.drawString((patient_margin_left + 1.3) * cm, (doct_margin_top - 2.1) * cm,
                 patient.pesel.encode('utf-8'))
    if len(pes) > 8:
        b.drawOn(c, (patient_margin_left + 0.0) * cm, (doct_margin_top - 1.7) * cm)
    c.drawString((tab2 + doct_margin_left) * cm, (ab - 6.8) * cm, permissions.encode('utf-8'))

    c.drawString((tab2 + doct_margin_left) * cm, (ab - 5.0) * cm, nfz.encode('utf-8'))

    date = datetime.date.today().strftime('%d.%m.%Y')

    c.drawString((tab1 + 1 + doct_margin_left) * cm, (ab - 18.3 + doct_margin_top) * cm, date)
    c.drawString((tab1 + 1 + doct_margin_left) * cm, (ab - 18.3 - 1.8) * cm, realisation_date)

    return c


def recipe_texts(request, p, us, system_settings, doct_margin_left=0, doct_margin_top=0, recNr='0000000000'):
    useNr = int(request.data.get('number', False))
    p.setFont("Arial", 9)

    x = 0.25
    y = 29.2
    p.drawString((x + 0) * cm, (y - 0.4) * cm, 'Recepta')
    if useNr:
        recNr = PrescriptionNumber.objects.filter(date_used__isnull=True, doctor=request.user.doctor)
        if len(recNr) == 0:
            raise RecipePrintException('Brak numeru recepty do wykorzystania')
        recNr = recNr[0]
        recNr_instance = recNr
        p.drawString((x + 3) * cm, (y - 0.4) * cm, recNr.nr)
    p.setFont("Arialb", 8)

    for i, line in enumerate(system_settings['documents_header_left'].split('\n')):
        p.drawString((x + 0) * cm, (y - 0.9 - i*0.3) * cm, line)

    p.setFont("Arial", 9)

    b = createBarcodeDrawing('Code128', value="20%s0009" % system_settings['regon'], width=5 * cm, height=0.6 * cm)
    p.drawString((x + 6.7) * cm, (y - 3.1) * cm, "20%s0009" % system_settings['regon'])
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
        b = createBarcodeDrawing('Code128', value=str(recNr.nr), width=6 * cm, height=0.6 * cm)
        p.drawString((x + 2.7) * cm, (y - 16.4) * cm, str(recNr.nr))
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
    if useNr:
        recNr_instance.date_used = datetime.datetime.now()
        recNr_instance.save()
    return p


class PrintGlasses(APIView):
    queryset = Prescription.objects.all()

    def post(self, request):
        data = request.data
        Story = []
        code = randint(0, 10000)
        fileNm = settings.MEDIA_ROOT + "/tmp/" + str(code) + ".pdf"
        fileNm2 = "/media/tmp/" + str(code) + ".pdf"
        # doc = SimpleDocTemplate(fileNm,pagesize=A4,
        #                   rightMargin=15,leftMargin=15,
        #                   topMargin=15,bottomMargin=15)

        c = canvas.Canvas(fileNm, pagesize=A5)

        w = 14.8
        h = 21

        pdfmetrics.registerFont(TTFont('Arial', 'Arial.ttf'))
        styles = getSampleStyleSheet()
        styles.add(ParagraphStyle(name='JustifyBold', alignment=TA_JUSTIFY, fontName='Arial-Bold', fontSize=9))
        styles.add(ParagraphStyle(name='Heading', alignment=TA_CENTER, fontName='Arial'))
        styles.add(ParagraphStyle(name='HeadingBold', alignment=TA_CENTER, fontName='Arial-Bold', fontSize=14))
        styles.add(ParagraphStyle(name='Polish', fontName='Arial', fontSize=10, ))
        styles.add(ParagraphStyle(name='TH', alignment=TA_CENTER, fontName='Arial', fontSize=12))
        styles.add(ParagraphStyle(name='PolishC', alignment=TA_CENTER, fontName='Arial', fontSize=10))
        styles.add(ParagraphStyle(name='PolishS', fontName='Arial', fontSize=8))
        styleN = styles["Polish"]
        styleH = styles["TH"]
        styleNC = styles["PolishC"]
        dt = [('', '', 'SFERA', 'CYLINDER', Paragraph(u'<para align="center">OŚ</para>', styleN), 'PRYZMA'),
              (Paragraph('DO DALI', styleNC), 'O.P.', data['tabela1'][0], data['tabela1'][1],
               data['tabela1'][2], data['tabela1'][3]),
              ('', 'O.L.', data['tabela1'][4], data['tabela1'][5], data['tabela1'][6],
               data['tabela1'][7]),
              (Paragraph('DO BLIŻY', styleNC), 'O.P.', data['tabela1'][8], data['tabela1'][9],
               data['tabela1'][10], data['tabela1'][11]),
              ('', 'O.L.', data['tabela1'][12], data['tabela1'][13], data['tabela1'][14],
               data['tabela1'][15])]
        table1 = Table(dt, colWidths=[1.5 * cm, 1.5 * cm, 2.5 * cm, 2.5 * cm, 2.5 * cm, 2.5 * cm])
        table1.setStyle(TableStyle([('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                                    ('GRID', (0, 0), (-1, -1), 0.25, colors.black),
                                    ('SPAN', (0, 1), (0, 2)), ('SPAN', (0, 3), (0, 4))
                                    ]))
        # Story.append(table)

        dt = [(Paragraph('MIEJSCE DLA WYCENY [ZŁ]', styleH), ''), (Paragraph('Oprawa', styleN), data['tabela2'][0]),
              (Paragraph('Cena oprawy odliczona od droższej oprawy', styleN), data['tabela2'][1]),
              (Paragraph('Prawe szkło', styleN), data['tabela2'][2]),
              (Paragraph('Lewe szkło', styleN), data['tabela2'][3]),
              (Paragraph('Futerał', styleN), data['tabela2'][4]),
              (Paragraph('Suma', styleN), data['tabela2'][5]),
              (Paragraph('Usługa', styleN), data['tabela2'][6]),
              (Paragraph('Razem', styleN), data['tabela2'][7])
              ]
        table2 = Table(dt)
        table2.setStyle(TableStyle([('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                                    ('GRID', (0, 0), (-1, -1), 0.25, colors.black),
                                    ('SPAN', (0, 0), (1, 0))
                                    ]))

        glasses = settings.BASE_DIR + '/static/images/okulary.png'
        p = Paragraph('Nazwisko pacjenta:  ' + data['name'], styleN)
        p.wrapOn(c, 10 * cm, (2) * cm)
        p.drawOn(c, (1) * cm, (h - 2) * cm)

        # drawing = svg2rlg(glasses)
        # drawing.drawOn(c,1*cm,(h-6.29/2-3.5)*cm)

        c.drawImage(glasses, 1 * cm, (h - 2.66 * 3 / 2 - 2.5) * cm, 7.44 * 3 / 2 * cm, 2.66 * 3 / 2 * cm)

        table1.wrapOn(c, 8 * cm, 3 * cm)
        table1.drawOn(c, 1 * cm, (h - 10) * cm)

        c.setFont("Arial", 10)

        p = Paragraph('SZKŁA', styleN)
        p.wrapOn(c, 4 * cm, (2) * cm)
        p.drawOn(c, (1) * cm, (h - 11) * cm)
        c.drawString(2.5 * cm, (h - 10.94) * cm, data['tabela1'][16])

        c.drawString(5 * cm, (h - 11) * cm, 'OPRAWA  ' + data['tabela1'][17])
        c.drawString(1 * cm, (h - 12) * cm, 'Data i podpis lekarza  _________________')

        # p = Paragraph('Odl. zrenic.'+data['tabela1'][0][''], styleN)
        # p.wrapOn(c, 4*cm, (2)*cm)
        # p.drawOn(c,(9)*cm,(h-11)*cm)

        # p = Paragraph('Odl. zrenic.'+data['tabela1'][2][''], styleN)
        # p.wrapOn(c, 4*cm, (2)*cm)
        # p.drawOn(c,(11)*cm,(h-11)*cm)

        table2.wrapOn(c, 7 * cm, 6 * cm)
        table2.drawOn(c, (7) * cm, (h - 20) * cm)

        p = Paragraph('Pieczątka Wydziału Zdrowia zatwierdzającego receptę', styles['PolishS'])
        p.wrapOn(c, 5 * cm, (2) * cm)
        p.drawOn(c, (1) * cm, (h - 17) * cm)

        p = Paragraph('Pieczątka z adresami sklepów', styles['PolishS'])
        p.wrapOn(c, 6 * cm, (2) * cm)
        p.drawOn(c, (1) * cm, (h - 20) * cm)

        # c.drawString(2*cm,(h-14)*cm,('Pieczątka z adresami sklepów').encode('utf-8'))

        # pozycja srodka okularow
        px = 3.55
        lx = px + 6
        py = ly = h - 5
        r = 1.5
        ra = data['op']
        la = data['ol']
        if la >= 0:
            c.line(lx * cm, ly * cm, (lx + r * math.cos(math.radians(la + 5))) * cm,
                   (ly + r * math.sin(math.radians(la + 5))) * cm)
            c.line(px * cm, py * cm, (px + r * math.cos(math.radians(ra + 5))) * cm,
                   (py + r * math.sin(math.radians(ra + 5))) * cm)

        c.save()

        save_document('Recepta okulistyczna', data['patientId'], fileNm, request.user)

        # return response
        return HttpResponse(fileNm2)
