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

from reportlab.platypus import Paragraph


def print_recipe(request):
    file_name = datetime.datetime.now().strftime("%s") + '.pdf'
    recipe_file = os.path.join(settings.MEDIA_ROOT, 'tmp', 'pdf', 'recipes', file_name)
    medicines = json.loads(request.POST.get('medicines', "[]"))
    patient = json.loads(request.POST.get('patient', "{}"))
    realisation_date = request.POST.get('realisation_date', "")
    c = canvas.Canvas(recipe_file, pagesize=(10 * cm, 29.7 * cm))
    c = recipe_lines(c)
    c = recipe_es(c, patient, realisation_date)
    c.save()
    return HttpResponse(json.dumps({'url': '/media/tmp/pdf/recipes/' + file_name}), content_type='application/json')


def recipe_lines(c, tab1=0):
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

    if patient['pesel'][6:9] == '999':
        patient['pesel'] = ''

    doct_margin_left=0
    doct_margin_top=0
    tab1 = 0
    tab2 = 0
    ab = 29.7

    c.setFont("Arial", 9)
    styles = getSampleStyleSheet()
    styles.add(ParagraphStyle(name='PolishS', fontName='Arial', fontSize=9))
    styles.add(ParagraphStyle(name='address', fontName='Arial', fontSize=7))
    # informacje o pacjencie
    c.drawString((doct_margin_left + tab1) * cm, (doct_margin_top) * cm, patient['name'].encode('utf-8'))
    if len(patient['address']) > 0:
        # p.drawString((doct_margin_left+tab1)*cm, (doct_margin_top+pat-0.5)*cm, patient['address'].encode('utf-8'))
        par = Paragraph(patient['address'].encode('utf-8'), styles['address'])
        par.wrapOn(p, 6.0 * cm, (2) * cm)
        par.drawOn(p, (doct_margin_left + tab1) * cm, (doct_margin_top - 1) * cm)
    # drukowany pesel

    pes = str(patient['pesel'])
    weights = [1, 3, 7, 9, 1, 3, 7, 9, 1, 3, 7, 9, 1, 3, 7, 9, 1, 3, 7, 9, 1, 3, 7, 9, 1, 3, 7, 9]
    res = sum([int(pes[i]) * weights[i] for i in range(0, len(pes))]) % 10
    pes += str(res)

    if len(pes) > 8:
        b = createBarcodeDrawing('Code128', value=pes, width=5 * cm, height=0.5 * cm)

    c.drawString((doct_margin_left + 1.5) * cm, (doct_margin_top - 2.1) * cm,
                 patient['pesel'].encode('utf-8'))
    if len(pes) > 8:
        b.drawOn(c, (doct_margin_left + 0.0) * cm, (doct_margin_top - 1.7) * cm)
    c.drawString((tab2 + doct_margin_left) * cm, (ab - 6.8 + doct_margin_top) * cm, permissions.encode('utf-8'))

    c.drawString((tab2 + doct_margin_left) * cm, (ab - 5.0 + doct_margin_top) * cm, nfz.encode('utf-8'))

    date = datetime.date.today().strftime('%d.%m.%Y')

    c.drawString((tab1 + 1 + doct_margin_left) * cm, (ab - 18.3 + doct_margin_top) * cm, date)
    c.drawString((tab1 + 1 + doct_margin_left) * cm, (ab - 18.3 - 1.8) * cm, realisation_date)

    return c