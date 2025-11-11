from django.contrib import admin
from .models import Property, Application, ApplicationDocument, ApplicationStatusHistory

# Register your models here.
admin.site.register(Property)
admin.site.register(Application)
admin.site.register(ApplicationDocument)
admin.site.register(ApplicationStatusHistory)