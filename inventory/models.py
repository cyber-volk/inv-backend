# models.py
from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils import timezone

class User(AbstractUser):
    """
    Custom User model to extend Django's built-in User model
    Allows for additional fields specific to inventory management
    """
    ROLE_CHOICES = (
        ('admin', 'Administrator'),
        ('manager', 'Manager'),
        ('staff', 'Staff'),
    )
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='staff')
    department = models.CharField(max_length=100, blank=True, null=True)
    is_active = models.BooleanField(default=True)

class Manager(models.Model):
    """
    Manager model representing inventory managers
    """
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='manager_profile')
    email = models.EmailField(unique=True)
    department = models.CharField(max_length=100)

    def __str__(self):
        return self.user.username

class Product(models.Model):
    """
    Product model for tracking inventory items
    """
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    quantity = models.IntegerField(default=0)
    low_threshold = models.IntegerField(default=10)
    high_threshold = models.IntegerField(default=100)
    category = models.CharField(max_length=100)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    sku = models.CharField(max_length=50, unique=True)
    
    # Relationships
    manager = models.ForeignKey(Manager, on_delete=models.SET_NULL, null=True, related_name='products')
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

    def check_stock(self):
        """
        Check current stock level and return status
        """
        if self.quantity <= self.low_threshold:
            return 'low'
        elif self.quantity >= self.high_threshold:
            return 'high'
        return 'normal'

class Staff(models.Model):
    """
    Staff model for inventory employees
    """
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='staff_profile')
    manager = models.ForeignKey(Manager, on_delete=models.SET_NULL, null=True, related_name='staff')
    position = models.CharField(max_length=100)
    shift = models.CharField(max_length=50)

    def __str__(self):
        return self.user.username

class InventoryLog(models.Model):
    """
    Inventory Log for tracking product movements and changes
    """
    ACTION_TYPES = (
        ('add', 'Stock Added'),
        ('remove', 'Stock Removed'),
        ('adjust', 'Stock Adjusted'),
    )

    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='inventory_logs')
    action_type = models.CharField(max_length=10, choices=ACTION_TYPES)
    quantity_change = models.IntegerField()
    date = models.DateTimeField(default=timezone.now)
    performed_by = models.ForeignKey(Staff, on_delete=models.SET_NULL, null=True)
    notes = models.TextField(blank=True)

    def __str__(self):
        return f"{self.product.name} - {self.action_type} - {self.quantity_change}"