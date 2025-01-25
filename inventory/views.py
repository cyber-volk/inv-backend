# views.py
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from .models import User, Manager, Product, Staff, InventoryLog
from .serializers import (UserSerializer, UserCreateSerializer, ManagerSerializer, 
                          ProductSerializer, StaffSerializer, InventoryLogSerializer)
from .permissions import IsAdminUser, IsManagerUser, IsStaffUser

class UserViewSet(viewsets.ModelViewSet):
    """
    ViewSet for User management with role-based permissions
    Supports: CRUD operations, activation/deactivation
    """
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAdminUser]

    @action(detail=True, methods=['patch'])
    def toggle_activation(self, request, pk=None):
        """
        Custom action to activate/deactivate user
        """
        user = self.get_object()
        user.is_active = not user.is_active
        user.save()
        return Response({
            'status': 'User activation toggled', 
            'is_active': user.is_active
        })

class UserCreateViewSet(viewsets.ModelViewSet):
    """
    ViewSet for creating new users with roles
    """
    queryset = User.objects.all()
    serializer_class = UserCreateSerializer
    permission_classes = [AllowAny]  # Allow anyone to register

    def get_permissions(self):
        if self.action in ['create']:
            return [AllowAny()]
        return [IsAdminUser()]

class ManagerViewSet(viewsets.ModelViewSet):
    """
    ViewSet for Manager management
    Supports: CRUD operations, staff and product listing
    """
    queryset = Manager.objects.all()
    serializer_class = ManagerSerializer
    permission_classes = [IsAdminUser]

    @action(detail=True)
    def staff(self, request, pk=None):
        """
        List staff managed by this manager
        """
        manager = self.get_object()
        staff = manager.staff.all()
        serializer = StaffSerializer(staff, many=True)
        return Response(serializer.data)

    @action(detail=True)
    def products(self, request, pk=None):
        """
        List products managed by this manager
        """
        manager = self.get_object()
        products = manager.products.all()
        serializer = ProductSerializer(products, many=True)
        return Response(serializer.data)

    @action(detail=True)
    def reports(self, request, pk=None):
        """
        Generate manager-specific reports
        """
        manager = self.get_object()
        # Implement report generation logic
        return Response({
            'total_staff': manager.staff.count(),
            'total_products': manager.products.count(),
        })

class ProductViewSet(viewsets.ModelViewSet):
    """
    ViewSet for Product management
    Supports: CRUD operations, stock management
    """
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    permission_classes = [IsManagerUser]

    @action(detail=True)
    def stock(self, request, pk=None):
        """
        Check current product stock
        """
        product = self.get_object()
        return Response({
            'quantity': product.quantity,
            'status': product.check_stock()
        })

    @action(detail=True, methods=['POST'])
    def update_stock(self, request, pk=None):
        """
        Update product quantity
        """
        product = self.get_object()
        quantity = request.data.get('quantity', 0)
        action_type = request.data.get('action', 'adjust')

        if action_type == 'add':
            product.quantity += quantity
        elif action_type == 'remove':
            product.quantity = max(0, product.quantity - quantity)
        product.save()

        # Create inventory log
        InventoryLog.objects.create(
            product=product,
            action_type=action_type,
            quantity_change=quantity,
            performed_by=request.user.staff_profile
        )

        return Response({
            'new_quantity': product.quantity,
            'status': product.check_stock()
        })

    @action(detail=True)
    def logs(self, request, pk=None):
        """
        Get product inventory logs
        """
        product = self.get_object()
        logs = product.inventory_logs.all()
        serializer = InventoryLogSerializer(logs, many=True)
        return Response(serializer.data)

    @action(detail=True)
    def barcode(self, request, pk=None):
        """
        Generate product barcode
        """
        product = self.get_object()
        # Implement barcode generation logic
        return Response({
            'barcode': f'BARCODE-{product.sku}'
        })

class StaffViewSet(viewsets.ModelViewSet):
    """
    ViewSet for Staff management
    Supports: CRUD operations, product and log management
    """
    queryset = Staff.objects.all()
    serializer_class = StaffSerializer
    permission_classes = [IsManagerUser]

    @action(detail=True)
    def logs(self, request, pk=None):
        """
        Get staff activity logs
        """
        staff = self.get_object()
        logs = InventoryLog.objects.filter(performed_by=staff)
        serializer = InventoryLogSerializer(logs, many=True)
        return Response(serializer.data)

    @action(detail=True)
    def products(self, request, pk=None):
        """
        List products managed by staff
        """
        staff = self.get_object()
        products = staff.manager.products.all()
        serializer = ProductSerializer(products, many=True)
        return Response(serializer.data)

class InventoryLogViewSet(viewsets.ModelViewSet):
    """
    ViewSet for Inventory Log management
    Supports: CRUD operations, report generation
    """
    queryset = InventoryLog.objects.all()
    serializer_class = InventoryLogSerializer
    permission_classes = [IsManagerUser]

    @action(detail=False)
    def reports(self, request):
        """
        Generate comprehensive inventory reports
        """
        # Basic inventory statistics
        total_logs = self.queryset.count()
        logs_by_action = self.queryset.values('action_type').annotate(count=models.Count('id'))
        
        # Aggregate product movement
        product_movement = self.queryset.values('product__name').annotate(
            total_added=models.Sum(
                models.Case(
                    models.When(action_type='add', then=models.F('quantity_change')),
                    default=0
                )
            ),
            total_removed=models.Sum(
                models.Case(
                    models.When(action_type='remove', then=models.F('quantity_change')),
                    default=0
                )
            )
        )

        return Response({
            'total_logs': total_logs,
            'logs_by_action': list(logs_by_action),
            'product_movement': list(product_movement)
        })

    @action(detail=False)
    def statistics(self, request):
        """
        Get detailed inventory statistics
        """
        # Low stock products
        low_stock_products = Product.objects.filter(
            quantity__lte=models.F('low_threshold')
        )

        return Response({
            'total_products': Product.objects.count(),
            'total_logs': self.queryset.count(),
            'low_stock_products': ProductSerializer(low_stock_products, many=True).data
        })