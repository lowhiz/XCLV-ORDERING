from django.urls import path
from . import views


urlpatterns = [
    path('order/', views.create_order, name='create_order'),
    path('order_details/<int:order_id>/', views.past_order_details, name='order_details'),
    path('order-success/', views.order_success, name='order_success'),
]
