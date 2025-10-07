
from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.utils import timezone

class CustomUserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError('The Email must be set')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password) 
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('role', 'admin')
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return self.create_user(email, password, **extra_fields)


class User(AbstractBaseUser, PermissionsMixin):
    ROLE_CHOICES = [
        ('applicant', 'Applicant'),
        ('lawyer', 'Lawyer'),
        ('lsk_admin', 'LSK Admin'),
        ('admin', 'Admin')
    ]

    first_name = models.CharField(max_length=500)
    last_name = models.CharField(max_length=500)
    email = models.EmailField(max_length=1000, unique=True, null=True)
    role = models.CharField(max_length=100, choices=ROLE_CHOICES, default='applicant')
    phone_number = models.CharField(max_length=20, null=True, blank=True)
    image = models.ImageField(upload_to='profiles/', null=True, blank=True)
    is_deleted = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    objects = CustomUserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name', 'last_name']

    def __str__(self):
        return f"{self.first_name} {self.last_name}"


class LawyerProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='lawyer_profile')
    latitude = models.DecimalField(max_digits=15, decimal_places=6, null=True, blank=True)
    longitude = models.DecimalField(max_digits=15, decimal_places=6, null=True, blank=True)
    profile_id = models.CharField(max_length=100, unique=True)
    verified = models.BooleanField(default=False)
    practising_status = models.CharField(max_length=20, blank=True)
    practice_number = models.CharField(max_length=100, blank=True, unique=True)
    work_place = models.TextField(blank=True)
    physical_address = models.TextField(blank=True)
    cpd_points_2025 = models.IntegerField(default=0)
    criminal_law = models.BooleanField(default=False)
    constitutional_law = models.BooleanField(default=False)
    corporate_law = models.BooleanField(default=False)
    family_law = models.BooleanField(default=False)
    pro_bono_legal_services = models.BooleanField(default=False)
    alternative_dispute_resolution = models.BooleanField(default=False)
    regional_and_international_law = models.BooleanField(default=False)
    mining_law = models.BooleanField(default=False)

    def __str__(self):
        return f"Lawyer: {self.user.first_name} {self.user.last_name} ({self.practice_number})"


class LskAdminProfile(models.Model):
    lawyer = models.OneToOneField(LawyerProfile, on_delete=models.CASCADE, related_name='lsk_admin_profile')

    def __str__(self):
        return f"LSK Admin: {self.lawyer.user.email}"


class ApplicantProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='applicant_profile')

    def __str__(self):
        return f"Applicant: {self.user.email}"



















