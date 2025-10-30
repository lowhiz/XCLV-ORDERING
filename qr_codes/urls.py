from django.urls import path
from . import views

urlpatterns = [
    path('order/', views.validation, name='order'),
    path('order/validate-location/', views.validate_location_ajax, name='validate_location_ajax'),
]
