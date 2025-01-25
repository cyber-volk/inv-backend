# serializers.py
from rest_framework import serializers
from .models import User, Manager, Product, Staff, InventoryLog

class UserSerializer(serializers.ModelSerializer):
    """
    Serializer for User model with role-based fields
    """
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'role', 'is_active']
        read_only_fields = ['id']

class UserCreateSerializer(serializers.ModelSerializer):
    """
    Serializer for creating users with roles
    """
    password = serializers.CharField(write_only=True)
    
    class Meta:
        model = User
        fields = ['username', 'email', 'password', 'role', 'department']

    def create(self, validated_data):
        password = validated_data.pop('password')
        user = User.objects.create(**validated_data)
        user.set_password(password)
        user.save()

        # Create corresponding profile based on role
        role = validated_data.get('role')
        if role == 'manager':
            Manager.objects.create(
                user=user,
                email=validated_data.get('email'),
                department=validated_data.get('department', '')
            )
        elif role == 'staff':
            Staff.objects.create(
                user=user,
                position='Staff Member',  # Default position
                shift='Day'  # Default shift
            )

        return user

class ManagerSerializer(serializers.ModelSerializer):
    """
    Serializer for Manager model with nested user information
    """
    user = UserSerializer(read_only=True)
    staff_count = serializers.SerializerMethodField()
    product_count = serializers.SerializerMethodField()

    class Meta:
        model = Manager
        fields = ['id', 'user', 'email', 'department', 'staff_count', 'product_count']
    
    def get_staff_count(self, obj):
        return obj.staff.count()
    
    def get_product_count(self, obj):
        return obj.products.count()

class ProductSerializer(serializers.ModelSerializer):
    """
    Serializer for Product model with stock status
    """
    stock_status = serializers.SerializerMethodField()

    class Meta:
        model = Product
        fields = '__all__'
        read_only_fields = ['created_at', 'updated_at']
    
    def get_stock_status(self, obj):
        return obj.check_stock()

class StaffSerializer(serializers.ModelSerializer):
    """
    Serializer for Staff model with nested user information
    """
    user = UserSerializer(read_only=True)
    managed_products = serializers.SerializerMethodField()

    class Meta:
        model = Staff
        fields = ['id', 'user', 'manager', 'position', 'shift', 'managed_products']
    
    def get_managed_products(self, obj):
        return ProductSerializer(obj.manager.products.all(), many=True).data

class InventoryLogSerializer(serializers.ModelSerializer):
    """
    Serializer for InventoryLog with additional context
    """
    product_name = serializers.CharField(source='product.name', read_only=True)
    staff_username = serializers.CharField(source='performed_by.user.username', read_only=True)

    class Meta:
        model = InventoryLog
        fields = '__all__'
        read_only_fields = ['date']