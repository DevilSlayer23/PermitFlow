from django.db import models
from django.conf import settings
from django.core.validators import MinValueValidator
from django.utils import timezone
from core.models import PermitType, Status
import uuid

def generate_application_number():
    """Generate unique application number in format BP-YYYY-NNNNN"""
    year = timezone.now().year
    # Get count of applications this year
    count = Application.objects.filter(
        submission_date__year=year
    ).count() + 1
    return f"BP-{year}-{count:05d}"


class Property(models.Model):
    """Property model for application location"""
    street_number = models.CharField(max_length=20)
    street_name = models.CharField(max_length=100)
    unit = models.CharField(max_length=20, blank=True)
    city = models.CharField(max_length=50, default='Toronto')
    province = models.CharField(max_length=2, default='ON')
    postal_code = models.CharField(max_length=7, db_index=True)
    legal_description = models.TextField(blank=True)
    ward = models.CharField(max_length=50, blank=True)
    zoning_designation = models.CharField(max_length=50, blank=True)

    lot_size = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        null=True, 
        blank=True
    )
    latitude = models.DecimalField(
        max_digits=10, 
        decimal_places=7, 
        null=True, 
        blank=True
    )
    longitude = models.DecimalField(
        max_digits=10, 
        decimal_places=7, 
        null=True, 
        blank=True
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'properties'
        verbose_name_plural = 'Properties'
        indexes = [
            models.Index(fields=['postal_code']),
            models.Index(fields=['city', 'street_name']),
        ]
    
    def __str__(self):
        address = f"{self.street_number} {self.street_name}"
        if self.unit:
            address += f", Unit {self.unit}"
        return f"{address}, {self.city}"
    
    @property
    def full_address(self):
        """Return formatted full address"""
        parts = [f"{self.street_number} {self.street_name}"]
        if self.unit:
            parts.append(f"Unit {self.unit}")
        parts.extend([self.city, self.province, self.postal_code])
        return ", ".join(parts)


class Application(models.Model):
    """Main application model"""
    PRIORITY_CHOICES = [
        (1, 'Low'),
        (2, 'Normal'),
        (3, 'High'),
        (4, 'Urgent'),
    ]
    
    # Unique identifier
    application_number = models.CharField(
        max_length=20, 
        unique=True, 
        default=generate_application_number,
        db_index=True
    )
    
    # Basic Information
    submission_date = models.DateTimeField(auto_now_add=True)
    project_description = models.TextField()
    estimated_value = models.DecimalField(
        max_digits=12, 
        decimal_places=2,
        validators=[MinValueValidator(0)]
    )
    
    # Status and Priority
    current_status = models.CharField(max_length=30, default='DRAFT', db_index=True)
    priority_level = models.IntegerField(choices=PRIORITY_CHOICES, default=2)
    
    # Dates
    target_completion_date = models.DateField(null=True, blank=True)
    actual_completion_date = models.DateField(null=True, blank=True)
    
    # Relationships
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name='applications'
    )
    permit_type = models.ForeignKey(
        PermitType,
        on_delete=models.PROTECT,
        related_name='applications'
    )
    # property = models.ForeignKey(
    #     Property,
    #     on_delete=models.PROTECT,
    #     related_name='applications'
    # )
    
    # Audit fields
    last_modified_date = models.DateTimeField(auto_now=True)
    last_modified_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name='modified_applications'
    )
    
    class Meta:
        db_table = 'applications'
        ordering = ['-submission_date']
        indexes = [
            models.Index(fields=['application_number']),
            models.Index(fields=['current_status']),
            models.Index(fields=['created_by']),
            models.Index(fields=['-submission_date']),
        ]
    
    def __str__(self):
        return f"{self.application_number} - {self.property.full_address}"
    
    def calculate_target_completion_date(self):
        """Calculate target completion date based on permit type"""
        if not self.target_completion_date:
            processing_days = self.permit_type.standard_processing_days
            self.target_completion_date = (
                self.submission_date + timezone.timedelta(days=processing_days)
            ).date()
            self.save(update_fields=['target_completion_date'])
    
    def update_status(self, new_status, user=None):
        """Update application status with audit trail"""
        old_status = self.current_status
        self.current_status = new_status
        if user:
            self.last_modified_by = user
        self.save()
        
        # Create status history record
        ApplicationStatusHistory.objects.create(
            application=self,
            from_status=old_status,
            to_status=new_status,
            changed_by=user,
            change_reason=f"Status changed from {old_status} to {new_status}"
        )


    @property
    def is_overdue(self):
        """Check if application is past target completion date"""
        if self.target_completion_date and self.current_status not in ['APPROVED', 'REJECTED']:
            return timezone.now().date() > self.target_completion_date
        return False
    
    @property
    def days_in_process(self):
        """Calculate days since submission"""
        if self.actual_completion_date:
            return (self.actual_completion_date - self.submission_date.date()).days
        return (timezone.now().date()- self.submission_date.date()).days


class ApplicationDocument(models.Model):
    """Document attachments for applications"""
    DOCUMENT_CATEGORIES = [
        ('Site Plan', 'Site Plan'),
        ('Building Plans', 'Building Plans'),
        ('Structural Drawings', 'Structural Drawings'),
        ('Engineering Reports', 'Engineering Reports'),
        ('Proof of Ownership', 'Proof of Ownership'),
        ('Other', 'Other'),
    ]
    
    application = models.ForeignKey(
        Application,
        on_delete=models.CASCADE,
        related_name='documents'
    )
    document_name = models.CharField(max_length=255)
    file = models.FileField(upload_to='applications/%Y/%m/')
    file_name = models.CharField(max_length=255)
    file_size = models.IntegerField()  # in bytes
    file_type = models.CharField(max_length=50)
    document_category = models.CharField(max_length=50, choices=DOCUMENT_CATEGORIES)
    is_required = models.BooleanField(default=False)
    version = models.IntegerField(default=1)
    
    uploaded_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True
    )
    upload_date = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'application_documents'
        ordering = ['-upload_date']
        indexes = [
            models.Index(fields=['application']),
        ]
    
    def __str__(self):
        return f"{self.document_name} - {self.application.application_number}"
    
    def save(self, *args, **kwargs):
        if self.file:
            self.file_size = self.file.size
            self.file_name = self.file.name
        super().save(*args, **kwargs)


class ApplicationStatusHistory(models.Model):
    """Track status changes for audit trail"""
    application = models.ForeignKey(
        Application,
        on_delete=models.CASCADE,
        related_name='status_history'
    )
    from_status = models.CharField(max_length=30)
    to_status = models.CharField(max_length=30)
    changed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True
    )
    changed_at = models.DateTimeField(auto_now_add=True)
    change_reason = models.TextField(blank=True)
    
    class Meta:
        db_table = 'application_status_history'
        ordering = ['-changed_at']
        verbose_name_plural = 'Application Status Histories'
    
    def __str__(self):
        return f"{self.application.application_number}: {self.from_status} → {self.to_status}"