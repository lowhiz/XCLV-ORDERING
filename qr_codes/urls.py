from django.urls import path
from . import views

app_name = 'qr_codes'

urlpatterns = [
    # Main QR entry point - what customers scan
    path('order/', views.order_entry, name='order_entry'),

    # AJAX endpoint for location validation
    path('order/validate-location/', views.validate_location_ajax, name='validate_location_ajax'),

    # Legacy support
    path('validation/', views.validation, name='validation'),
]
