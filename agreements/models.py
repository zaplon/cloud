from django.core.exceptions import ValidationError
from django.db import models
from django.conf import settings
from django.utils.translation import ugettext as _
# Create your models here.


class AgreementToUser(models.Model):
    datetime = models.DateTimeField(auto_now_add=True, verbose_name=_('Added date'))
    user = models.ForeignKey(settings.AUTH_USER_MODEL, verbose_name=_('User'))
    agreement = models.ForeignKey('Agreement', verbose_name=_('Agreements'))


class Agreement(models.Model):
    users = models.ManyToManyField(settings.AUTH_USER_MODEL, through=AgreementToUser, related_name='agreements')
    text = models.TextField(blank=True, null=True)
    document = models.FileField(blank=True, null=True)
    title = models.CharField(max_length=256, blank=True, null=True)

    def clean(self):
        if self.document and self.document.name.split('.')[-1] not in ['pdf', 'doc', 'txt']:
            raise ValidationError(_(u'The file attached to the agreement should be a text document'))

    def __unicode__(self):
        return self.title if self.title else self.text[0:100]
