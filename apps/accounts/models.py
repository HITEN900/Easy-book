from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
    USER_TYPES = (
        ('customer', 'Customer'),
        ('bus_owner', 'Bus Owner'),
    )
    
    user_type = models.CharField(max_length=20, choices=USER_TYPES, default='customer')
    phone = models.CharField(max_length=15, unique=True)  # Added unique=True
    email = models.EmailField(unique=True)
    
    def __str__(self):
        return f"{self.username} ({self.get_user_type_display()})"