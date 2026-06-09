from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework_simplejwt.views import TokenRefreshView
from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularSwaggerView,
    SpectacularRedocView
)
from django.urls import path
from . import views

router = DefaultRouter()
router.register('productes', views.ProductViewSet)
router.register('users', views.UserViewset)
router.register('me', views.UserProfileViewSet)
router.register('variants', views.ProductVariantViewSet)
router.register('orders', views.OrderViewSet, basename='order')

urlpatterns = router.urls + [
    path('auth/register/', views.RegisterJSONView.as_view(), name='register'),
    path('auth/login/', TokenObtainPairView.as_view(), name='get-token'),
    path('auth/token/refresh/', TokenRefreshView.as_view()),
    path('cart/', views.CartView.as_view(), name='cart-api'),
    path('cart/clear/', views.CartClearView.as_view(), name='cart-clear'),
    path('schema/', SpectacularAPIView.as_view(), name='schema'),
    path('schema/swagger/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    path('schema/redoc/', SpectacularRedocView.as_view(url_name='schema'), name='redoc')
]