from django.core.exceptions import ValidationError
from django.db import models
from django.conf import settings
from django.utils.translation import ugettext as _
from django.contrib.auth.models import Group


class AgreementToUser(models.Model):
    datetime = models.DateTimeField(auto_now_add=True, verbose_name=_('Added date'))
    user = models.ForeignKey(settings.AUTH_USER_MODEL, verbose_name=_('User'))
    agreement = models.ForeignKey('Agreement', verbose_name=_('Agreement'))

    class Meta:
        verbose_name = _('user agreement')
        verbose_name_plural = _('users agreements')

    def __unicode__(self):
        return "%s - %s" % (str(self.agreement), str(self.user))


class Agreement(models.Model):
    users = models.ManyToManyField(settings.AUTH_USER_MODEL, through=AgreementToUser, related_name='agreements')
    text = models.TextField(blank=True, null=True, verbose_name=_('Text'))
    document = models.FileField(blank=True, null=True, verbose_name=_('Document'))
    title = models.CharField(max_length=256, blank=True, null=True, verbose_name=_('Title'))
    targeted_users = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name=_('user_agreements'),
                                            verbose_name=_('targeted users'),
                                            help_text=_('select users which should see the agreement.'))

    class Meta:
        verbose_name = _('agreement')
        verbose_name_plural = _('agreements')

    def clean(self):
        if self.document and self.document.name.split('.')[-1] not in ['pdf', 'doc', 'txt']:
            raise ValidationError(_(u'The file attached to the agreement should be a text document'))

    def __unicode__(self):
        return self.title if self.title else self.text[0:100]
