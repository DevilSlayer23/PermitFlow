from django.db import models
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, BaseUserManager
from django.core.validators import MinLengthValidator
from django.utils import timezone

class UserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError('Users must have an email address')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('account_status', 'Active')
        
        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')
        
        return self.create_user(email, password, **extra_fields)


class Role(models.Model):
    """Role model for permissions management"""
    role_name = models.CharField(max_length=50, unique=True)
    role_description = models.TextField(blank=True)
    permission_level = models.IntegerField(default=1)
    
    # Permission flags
    can_submit_applications = models.BooleanField(default=False)
    can_review_applications = models.BooleanField(default=False)
    can_approve_applications = models.BooleanField(default=False)
    can_configure_system = models.BooleanField(default=False)
    can_manage_users = models.BooleanField(default=False)
    can_view_all_applications = models.BooleanField(default=False)
    can_generate_reports = models.BooleanField(default=False)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'roles'
        ordering = ['role_name']
    
    def __str__(self):
        return self.role_name


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
    
    def __str__(self):
        return f"{self.department_name} ({self.department_code})"


class User(AbstractBaseUser, PermissionsMixin):
    """Custom user model"""
    ACCOUNT_TYPE_CHOICES = [
        ('Admin', 'Admin'),
        ('Municipal Staff', 'Municipal Staff'),
        ('External Professional', 'External Professional'),
        ('Applicant', 'Applicant'),
    ]
    
    ACCOUNT_STATUS_CHOICES = [
        ('Active', 'Active'),
        ('Inactive', 'Inactive'),
        ('Locked', 'Locked'),
        ('Pending Activation', 'Pending Activation'),
    ]
    
    # Basic Information
    email = models.EmailField(unique=True, db_index=True)
    username = models.CharField(max_length=150, unique=True, db_index=True)
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    phone_number = models.CharField(max_length=20, blank=True)
    
    # Account Information
    account_type = models.CharField(max_length=30, choices=ACCOUNT_TYPE_CHOICES)
    account_status = models.CharField(
        max_length=20, 
        choices=ACCOUNT_STATUS_CHOICES, 
        default='Active'
    )
    
    # Relationships
    # role = models.ForeignKey(Role, on_delete=models.PROTECT, related_name='users') or None
    department = models.ForeignKey(
        Department, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        related_name='users'
    )
    
    # Security
    failed_login_attempts = models.IntegerField(default=0)
    mfa_enabled = models.BooleanField(default=False)
    require_password_change = models.BooleanField(default=False)
    
    # Timestamps
    created_date = models.DateTimeField(auto_now_add=True)
    last_login_date = models.DateTimeField(null=True, blank=True)
    
    # Django required fields
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)
    
    objects = UserManager()
    
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'first_name', 'last_name', 'account_type']
    
    class Meta:
        db_table = 'users'
        ordering = ['-created_date']
        indexes = [
            models.Index(fields=['email']),
            models.Index(fields=['username']),
            models.Index(fields=['account_status']),
        ]
    
    def __str__(self):
        return f"{self.get_full_name()} ({self.email})"
    
    def get_full_name(self):
        return f"{self.first_name} {self.last_name}"
    
    def has_permission(self, permission):
        """Check if user has specific permission"""
        return getattr(self.role, permission, False)
    
    def update_last_login(self):
        """Update last login timestamp"""
        self.last_login_date = timezone.now()
        self.save(update_fields=['last_login_date'])
    
    def increment_failed_login(self):
        """Increment failed login attempts and lock account if threshold reached"""
        self.failed_login_attempts += 1
        if self.failed_login_attempts >= 5:
            self.account_status = 'Locked'
        self.save(update_fields=['failed_login_attempts', 'account_status'])
    
    def reset_failed_login(self):
        """Reset failed login attempts"""
        self.failed_login_attempts = 0
        self.save(update_fields=['failed_login_attempts'])