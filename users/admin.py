from django.contrib import admin

from users.models import User, UserManager, Role, Department

# Register your models here.
admin.site.register([User, Role, Department])