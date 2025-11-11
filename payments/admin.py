from django.contrib import admin
from payments.models import Payment, FeeSchedule, Transaction

# Register your models here.
admin.site.register(Payment)
admin.site.register(FeeSchedule)
admin.site.register(Transaction)