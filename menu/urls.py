from django.urls import path
from . import views


urlpatterns = [
    path('menu/order/', views.create_order, name='create_order'),
    path('view/', views.view_menu, name='view_menu'),
]
