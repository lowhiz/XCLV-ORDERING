from django.urls import path
from . import views


urlpatterns = [
    path('menu/', views.menu_list, name='menu_list'),
    path('view/', views.menu_view, name='menu_view'),
    path('menu/order/', views.create_order, name='create_order'),
]
