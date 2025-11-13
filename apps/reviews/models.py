from django.db import models
from django.conf import settings
from applications.models import Application
from permits.models import Department

class Review(models.Model):
    """Technical review model"""
    REVIEW_TYPES = [
        ('Building Code', 'Building Code'),
        ('Zoning', 'Zoning'),
        ('Fire Safety', 'Fire Safety'),
        ('Engineering', 'Engineering'),
        ('Heritage', 'Heritage'),
    ]
    
    REVIEW_DECISIONS = [
        ('Approved', 'Approved'),
        ('Approved with Conditions', 'Approved with Conditions'),
        ('Requires Additional Information', 'Requires Additional Information'),
        ('Rejected', 'Rejected'),
    ]
    
    application = models.ForeignKey(
        Application,
        on_delete=models.CASCADE,
        related_name='reviews'
    )
    review_type = models.CharField(max_length=50, choices=REVIEW_TYPES)
    reviewer = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name='reviews'
    )
    department = models.ForeignKey(
        Department,
        on_delete=models.PROTECT,
        related_name='reviews'
    )
    
    # Dates
    assigned_date = models.DateTimeField(auto_now_add=True)
    start_date = models.DateTimeField(null=True, blank=True)
    completion_date = models.DateTimeField(null=True, blank=True)
    
    # Review details
    review_decision = models.CharField(
        max_length=50, 
        choices=REVIEW_DECISIONS, 
        blank=True
    )
    findings_summary = models.TextField(blank=True)
    conditions = models.TextField(blank=True)
    reviewer_notes = models.TextField(blank=True)
    review_duration = models.IntegerField(null=True, blank=True)  # minutes
    is_completed = models.BooleanField(default=False)
    
    class Meta:
        db_table = 'reviews'
        ordering = ['-assigned_date']
        indexes = [
            models.Index(fields=['application']),
            models.Index(fields=['reviewer']),
            models.Index(fields=['is_completed']),
        ]
    
    def __str__(self):
        return f"{self.review_type} - {self.application.application_number}"