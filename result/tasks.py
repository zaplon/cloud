import os
import subprocess

from django_redis import get_redis_connection
from datetime import datetime
from dateutil.relativedelta import relativedelta
from django.conf import settings

from gabinet.tasks import app
from result.models import Result


@app.task()
def generate_results_pdf(patient_id, period):
    if period == 'all':
        pdf_files = Result.objects.filter(patient_id=patient_id)
    else:
        if period == '1 month':
            start_date = datetime.now() - relativedelta(months=1)
        elif period == '3 months':
            start_date = datetime.now() - relativedelta(months=3)
        pdf_files = Result.objects.filter(uploaded__gte=start_date, patient_id=patient_id)
    pdfs = []
    redis = get_redis_connection()
    if not pdf_files.exists():
        redis.set(settings.RESULTS_PDF_KEY_PATTERN % (patient_id, period), '-', settings.RESULTS_PDF_TTL)
    for pdf in pdf_files:
        if pdf.file.path.find('.pdf') > -1:
            pdfs.append(pdf.file.path)
    output_dir = os.path.join(settings.MEDIA_ROOT, 'merged_results')
    ts = datetime.now().strftime('%s')
    file_name = os.path.join(output_dir, '%s.pdf' % ts)
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    subprocess.check_output(["pdftk", pdfs.join(' '), 'cat', 'output', file_name], stderr=subprocess.STDOUT)
    file_url = 'media/merged_results/%s.pdf' % ts
    redis.set(settings.RESULTS_PDF_KEY_PATTERN % (patient_id, period), file_url, settings.RESULTS_PDF_TTL)
