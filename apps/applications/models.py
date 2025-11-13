from django.db import models
from django.conf import settings
from django.core.validators import MinValueValidator
from django.forms import ValidationError
from django.utils import timezone
from apps.real_estate.models import RealEstate
from authentication.models import CustomUser
from permits.models import Permit



def generate_application_number():
    """Generate unique application number in format BP-YYYY-NNNNN"""
    year = timezone.now().year
    # Get count of applications this year
    count = Application.objects.filter(
        submission_date__year=year
    ).count() + 1
    return f"BP-{year}-{count:05d}"

def validate_file_size(value):
        if value > 5000:
            raise ValidationError(f'File size ({value}) is too large. The maximum file size allowed is 5MB.')
        

""" Begin Status Model Definition """

class Status(models.Model):
    """Application status model"""
    STATUS_CATEGORIES = [
        ('Initial', 'Initial'),
        ('Processing', 'Processing'),
        ('Pending', 'Pending'),
        ('Completed', 'Completed'),
    ]

    status_id = models.AutoField(primary_key=True)
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
        app_label = 'applications'
    
    def __str__(self):
        return self.status_name
    
"""End Status Model Definition """

"""Begin Application Model Definition """

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
        db_index=True,
        primary_key=True
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
    current_status = models.ForeignKey(
        Status,
        on_delete=models.PROTECT,
        related_name='applications'
    
    )
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

    permit = models.ForeignKey(
        Permit,
        on_delete=models.PROTECT,
        related_name='applications',
        null=True,
        blank=True
    )

    associated_property = models.ForeignKey(
        RealEstate,
        on_delete=models.PROTECT,
        related_name='applications',
    )

    
    # Audit fields
    created_date = models.DateTimeField(default=timezone.now())
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
        app_label = 'applications'
    
    def __str__(self):
        return f"{self.application_number} - {self.current_status}"
    
    def save(self, *args, **kwargs):
        is_new = self._state.adding
        super().save(*args, **kwargs)
        if is_new:
            self.calculate_target_completion_date()

    def calculate_target_completion_date(self):
        """Calculate target completion date based on permit type"""
        if not self.target_completion_date:
            processing_days = self.permit.standard_processing_days
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

"""End Application Model Definition """


"""Begin ApplicationDocument Model Definition """

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
    # document_id = models.AutoField(primary_key=True)
    document_name = models.CharField(max_length=255)
    file = models.FileField(upload_to='applications/%Y/%m/')
    file_name = models.CharField(max_length=255, blank=True)
    file_type = models.CharField(max_length=50, blank=True)
    file_size = models.DecimalField(blank=True, decimal_places=2, max_digits = 100, validators=[validate_file_size])# Size in bytes
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
        app_label = 'applications'
    
    def __str__(self):
        return f"{self.document_name} - {self.application.application_number}"
    
    
    
    def save(self, *args, **kwargs):
        if self.file:
            self.file_size = self.file.size/1000
            self.file_name = self.file.name
            if self.file_size > 5000:
                self.version += 1

        
        super().save(*args, **kwargs)

        super().save(*args, **kwargs)
"""End ApplicationDocument Model Definition """

"""Begin ApplicationStatusHistory Model Definition """

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

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)

"""End ApplicationStatusHistory Model Definition """

"""Begin Applicant Model Definition """

class Applicant:
    """Applicant model for application applicants"""

    application = models.ForeignKey(
        Application,
        on_delete=models.CASCADE,
        related_name='applicants'
    )
    applicant_id = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    email = models.EmailField()
    phone_number = models.CharField(max_length=20, blank=True)
    organization_name = models.CharField(max_length=100, blank=True)
    role = models.CharField(max_length=50, blank=True)  # e.g., Owner, Contractor
    is_active = models.BooleanField(default=True)
    
    class Meta:
        db_table = 'applicants'
        indexes = [
            models.Index(fields=['application']),
        ]
        app_label = 'applications'
    
    def __str__(self):
        return f"{self.first_name} {self.last_name} - {self.application.application_number}"
    
"""End Applicant Model Definition """