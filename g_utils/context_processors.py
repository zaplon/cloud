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
    ctx = {}
    system_settings = SystemSettings.objects.first()
    ctx.update({
        'system_settings': system_settings
    })
    if request.user.is_authenticated():
        ctx.update({'user_data': json.dumps(UserSerializer(instance=request.user).data)})
        if is_doctor(False, request.user):
            user = request.user
            doctor = user.doctor
            ctx.update({'recipes_available': request.user.doctor.recipes.filter(was_used=False).count(),
                        'recipes_total': request.user.doctor.recipes.count(),
                        'doctor_data': json.dumps(DoctorSerializer(instance=doctor).data)})

    ctx.update({'MODULES': settings.MODULES, 'APP_URL': settings.APP_URL})
    return ctx
