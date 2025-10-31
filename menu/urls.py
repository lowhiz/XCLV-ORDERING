from django.urls import path
from . import views


urlpatterns = [
    path('order/', views.create_order, name='create_order'),
    path('view/', views.view_menu, name='view_menu'),
    path('review/', views.order_review, name='order_review'),
]
