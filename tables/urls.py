from django.urls import path
from . import views

urlpatterns = [
    path('', views.pending_table_orders, name='pending_table_orders'),
    path('overview/', views.table_overview, name='table_overview'),
    path('table-order/<int:table_order_id>/', views.table_order_data, name='table_order_data'),
    path('edit-order/<int:table_order_id>/', views.edit_order, name='edit_order'),
]
