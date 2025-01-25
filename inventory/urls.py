# urls.py
from django.contrib import admin
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
    TokenVerifyView
)
from inventory.views import (
    UserViewSet, UserCreateViewSet, ManagerViewSet, 
    ProductViewSet, StaffViewSet, InventoryLogViewSet
)

# Create router and register viewsets
router = DefaultRouter()
router.register(r'users', UserViewSet)
router.register(r'register', UserCreateViewSet)
router.register(r'managers', ManagerViewSet)
router.register(r'products', ProductViewSet)
router.register(r'staff', StaffViewSet)
router.register(r'inventory-logs', InventoryLogViewSet)

urlpatterns = [
    # Admin site
    path('admin/', admin.site.urls),
    
    # Authentication endpoints
    path('auth/login/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('auth/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('auth/verify/', TokenVerifyView.as_view(), name='token_verify'),
    
    # API endpoints
    path('', include(router.urls)),
]