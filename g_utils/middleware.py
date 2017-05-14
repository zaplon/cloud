from django.shortcuts import HttpResponseRedirect
from django.conf import settings


def setup_middleware(get_response):
    # One-time configuration and initialization.

    def middleware(request):

        if request.user.is_authenticated():
            if request.path.find('/setup/') == -1 and not request.method == 'POST':
                if hasattr(request.user, 'doctor'):
                    d = request.user.doctor
                    if len(d.pwz) == 0:
                        return HttpResponseRedirect('/setup/1/')
                    if d.working_hours is None:
                        return HttpResponseRedirect('/setup/2/')
                else:
                    u = request.user
                    if not u.profile.mobile:
                        return HttpResponseRedirect('/setup/1/')

        response = get_response(request)

        # Code to be executed for each request/response after
        # the view is called.

        return response

    return middleware
