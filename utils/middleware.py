from django.shortcuts import HttpResponseRedirect


def setup_middleware(get_response):
    # One-time configuration and initialization.

    def middleware(request):

        if request.user.is_authenticated() and hasattr(request.user, 'doctor'):
            if request.path.find('/setup/') == -1:
                d = request.user.doctor
                if len(d.pwz) == 0:
                    return HttpResponseRedirect('/setup/1/')
                if d.working_hours is None:
                    return HttpResponseRedirect('/setup/2/')

        response = get_response(request)

        # Code to be executed for each request/response after
        # the view is called.

        return response

    return middleware
