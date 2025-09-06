from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
    ROLE_CHOICES = [
        ('user', 'User'),
        ('vendor', 'Vendor'),
        ('admin', 'Admin'),
    ]
    role = models.CharField(max_length=15, choices=ROLE_CHOICES, default='user')
    fullname = models.CharField(max_length=255)

    def is_vendor(self):
        return self.role == 'vendor'

    def is_admin(self):
        return self.role == 'admin'
    
    
class Vendor(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='vendor_profile')
    business_name = models.CharField(max_length=255)
    business_email = models.EmailField()
    phone_number = models.CharField(max_length=20)
    website = models.CharField(max_length=255,null=True, blank=True)
    division = models.CharField(max_length=255)
    district = models.CharField(max_length=255)
    sub_district = models.CharField(max_length=255)
    union = models.CharField(max_length=255, blank=True)
    address = models.CharField(max_length=255)
    profile_image = models.ImageField()
    license_image = models.ImageField()
    nid_front = models.ImageField()
    nid_back = models.ImageField()
    registration_number = models.CharField(max_length=100, blank=True)
    tax_id = models.CharField(max_length=100, blank=True,)
    business_description = models.TextField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.business_name
