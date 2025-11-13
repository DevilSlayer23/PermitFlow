from django.db import models

# Create your models here.
class RealEstate(models.Model):
    """RealEstate model for application location"""
    real_estate_id = models.AutoField(primary_key=True, db_index=True)
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
        db_table = 'real_estate'
        verbose_name_plural = 'Real Estates'
        indexes = [
            models.Index(fields=['postal_code']),
            models.Index(fields=['city', 'street_name']),
        ]
        app_label = 'real_estate'
    
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
    
