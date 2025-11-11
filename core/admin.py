from django.contrib import admin

from core.models import PermitType, Permit, Status

# Register your models here.
admin.site.register(Permit)
admin.site.register(PermitType)
admin.site.register(Status)
