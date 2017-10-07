from django.shortcuts import HttpResponseRedirect, render
from django.conf import settings


def permissions_middleware(get_response):
    
    def middleware(request):
        u = request.user
        for m in settings.MODULES:
            if request.path.startswith('/' + m[1]):
                if type(m[0]) == list:
                    if not (u.has_perm(m[0][0]) or u.has_perm(m[0][1])):
                        return render(request, 'no_permissions.html')
                elif m[0] is not True and not u.has_perm(m[0]):
                    return render(request, 'no_permissions.html')
        response = get_response(request)
        return response
    return middleware

    
def setup_middleware(get_response):
    # One-time configuration and initialization.

    def middleware(request):

        if request.user.is_authenticated():
            if request.path.startswith('/admin/') or request.path.startswith('/agreements/'):
                return get_response(request)
            if request.path.find('/setup/') == -1 and not request.method == 'POST':
                if hasattr(request.user, 'doctor'):
                    d = request.user.doctor
                    if len(d.pwz) == 0 or len(d.user.last_name) == 0:
                        return HttpResponseRedirect('/setup/1/')
                    if d.working_hours is None:
                        return HttpResponseRedirect('/setup/2/')
                else:
                    u = request.user
                    if not u.last_name:
                        return HttpResponseRedirect('/setup/1/')

        response = get_response(request)

        # Code to be executed for each request/response after
        # the view is called.

        return response

    return middleware
