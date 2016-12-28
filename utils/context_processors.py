from utils.forms import NoFormFormHelper


def form_helpers(request):
    return {'NoFormFormHelper': NoFormFormHelper}


def utils(request):
    if request.user.is_authenticated and hasattr(request.user, 'doctor'):
        return {'recipes_available': request.user.doctor.recipes.filter(was_used=False).count(),
                'recipes_total': request.user.doctor.recipes.count()}
    else:
        return {}