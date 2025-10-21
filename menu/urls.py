from django.urls import path
from menu import views

urlpatterns = [
    path('menu/', views.menu_view, name='menu'),
]
