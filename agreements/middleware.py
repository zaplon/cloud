from django.http import HttpResponseRedirect
from django.urls import reverse
from django.conf import settings


def display_agreement_middleware(get_response):

    def middleware(request):

        if 'agreement_to_show' in request.session:
            url = reverse('agreements:agreement', kwargs={'agreement': request.session['agreement_to_show']})
            if not request.path == url and not request.path.startswith(settings.MEDIA_URL):
                return HttpResponseRedirect(url)
        response = get_response(request)
        return response

    return middleware
