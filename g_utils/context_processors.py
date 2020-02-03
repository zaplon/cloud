from g_utils.forms import NoFormFormHelper
from django.conf import settings


def form_helpers(request):
    return {'NoFormFormHelper': NoFormFormHelper}


def utils(request):
    return {'APP_URL': settings.APP_URL}
