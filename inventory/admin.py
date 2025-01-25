from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User, Manager, Product, Staff, InventoryLog

# Register your models here.

@admin.register(User)
class CustomUserAdmin(UserAdmin):
    list_display = ('username', 'email', 'role', 'department', 'is_active', 'date_joined')
    list_filter = ('role', 'is_active', 'department')
    search_fields = ('username', 'email', 'department')
    ordering = ('-date_joined',)
    fieldsets = UserAdmin.fieldsets + (
        ('Additional Info', {'fields': ('role', 'department')}),
    )

@admin.register(Manager)
class ManagerAdmin(admin.ModelAdmin):
    list_display = ('user', 'email', 'department')
    search_fields = ('user__username', 'email', 'department')
    list_filter = ('department',)

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'sku', 'category', 'quantity', 'price', 'manager')
    list_filter = ('category', 'manager')
    search_fields = ('name', 'sku', 'description')
    ordering = ('name',)
    readonly_fields = ('created_at', 'updated_at')

@admin.register(Staff)
class StaffAdmin(admin.ModelAdmin):
    list_display = ('user', 'position', 'shift', 'manager')
    list_filter = ('position', 'shift', 'manager')
    search_fields = ('user__username', 'position')

@admin.register(InventoryLog)
class InventoryLogAdmin(admin.ModelAdmin):
    list_display = ('product', 'action_type', 'quantity_change', 'date', 'performed_by')
    list_filter = ('action_type', 'date', 'performed_by')
    search_fields = ('product__name', 'notes')
    readonly_fields = ('date',)
    ordering = ('-date',)
