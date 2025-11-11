from django.db import models
from users.models import Department

class Status(models.Model):
    """Application status model"""
    STATUS_CATEGORIES = [
        ('Initial', 'Initial'),
        ('Processing', 'Processing'),
        ('Pending', 'Pending'),
        ('Completed', 'Completed'),
    ]

    
    status_code = models.CharField(max_length=30, unique=True, db_index=True)
    status_name = models.CharField(max_length=100)
    status_description = models.TextField(blank=True)
    status_category = models.CharField(max_length=20, choices=STATUS_CATEGORIES)
    is_open_status = models.BooleanField(default=True)
    display_order = models.IntegerField(default=0)
    color_code = models.CharField(max_length=7, blank=True)  # Hex color code
    
    class Meta:
        db_table = 'statuses'
        ordering = ['display_order']
        verbose_name_plural = 'Statuses'
    
    def __str__(self):
        return self.status_name


class PermitType(models.Model):

     # Permit Categories
    # PERMIT_CATEGORIES = [
        
    #     ('Building', 'Building'),
    #     ('Demolition', 'Demolition'),
    #     ('Electrical', 'Electrical'),
    #     ('Plumbing', 'Plumbing'),
    #     ('Mechanical', 'Mechanical'),
    #     ('Zoning', 'Zoning'),
    #     ('Environmental', 'Environmental'),
    #     ('Signage', 'Signage'),
    #     ('Fire Safety', 'Fire Safety'),
    #     ('Other', 'Other'),

    # ]

    PERMIT_CATEGORIES = [
        ('Construction', 'Construction'),
        ('Right of Way', 'Right of Way'),
    ]

    """Permit type configuration"""
    permit_type_name = models.CharField(max_length=100)
    permit_category = models.CharField(max_length=50, choices=PERMIT_CATEGORIES)
    description = models.TextField(blank=True)
    standard_processing_days = models.IntegerField(default=90)
    requires_multiple_departments = models.BooleanField(default=False)
    required_documents = models.TextField(blank=True)  # JSON string
    application_form_template = models.CharField(max_length=255, blank=True)
    is_active = models.BooleanField(default=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'permit_types'
        ordering = ['permit_type_name']
    
    def __str__(self):
        return self.permit_type_name


class Permit(models.Model):
    """Permit application model"""
    applicant_name =  models.ForeignKey('users.User', on_delete=models.CASCADE)
    permit_type = models.ForeignKey(PermitType, on_delete=models.CASCADE)
    submission_date = models.DateTimeField(auto_now_add=True)
    current_status = models.ForeignKey(Status, on_delete=models.CASCADE)
    assigned_department = models.ForeignKey('users.Department', on_delete=models.CASCADE)
    processing_deadline = models.DateField(null=True, blank=True)
    is_approved = models.BooleanField(default=False)
    approval_date = models.DateTimeField(null=True, blank=True)
    notes = models.TextField(blank=True)
    
    class Meta:
        db_table = 'permits'
        ordering = ['-submission_date']
    
    def __str__(self):
        return f"Permit #{self.id} - {self.applicant_name}"

