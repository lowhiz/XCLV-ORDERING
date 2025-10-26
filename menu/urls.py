from django.urls import path
from . import views

app_name = 'menu'

urlpatterns = [
    path('menu/', views.menu_list, name='menu_list'),
    path('menu/order/', views.create_order, name='create_order'),
]
