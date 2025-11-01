from django.urls import path
from . import views


urlpatterns = [
    path('view/', views.view_menu, name='view_menu'),
    path('review/', views.order_review, name='order_review'),
    path('table-details/', views.table_details, name='table_details'),
]
