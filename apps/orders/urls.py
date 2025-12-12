from django.urls import path
from apps.orders.views import OrderListView
from apps.orders.views import OrderDetailView

urlpatterns = [
    path('order_list/', OrderListView.as_view(), name='orders'),
    path('order_detail/<str:order_number>', OrderDetailView.as_view(), name='order_detail')
]
