from django.db import models
from django.conf import settings
from django.utils import timezone
from applications.models import Application
from core.models import PermitType

def generate_receipt_number():
    """Generate unique receipt number in format RCPT-YYYY-NNNNN"""
    year = timezone.now().year
    count = Payment.objects.filter(payment_date__year=year).count() + 1
    return f"RCPT-{year}-{count:05d}"


class FeeSchedule(models.Model):
    """Fee calculation configuration"""
    permit_type = models.ForeignKey(
        PermitType,
        on_delete=models.CASCADE,
        related_name='fee_schedules'
    )
    fee_schedule_name = models.CharField(max_length=100)
    effective_date = models.DateField()
    expiry_date = models.DateField(null=True, blank=True)
    
    base_fee = models.DecimalField(max_digits=10, decimal_places=2)
    valuation_rate = models.DecimalField(max_digits=5, decimal_places=4)  # 0.0150 = 1.5%
    minimum_fee = models.DecimalField(max_digits=10, decimal_places=2)
    maximum_fee = models.DecimalField(max_digits=10, decimal_places=2)
    
    calculation_formula = models.TextField(blank=True)
    fee_type = models.CharField(max_length=50, default='Standard')
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'fee_schedules'
        ordering = ['-effective_date']
    
    def __str__(self):
        return f"{self.fee_schedule_name} - {self.permit_type.permit_type_name}"
    
    def calculate_fee(self, project_value):
        """Calculate total fee based on project value"""
        calculated_fee = self.base_fee + (project_value * float(self.valuation_rate))
        
        # Apply minimum and maximum constraints
        if calculated_fee < self.minimum_fee:
            calculated_fee = self.minimum_fee
        elif calculated_fee > self.maximum_fee:
            calculated_fee = self.maximum_fee
        
        return float(calculated_fee)


class Payment(models.Model):
    """Payment transaction model"""
    PAYMENT_METHODS = [
        ('Credit Card', 'Credit Card'),
        ('Debit Card', 'Debit Card'),
        ('Bank Transfer', 'Bank Transfer'),
        ('Cheque', 'Cheque'),
    ]
    
    PAYMENT_STATUS_CHOICES = [
        ('Pending', 'Pending'),
        ('Completed', 'Completed'),
        ('Failed', 'Failed'),
        ('Refunded', 'Refunded'),
    ]
    
    application = models.ForeignKey(
        Application,
        on_delete=models.PROTECT,
        related_name='payment'
    )
    receipt_number = models.CharField(
        max_length=20,
        unique=True,
        default=generate_receipt_number,
        db_index=True
    )
    
    # Payment details
    payment_date = models.DateTimeField(auto_now_add=True)
    payment_amount = models.DecimalField(max_digits=10, decimal_places=2)
    base_amount = models.DecimalField(max_digits=10, decimal_places=2)
    tax_amount = models.DecimalField(max_digits=10, decimal_places=2)  # 13% HST
    
    payment_method = models.CharField(max_length=20, choices=PAYMENT_METHODS)
    payment_status = models.CharField(
        max_length=20,
        choices=PAYMENT_STATUS_CHOICES,
        default='Pending'
    )
    
    # Gateway information
    transaction_id = models.CharField(max_length=100, blank=True)
    card_last_four = models.CharField(max_length=4, blank=True)
    
    # User information
    paid_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name='payment'
    )
    
    # Refund information
    refund_amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True
    )
    refund_date = models.DateTimeField(null=True, blank=True)
    refund_reason = models.TextField(blank=True)
    
    fee_schedule = models.ForeignKey(
        FeeSchedule,
        on_delete=models.SET_NULL,
        null=True,
        related_name='payment'
    )
    
    class Meta:
        db_table = 'payment'
        ordering = ['-payment_date']
        indexes = [
            models.Index(fields=['receipt_number']),
            models.Index(fields=['application']),
            models.Index(fields=['payment_status']),
        ]
    
    def __str__(self):
        return f"{self.receipt_number} - ${self.payment_amount}"
    
    def calculate_amounts(self, base_amount):
        """Calculate payment amounts including tax"""
        self.base_amount = base_amount
        self.tax_amount = base_amount * 0.13  # 13% HST
        self.payment_amount = self.base_amount + self.tax_amount
        self.save(update_fields=['base_amount', 'tax_amount', 'payment_amount'])

class Transaction(models.Model):
    """Model to log payment gateway transactions"""
    payment = models.ForeignKey(
        Payment,
        on_delete=models.CASCADE,
        related_name='transactions'
    )
    transaction_type = models.CharField(max_length=50)  # e.g., Authorization, Capture, Refund
    transaction_id = models.CharField(max_length=100)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=20)  # e.g., Success, Failed
    response_code = models.CharField(max_length=50, blank=True)
    response_message = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'transactions'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['transaction_id']),
            models.Index(fields=['payment']),
        ]
    
    def __str__(self):
        return f"{self.transaction_type} - {self.transaction_id} - ${self.amount}"