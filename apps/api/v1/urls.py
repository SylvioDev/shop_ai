from rest_framework.routers import DefaultRouter
from django.urls import path
from . import views

router = DefaultRouter()
router.register('products', views.ProductViewSet)

urlpatterns = router.urls + [
    path('register/', views.RegisterJSONView.as_view(), name='register_json')
]