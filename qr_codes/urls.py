from django.urls import path
from . import views

urlpatterns = [
    path('order/', views.validation, name='order'),
    path('toggle-batch/', views.toggle_batch, name='toggle_batch'),
    path('order/validate-location/', views.validate_location_ajax, name='validate_location_ajax'),
    path('management/', views.qr_management, name='qr_management'),
    path('batch/<int:batch_id>/', views.qr_details, name='qr_details'),
    path('batch/<int:batch_id>/print/', views.print_qr_codes, name='print_qr_codes'),
]
