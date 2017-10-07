from django.contrib import admin
from .models import Agreement, AgreementToUser


class AgreementToUserAdmin(admin.ModelAdmin):
    fields = ('user', 'agreement', 'datetime')
    readonly_fields = ('datetime',)


class AgreementAdmin(admin.ModelAdmin):
    fields = ('title', 'text', 'document', 'targeted_users')


admin.site.register(Agreement, AgreementAdmin)
admin.site.register(AgreementToUser, AgreementToUserAdmin)
