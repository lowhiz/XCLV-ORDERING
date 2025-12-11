from django.urls import path
from . import views
from orders import views as order_views  # Import orders views

urlpatterns = [
    path('', views.pending_table_orders, name='pending_table_orders'),
    path('overview/', views.table_overview, name='table_overview'),
    path('table-order/<int:table_order_id>/', views.table_order_data, name='table_order_data'),
    path('table/<int:table_id>/', views.table_description, name='table_description'),
    path('table-details/', views.table_details, name='table_details'),
    path('edit-order/<int:table_order_id>/', views.edit_order, name='edit_order'),
    path('delete-order/<int:table_order_id>/', order_views.delete_order, name='delete_order'),  # Add this
    path('complete-order/<int:table_order_id>/', order_views.complete_order, name='complete_order'),  # Add this
    path('tables/api-status/', views.table_status_api, name='table_status_api'),
    path('api/pending-orders/', views.pending_orders_api, name='pending_orders_api'),
]
