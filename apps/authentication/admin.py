from django.contrib import admin

from authentication.models import CustomUser, UserManager, Role, Department

# Register your models here.
@admin.register(CustomUser)
class CustomUserAdmin(admin.ModelAdmin):
    list_display = ('username', 'email', 'first_name', 'last_name', 'role', 'is_active', 'is_staff')
    search_fields = ('username', 'email', 'first_name', 'last_name')
    list_filter = ('role', 'is_active', 'is_staff')
    ordering = ('username',)

@admin.register(Role)
class RoleAdmin(admin.ModelAdmin):
    list_display = ('role_name', 'description', 'permission_level')
    search_fields = ('role_name',)
    ordering = ('role_name',)

@admin.register(Department)
class DepartmentAdmin(admin.ModelAdmin):
    list_display = ('department_name', 'department_code', 'contact_email', 'is_active')
    search_fields = ('department_name', 'department_code')
    list_filter = ('is_active',)
    ordering = ('department_name',)
