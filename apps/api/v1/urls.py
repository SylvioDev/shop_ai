from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework_simplejwt.views import TokenRefreshView
from django.urls import path
from . import views

router = DefaultRouter()
router.register('products', views.ProductViewSet)
router.register('users', views.UserViewset)
router.register('me', views.UserProfileViewSet)
router.register('variants', views.ProductVariantViewSet)

urlpatterns = router.urls + [
    path('auth/register/', views.RegisterJSONView.as_view(), name='register_json'),
    path('auth/login/', TokenObtainPairView.as_view()),
    path('auth/token/refresh/', TokenRefreshView.as_view())
]