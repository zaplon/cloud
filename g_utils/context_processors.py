from g_utils.forms import NoFormFormHelper
from g_utils.templatetags.utils_tags import is_doctor
from user_profile.forms import DoctorForm
from user_profile.models import SystemSettings
from user_profile.rest import DoctorSerializer, UserSerializer
import json
from django.conf import settings


def form_helpers(request):
    return {'NoFormFormHelper': NoFormFormHelper}


def utils(request):
    return {'APP_URL': settings.APP_URL}
