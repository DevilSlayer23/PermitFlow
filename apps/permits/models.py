from .constants import PERMIT_CATEGORIES
from django.db import models

class Department(models.Model):
    """Municipal department model"""
    department_name = models.CharField(max_length=100)
    department_code = models.CharField(max_length=10, unique=True)
    contact_email = models.EmailField()
    contact_phone = models.CharField(max_length=20)
    physical_location = models.CharField(max_length=255, blank=True)
    is_active = models.BooleanField(default=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'departments'
        ordering = ['department_name']
        app_label = 'permits'

    def __str__(self):
        return f"{self.department_name} ({self.department_code})"




class Permit(models.Model):
    """Permit Type model representing different types of permits"""
    permit_id = models.AutoField(primary_key=True)
    permit_name = models.CharField(max_length=100)
    category = models.CharField(max_length=50, choices=PERMIT_CATEGORIES)
    description = models.TextField(blank=True)
    standard_processing_days = models.IntegerField(default=90)
    requires_multiple_departments = models.BooleanField(default=False)
    required_documents = models.TextField(blank=True)  # JSON string
    is_active = models.BooleanField(default=True)
    notes = models.TextField(blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    
    if (requires_multiple_departments):
        associated_departments = models.ManyToManyField(Department, blank=True, related_name='permits')
    else:
        associated_department = models.ForeignKey(Department, on_delete=models.CASCADE, blank=True, related_name='permits') 

    class Meta:
        db_table = 'permit'
        ordering = ['permit_name']
        app_label = 'permits'
    
    def __str__(self):
        return self.permit_name



