from utils.forms import NoFormFormHelper
from user_profile.forms import DoctorForm

def form_helpers(request):
    return {'NoFormFormHelper': NoFormFormHelper}


def utils(request):
    if request.user.is_authenticated and hasattr(request.user, 'doctor'):
        user = request.user
        doctor = request.user.doctor
        profile_form = DoctorForm(initial={'first_name': user.first_name, 'last_name': user.last_name, 'pwz': doctor.pwz,
                    'email': user.email})
        return {'recipes_available': request.user.doctor.recipes.filter(was_used=False).count(), 'profile_form': profile_form,
                'recipes_total': request.user.doctor.recipes.count()}
    else:
        return {}
