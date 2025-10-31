from django.urls import path
from . import views

urlpatterns = [
    path('', views.pending_table_orders, name='pending_table_orders'),
]
