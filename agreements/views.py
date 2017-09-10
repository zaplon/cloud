from django.contrib.auth.decorators import login_required
from django.dispatch import receiver
from django.http import HttpResponseBadRequest, HttpResponseRedirect
from django.shortcuts import redirect
from django.urls import reverse
from django.core.exceptions import ObjectDoesNotExist

from agreements.models import Agreement, AgreementToUser
from django.views.generic import TemplateView
from django.contrib.auth.signals import user_logged_in


@receiver(user_logged_in)
def redirect_to_agreement(**kwargs):
    if Agreement.objects.all().exclude(users=kwargs['user']).exists():
        a = Agreement.objects.all().exclude(users=kwargs['user'])[0]
        kwargs['request'].session['agreement_to_show'] = a.id
    else:
        if 'agreement_to_show' in kwargs['request'].session:
            del kwargs['request'].session['agreement_to_show']


class AgreementView(TemplateView):
    template_name = 'agreements/agreement.html'

    def get_context_data(self, **kwargs):
        try:
            agreement = Agreement.objects.get(id=self.kwargs['agreement'])
        except ObjectDoesNotExist:
            return HttpResponseBadRequest()
        context = super(AgreementView, self).get_context_data(**kwargs)
        context.update({
            'user': self.request.user,
            'object': agreement
        })
        return context

    def post(self, request, *args, **kwargs):
        context = self.get_context_data(**kwargs)
        AgreementToUser.objects.get_or_create(user=context['user'], agreement=context['object'])
        redirect_to_agreement(user=context['user'], request=request)
        return redirect('/')
