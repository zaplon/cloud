from g_utils.forms import NoFormFormHelper
from user_profile.forms import DoctorForm
from user_profile.rest import DoctorSerializer, UserSerializer
import json


def form_helpers(request):
    return {'NoFormFormHelper': NoFormFormHelper}


def utils(request):
    if request.user.is_authenticated and hasattr(request.user, 'doctor'):
        user = request.user
        doctor = request.user.doctor
        return {'recipes_available': request.user.doctor.recipes.filter(was_used=False).count(),
                'recipes_total': request.user.doctor.recipes.count(),
                'user_data': json.dumps(UserSerializer(instance=request.user).data),
                'doctor_data': json.dumps(DoctorSerializer(instance=doctor).data)}
    else:
        return {}
