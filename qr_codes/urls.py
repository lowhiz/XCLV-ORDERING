from django.urls import path
from qr_codes import views

urlpatterns = [
    path('order/', views.validation, name='order'),
]
