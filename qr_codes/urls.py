from django.urls import path
from . import views

urlpatterns = [
    path('order/', views.validation, name='order'),
    path('toggle-batch/', views.toggle_batch, name='toggle_batch'),
    path('order/validate-location/', views.validate_location_ajax, name='validate_location_ajax'),
    path('management/', views.qr_management, name='qr_management'),
]
